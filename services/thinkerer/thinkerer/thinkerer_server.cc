#include <iostream>
#include <memory>
#include <string>
#include <unordered_map>

#include <grpc++/grpc++.h>

#include "proto/thinkerer.pb.h"
#include "proto/thinkerer.grpc.pb.h"
#include "thinkerer_stor.h"

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
public:
  MessangerImlp()
    : Stor("data")
  {}

  Status SendMessage(ServerContext* context, const Msg* request,
                     MsgReply* reply) override 
  {
    messages_[request->to()].push_back(*request);

    time_t now;
    time(&now);
    messages_[request->to()].back().set_ts(now);
    Stor.AddMessage(messages_[request->to()].back());
    Stor.FlushData(true);
    return Status::OK;
  }

  Status RecvMessages(ServerContext* context, const MsgReq* request,
                      Msgs* reply) override
  {
    time_t now;
    time(&now);

    time_t startTs = now - 5 * 60;
    time_t endTs = now;

    if (request->start_ts()) {
      startTs = request->start_ts();
    }

    if (request->end_ts()) {
      endTs = request->end_ts();
    }

    for (const auto& msg : Stor.GetUserMessages(request->uid(), startTs, endTs)) {
      std::cerr << msg.message() << std::endl;
      auto m = reply->add_messages();
      m->MergeFrom(msg);
    }

    return Status::OK;
  }
private:
  std::unordered_map<std::string, std::vector<Msg>> messages_;
  ThinkererStor Stor;

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
