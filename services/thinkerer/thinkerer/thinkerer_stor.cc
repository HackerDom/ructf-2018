#include "thinkerer_stor.h"

#include <google/protobuf/message.h>
#include <google/protobuf/io/zero_copy_stream_impl.h>

#include <fstream>
#include <vector>
#include <time.h>

const int TIME_INTERVAL = 5 * 60; // 5 min

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

uint64_t ThinkererStor::AddMessage(const Msg& msg) {
  const auto newId = LastId++;
  std::lock_guard<std::mutex> guard(Lock);

  if (TimestampMin == 0) {
    TimestampMin = msg.ts();
  }

  if (TimestampMax == 0) {
    TimestampMax = msg.ts();
  }

  LastMessages.push_back(msg);
  FlushData();
  return newId;
}

time_t ThinkererStor::IntervalStartTime(time_t time) const {
  return (time / TIME_INTERVAL) * TIME_INTERVAL;
}

std::string ThinkererStor::Filename(time_t time) const {
  return DataDir + "/" + std::to_string(IntervalStartTime(time));
}

void ThinkererStor::FlushData(bool force) {
  time_t now;
  time(&now);

  std::cerr << "FlushData:" << force << " " << now << std::endl;
  auto nowIntervalStartTime = IntervalStartTime(now);
  auto currentIntervalStartTime = IntervalStartTime(TimestampMin);
  if (!force && (currentIntervalStartTime == nowIntervalStartTime)) {
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

    if (ts >= currentIntervalStartTime) {
      newMessages.emplace_back(msg);
      if (!force) {
        continue;
      }
    }

    if (!fileIntervalStartTime || (fileIntervalStartTime != myInterval)) {
      fileIntervalStartTime = myInterval;
      filename = Filename(currentIntervalStartTime);
      std::cerr << "filename:" << filename << std::endl;
      out.reset(new std::ofstream(filename, std::ios::binary));
      outStream.reset(new google::protobuf::io::OstreamOutputStream(out.get()));
    }

    writeDelimitedTo(msg, outStream.get());
  }

  LastMessages.swap(newMessages);
}

bool ThinkererStor::AcceptMessage(const Msg& msg, const std::string& uid, time_t startTs, time_t endTs) const {
  if (msg.to() != uid) {
    return false;
  }

  const auto ts = msg.ts();
  if (ts < startTs || ts > endTs) {
    return false;
  }

  return true;
}

std::vector<Msg> ThinkererStor::GetUserMessages(const std::string& uid, time_t startTs, time_t endTs) {
  std::lock_guard<std::mutex> guard(Lock);
  if (endTs <= startTs) {
    throw std::runtime_error("Bad ts interval");
  }

  if (endTs - startTs > 2 * TIME_INTERVAL) {
    throw std::runtime_error("Interval is too large");
  }

  const auto startInterval = IntervalStartTime(startTs);
  const auto endInterval = IntervalStartTime(endTs);

  std::vector<Msg> ret;

  if ((startTs >= TimestampMin && startTs <= TimestampMax) ||
      (endTs >= TimestampMin && endTs <= TimestampMax))
  {
    for (const auto& msg : LastMessages) {
      if (AcceptMessage(msg, uid, startTs, endTs)) {
        ret.emplace_back(msg);
      }
    }
  }

  for (auto currentInterval = startInterval; currentInterval <= endInterval; currentInterval += TIME_INTERVAL) {
    const auto filename = Filename(currentInterval);
    std::ifstream in(filename, std::ios::binary);
    if (!in.good()) {
      continue;
    }

    google::protobuf::io::IstreamInputStream inStream(&in);

    Msg msg;
    while (readDelimitedFrom(&inStream, &msg)) {
      if (AcceptMessage(msg, uid, startTs, endTs)) {
        ret.emplace_back(msg);
      }
    }
  }
  return ret;

}