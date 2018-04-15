#include <iostream>
#include <memory>
#include <string>
#include <unordered_map>
#include <csignal>

#include <grpc++/grpc++.h>

#include "proto/thinkerer.pb.h"
#include "proto/thinkerer.grpc.pb.h"

#include "thinkerer_auth.h"
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

Server* CurrentServer = nullptr;

class MessangerImlp final : public Thinkerer::Service {
public:
  MessangerImlp()
    : Stor("data")
    , Auth("data/auth")
  {}

  Status SendMessage(ServerContext* context, const Msg* request,
                     MsgReply* reply) override 
  {
    Msg msg(*request);

    time_t now;
    time(&now);
    msg.set_ts(now);

    if (!Auth.Check(request->from(), request->password())) {
      reply->set_error("Bad username or password");
      return Status::OK;
    }

    Stor.AddMessage(msg);
    return Status::OK;
  }

  Status RecvMessages(ServerContext* context, const MsgReq* request,
                      Msgs* reply) override
  {
    if (!Auth.Check(request->uid(), request->password())) {
      reply->set_error("Bad username or password");
      return Status::OK;
    }

    time_t now;
    time(&now);

    time_t startTs = now - 20 * 60;
    time_t endTs = now;

    if (request->start_ts()) {
      startTs = request->start_ts();
    }

    if (request->end_ts()) {
      endTs = request->end_ts();
    }

    // const auto& userMessages = 
    for (const auto& msg : Stor.GetUserMessages(request->uid(), startTs, endTs)) {
      auto m = reply->add_messages();
      m->MergeFrom(msg);
    }

    return Status::OK;
  }

  Status Register(ServerContext* context, const UserRegister* request,
                      MsgReply* reply) override
  {
    if (Auth.Register(request->username(), request->password())) {
      reply->set_status(1);
    }

    return Status::OK;
  }


private:
  std::unordered_map<std::string, std::vector<Msg>> messages_;
  ThinkererStor Stor;
  ThinkererAuth Auth;

};

void RunServer() {
  std::string server_address("0.0.0.0:50051");
  MessangerImlp service;

  ServerBuilder builder;
  builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
  builder.RegisterService(&service);
  std::unique_ptr<Server> server(builder.BuildAndStart());
  std::cout << "Server listening on " << server_address << std::endl;

  CurrentServer = server.get();
  auto f = [](int signal) {
    std::cerr << "Server shutdown now!" << std::endl;
    if (CurrentServer) {
      CurrentServer->Shutdown();
    }
    std::cerr << "Server shutdown done!" << std::endl;
  };
  std::signal(SIGINT, f);
  std::signal(SIGTERM, f);
  

  server->Wait();
  CurrentServer = nullptr;
}

int main(int argc, char** argv) {
  RunServer();

  return 0;
}
