#pragma once

#include <memory>
#include <string>
#include <mutex> 
#include <grpc++/grpc++.h>

#include "proto/thinkerer.pb.h"
#include "proto/thinkerer.grpc.pb.h"

using grpc::Channel;
using grpc::ClientContext;
using grpc::Status;
using thinkerer::Thinkerer;
using thinkerer::Msg;
using thinkerer::MsgReq;
using thinkerer::Msgs;
using thinkerer::MsgReply;


class ThinkererStor {
public:
  ThinkererStor(const std::string& dataDir);
  ~ThinkererStor();
  uint64_t AddMessage(const Msg& msg);
  std::vector<Msg> GetUserMessages(const std::string& uid, time_t startTs, time_t endTs);
  void FlushData(bool force = false);
  
private:
  time_t IntervalStartTime(time_t time) const;
  std::string Filename(time_t time) const;
  bool AcceptMessage(const Msg& msg, const std::string& uid, time_t startTs, time_t endTs) const;

private:
  std::string DataDir;
  std::vector<Msg> LastMessages;
  time_t TimestampMin = 0;
  time_t TimestampMax = 0;
  std::atomic_ullong LastId;
  std::mutex Lock;

};
