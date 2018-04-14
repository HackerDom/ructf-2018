#pragma once

#include <memory>
#include <string>
#include <mutex> 
#include <grpc++/grpc++.h>

#include <boost/thread/locks.hpp>
#include <boost/thread/shared_mutex.hpp>

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

typedef boost::shared_mutex Lock;
typedef boost::unique_lock< Lock > WriteLock;
typedef boost::shared_lock< Lock > ReadLock;

class ThinkererStor {
public:
  ThinkererStor(const std::string& dataDir);
  ~ThinkererStor();
  std::string AddMessage(const Msg& msg);
  std::vector<Msg> GetUserMessages(const std::string& uid, time_t startTs, time_t endTs);
  bool GetMessageById(const std::string& id, time_t ts, Msg& msg);
  void FlushData(bool force = false);
  
private:
  time_t IntervalStartTime(time_t time) const;
  std::string Filename(time_t time) const;
  bool AcceptMessage(const Msg& msg, const std::string& uid, time_t startTs, time_t endTs) const;
  void UpdateTs();

private:
  std::string DataDir;
  std::vector<Msg> LastMessages;
  time_t TimestampMin = 0;
  time_t TimestampMax = 0;
  std::atomic_ullong LastId;
  Lock Lock_;

};
