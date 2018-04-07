#ifndef GREETER_CLIENT_H
#define GREETER_CLIENT_H

#include <memory>
#include <string>
#include <grpc++/grpc++.h>

#include "helloworld/proto/helloworld.pb.h"
#include "helloworld/proto/helloworld.grpc.pb.h"

using grpc::Channel;
using grpc::ClientContext;
using grpc::Status;
using helloworld::HelloRequest;
using helloworld::HelloReply;
using helloworld::Greeter;
using helloworld::Msg;
using helloworld::MsgReq;
using helloworld::Msgs;
using helloworld::MsgReply;


class GreeterClient {
 public:
  GreeterClient(std::shared_ptr<Channel> channel);
  // Assambles the client's payload, sends it and presents the
  // response back from the server.
  std::string SayHello(const std::string& user);
  void SendMessage(const std::string& from, const std::string& to, const std::string& message);
  std::vector<Msg> RecvMessages(const std::string& uid);

 private:
  std::unique_ptr<Greeter::Stub> stub_;
};

#endif
