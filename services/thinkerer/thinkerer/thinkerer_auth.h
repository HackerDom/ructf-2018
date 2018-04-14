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
using thinkerer::UserAuth;
using thinkerer::UserRegister;

typedef boost::shared_mutex Lock;
typedef boost::unique_lock< Lock > WriteLock;
typedef boost::shared_lock< Lock > ReadLock;

class ThinkererAuth {
public:
  ThinkererAuth(const std::string& authFile);
  ~ThinkererAuth();
  bool Register(const std::string username, const std::string& password);
  bool Check(const std::string username, const std::string& password);

private:
  void FlushData();

private:
  std::string AuthFile;
  UserAuth Auth;
  Lock Lock_;

};
