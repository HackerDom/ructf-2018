#include "thinkerer_stor.h"
#include "proto_utils.h"

#include <google/protobuf/message.h>
#include <google/protobuf/io/zero_copy_stream_impl.h>

#include <fstream>
#include <vector>
#include <time.h>

const int TIME_INTERVAL = 5 * 60; // 5 min
const int MAX_MESSAGES_IN_MEMORY = 1000;


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
  if ((ts >= TimestampMin && ts <= TimestampMax)) {
    for (const auto& m : LastMessages) {
      if (m.id() == id) {
        msg.MergeFrom(m);
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
  while (ReadDelimitedFrom(&inStream, &m)) {
    if (m.id() == id) {
      msg.MergeFrom(m);
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

  if (!force) {
    return;
  }

  std::string filename;
  std::unique_ptr<std::ofstream> out;
  std::unique_ptr<google::protobuf::io::OstreamOutputStream> outStream;
  time_t fileIntervalStartTime = 0;

  for (const auto& msg : LastMessages) {
    const auto& ts = msg.ts();
    const auto& myInterval = IntervalStartTime(ts);

    if (!fileIntervalStartTime || (fileIntervalStartTime != myInterval)) {
      fileIntervalStartTime = myInterval;
      filename = Filename(myInterval);

      outStream.reset();
      out.reset();

      out.reset(new std::ofstream(filename, std::ios::binary | std::ios_base::app));
      outStream.reset(new google::protobuf::io::OstreamOutputStream(out.get()));

      if (!out->good()) {
        std::cerr << filename << "bad FD!" << std::endl;
      }
    }

    WriteDelimitedTo(msg, outStream.get());
  }

  LastMessages.clear();
  UpdateTs();
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

  if (endTs - startTs > 5 * TIME_INTERVAL) {
    throw std::runtime_error("Interval is too large");
  }

  const auto startInterval = IntervalStartTime(startTs);
  const auto endInterval = IntervalStartTime(endTs);

  std::vector<Msg> ret;

  if (true || (startTs >= TimestampMin && startTs <= TimestampMax) ||
      (endTs >= TimestampMin && endTs <= TimestampMax))
  {
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
    std::ifstream in(filename, std::ios::binary);
    if (!in.good()) {
      continue;
    }

    google::protobuf::io::IstreamInputStream inStream(&in);

    Msg msg;
    while (ReadDelimitedFrom(&inStream, &msg)) {
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
