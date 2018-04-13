#include <iostream>
#include <memory>
#include <string>
#include <unordered_map>

#include <grpc++/grpc++.h>

#include "proto/thinkerer.pb.h"
#include "proto/thinkerer.grpc.pb.h"

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;
using thinkerer::Msg;
using thinkerer::MsgReq;
using thinkerer::Msgs;
using thinkerer::MsgReply;
using thinkerer::Thinkerer;

class MessangerImlp final : public Thinkerer::Service {
  Status SendMessage(ServerContext* context, const Msg* request,
                     MsgReply* reply) override 
  {
    messages_[request->to()].push_back(*request);
    return Status::OK;
  }

  Status RecvMessages(ServerContext* context, const MsgReq* request,
                      Msgs* reply) override
  {
    std::cerr << "RecvMessages!" << std::endl;
    const auto messages_it = messages_.find(request->uid());
    if (messages_it == messages_.end()) {
      std::cerr << "RecvMessages:" << request->uid() << " 0 messages" << std::endl; 
      return Status::OK;
    }

    std::cerr << "RecvMessages:" << request->uid() << "  " << messages_it->second.size() << " messages" << std::endl;
    for (const auto& message : messages_it->second) {
      auto m = reply->add_messages();
      m->MergeFrom(message);
    }
    return Status::OK;
  }
private:
  std::unordered_map<std::string, std::vector<Msg>> messages_;
};

void RunServer() {
  std::string server_address("0.0.0.0:50051");
  MessangerImlp service;

  ServerBuilder builder;
  // Listen on the given address without any authentication mechanism.
  builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
  // Register "service" as the instance through which we'll communicate with
  // clients. In this case it corresponds to an *synchronous* service.
  builder.RegisterService(&service);
  // Finally assemble the server.
  std::unique_ptr<Server> server(builder.BuildAndStart());
  std::cout << "Server listening on " << server_address << std::endl;

  // Wait for the server to shutdown. Note that some other thread must be
  // responsible for shutting down the server for this call to ever return.
  server->Wait();
}

int main(int argc, char** argv) {
  RunServer();

  return 0;
}
