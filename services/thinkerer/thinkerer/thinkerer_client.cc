#include <iostream>

#include "thinkerer_client.h"

// Constructor with "initialization list"
ThinkererClient::ThinkererClient(std::shared_ptr<Channel> channel)
  : stub_(Thinkerer::NewStub(channel)) {}

void ThinkererClient::SendMessage(const std::string& from, 
                                const std::string& to,
                                const std::string& message) 
{
  Msg msg;
  msg.set_from(from);
  msg.set_to(to);
  msg.set_message(message);

  MsgReply reply;
  ClientContext context;
  Status status = stub_->SendMessage(&context, msg, &reply);
}

std::vector<Msg> ThinkererClient::RecvMessages(const std::string& uid) {
  std::vector<Msg> ret;
  MsgReq req;
  req.set_uid(uid);

  Msgs reply;
  ClientContext context;
  Status status = stub_->RecvMessages(&context, req, &reply);

  if (!status.ok()) {
    return ret;
  }

  for (const auto& m : reply.messages()) {
    ret.push_back(m);
  }
  return ret;
}
