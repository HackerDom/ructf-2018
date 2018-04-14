#include "thinkerer_stor.h"

#include <google/protobuf/message.h>
#include <google/protobuf/io/zero_copy_stream_impl.h>

#include <fstream>
#include <vector>
#include <time.h>

const int TIME_INTERVAL = 5 * 60; // 5 min
const int MAX_MESSAGES_IN_MEMORY = 1000;

bool writeDelimitedTo(
    const google::protobuf::MessageLite& message,
    google::protobuf::io::ZeroCopyOutputStream* rawOutput) {
  google::protobuf::io::CodedOutputStream output(rawOutput);

  // Write the size.
  const int size = message.ByteSize();
  output.WriteVarint32(size);

  uint8_t* buffer = output.GetDirectBufferForNBytesAndAdvance(size);
  if (buffer != NULL) {
    // Optimization:  The message fits in one buffer, so use the faster
    // direct-to-array serialization path.
    message.SerializeWithCachedSizesToArray(buffer);
  } else {
    // Slightly-slower path when the message is multiple buffers.
    message.SerializeWithCachedSizes(&output);
    if (output.HadError()) return false;
  }

  return true;
}

bool readDelimitedFrom(
    google::protobuf::io::ZeroCopyInputStream* rawInput,
    google::protobuf::MessageLite* message) {
  google::protobuf::io::CodedInputStream input(rawInput);

  // Read the size.
  uint32_t size;
  if (!input.ReadVarint32(&size)) return false;

  // Tell the stream not to read beyond that size.
  auto limit = input.PushLimit(size);

  // Parse the message.
  if (!message->MergePartialFromCodedStream(&input)) return false;
  if (!input.ConsumedEntireMessage()) return false;

  // Release the limit.
  input.PopLimit(limit);

  return true;
}


ThinkererStor::ThinkererStor(const std::string& dataDir) 
  : DataDir(dataDir)
  , LastId(0)
{ }

ThinkererStor::~ThinkererStor() {
  FlushData(/*force =*/ true);
}

void ThinkererStor::UpdateTs() {
  if (LastMessages.size()) {
    TimestampMin = LastMessages.front().ts();
    TimestampMax = LastMessages.back().ts();
  } else {
    TimestampMin = 0;
    TimestampMax = 0;
  }

}

std::string ThinkererStor::AddMessage(const Msg& msg) {
  WriteLock guard(Lock_);

  if (TimestampMin == 0) {
    TimestampMin = msg.ts();
  }

  if (TimestampMax == 0) {
    TimestampMax = msg.ts();
  }

  LastMessages.push_back(msg);

  auto id = LastMessages.back().id();
  if (id.empty()) {
    id = std::to_string(LastId++);
    LastMessages.back().set_id(id);
  }
  UpdateTs();

  FlushData();
  return id;
}

time_t ThinkererStor::IntervalStartTime(time_t time) const {
  return (time / TIME_INTERVAL) * TIME_INTERVAL;
}

std::string ThinkererStor::Filename(time_t time) const {
  return DataDir + "/" + std::to_string(IntervalStartTime(time));
}

bool ThinkererStor::GetMessageById(const std::string& id, time_t ts, Msg& msg) {
  // std::lock_guard<std::mutex> guard(Lock);
  std::cerr << "GetMessageById: " << TimestampMin << " " << ts << "  " << TimestampMax << std::endl;
  if ((ts >= TimestampMin && ts <= TimestampMax)) {
    for (const auto& m : LastMessages) {
      if (m.id() == id) {
        msg = m;
        std::cerr << "msg by id:" << id << " : " << msg.message() << std::endl;
        return true;
      }
    }
  }

  const auto filename = Filename(IntervalStartTime(ts));
  std::ifstream in(filename, std::ios::binary);
  if (!in.good()) {
    return false;
  }

  google::protobuf::io::IstreamInputStream inStream(&in);

  Msg m;
  while (readDelimitedFrom(&inStream, &m)) {
    if (m.id() == id) {
      msg = m;
      std::cerr << "msg by id:" << id << " : " << msg.message() << std::endl;
      return true;
    }
  }
  return false;
}

void ThinkererStor::FlushData(bool force) {
  time_t now;
  time(&now);

  if (LastMessages.size() > MAX_MESSAGES_IN_MEMORY) {
    force = true;
  }

  auto nowIntervalStartTime = IntervalStartTime(now);
  auto currentIntervalStartTime = IntervalStartTime(TimestampMin);
  std::cerr << "FlushData:" << force << " " << now << " " << nowIntervalStartTime << " " << currentIntervalStartTime << std::endl;
  if (!force && (currentIntervalStartTime == nowIntervalStartTime)) {
    std::cerr << "NoFlush" << std::endl;
    return;
  }

  std::string filename;
  std::unique_ptr<std::ofstream> out;
  std::unique_ptr<google::protobuf::io::OstreamOutputStream> outStream;
  time_t fileIntervalStartTime = 0;

  std::vector<Msg> newMessages;
  newMessages.reserve(LastMessages.size());
  for (const auto& msg : LastMessages) {
    const auto& ts = msg.ts();
    const auto& myInterval = IntervalStartTime(ts);

    if (!force && ts >= currentIntervalStartTime) {
      newMessages.push_back(msg);
      continue;
    }

    if (!fileIntervalStartTime || (fileIntervalStartTime != myInterval)) {
      fileIntervalStartTime = myInterval;
      filename = Filename(myInterval);
      std::cerr << "filename:" << filename << std::endl;

      outStream.reset();
      out.reset();

      out.reset(new std::ofstream(filename, std::ios::binary | std::ios_base::app));
      outStream.reset(new google::protobuf::io::OstreamOutputStream(out.get()));
      std::cerr << "msg write done" << std::endl;
    }

    writeDelimitedTo(msg, outStream.get());
    
  }
  std::cerr << "End write" << std::endl;

  LastMessages = newMessages;
  std::cerr << "SWAP messages" << std::endl;
  UpdateTs();
  std::cerr << "Flush DONE!" << std::endl;
}

bool ThinkererStor::AcceptMessage(const Msg& msg, const std::string& uid, time_t startTs, time_t endTs) const {
  if (msg.to() != uid && msg.from() != uid) {
    return false;
  }

  const auto ts = msg.ts();
  if (ts < startTs || ts > endTs) {
    return false;
  }

  return true;
}

std::vector<Msg> ThinkererStor::GetUserMessages(const std::string& uid, time_t startTs, time_t endTs) {
  ReadLock guard(Lock_);
  if (endTs <= startTs) {
    throw std::runtime_error("Bad ts interval");
  }

  if (endTs - startTs > 2 * TIME_INTERVAL) {
    throw std::runtime_error("Interval is too large");
  }

  const auto startInterval = IntervalStartTime(startTs);
  const auto endInterval = IntervalStartTime(endTs);

  std::vector<Msg> ret;

  std::cerr << "Intervals: " << startTs << " " << endTs << " "
            << TimestampMin << " " << TimestampMax << std::endl;
  if (true || (startTs >= TimestampMin && startTs <= TimestampMax) ||
      (endTs >= TimestampMin && endTs <= TimestampMax))
  {
    std::cerr << "!!!! In LastMessages" << std::endl;
    for (const auto& msg : LastMessages) {
      if (AcceptMessage(msg, uid, startTs, endTs)) {
        ret.push_back(msg);
        if (msg.has_msg_forward()) {
          Msg forwardedMsg;
          if (GetMessageById(msg.msg_forward().id(), msg.msg_forward().ts(), forwardedMsg)) {
            ret.push_back(forwardedMsg);
          }
        }
      }
    }
  }

  for (auto currentInterval = startInterval; currentInterval <= endInterval; currentInterval += TIME_INTERVAL) {
    const auto filename = Filename(currentInterval);
    std::cerr << "!!!!! In " << filename << std::endl;
    std::ifstream in(filename, std::ios::binary);
    if (!in.good()) {
      continue;
    }

    google::protobuf::io::IstreamInputStream inStream(&in);

    Msg msg;
    while (readDelimitedFrom(&inStream, &msg)) {
      if (AcceptMessage(msg, uid, startTs, endTs)) {
        ret.push_back(msg);
        if (msg.has_msg_forward()) {
          Msg forwardedMsg;
          if (GetMessageById(msg.msg_forward().id(), msg.msg_forward().ts(), forwardedMsg)) {
            ret.push_back(forwardedMsg);
          }
        }
      }
    }
  }
  return ret;
}
