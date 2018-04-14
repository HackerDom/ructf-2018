#pragma once

#include <memory>
#include <string>
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


class ThinkererClient {
 public:
  ThinkererClient(std::shared_ptr<Channel> channel);
  void SendMessage(const std::string& from, const std::string& to,
                   const std::string& message,
                   const std::string& forwardMsgId = "",
                   const time_t forwardMsgTs = 0);

  std::vector<Msg> RecvMessages(const std::string& uid);

 private:
  std::unique_ptr<Thinkerer::Stub> stub_;
};
