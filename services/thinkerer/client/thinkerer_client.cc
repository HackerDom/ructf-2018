#include <iostream>

#include "thinkerer_client.h"

ThinkererClient::ThinkererClient(std::shared_ptr<Channel> channel)
  : stub_(Thinkerer::NewStub(channel)) {}

void ThinkererClient::SendMessage(const std::string& from, 
                                  const std::string& password,
                                  const std::string& to,
                                  const std::string& message,
                                  const std::string& id,
                                  const std::string& forwardMsgId,
                                  const time_t forwardMsgTs) 
{
  Msg msg;
  msg.set_from(from);
  msg.set_to(to);

  if (!message.empty()) {
    msg.set_message(message);
  }
  msg.set_password(password);

  if (!id.empty()) {
    msg.set_id(id);
  }

  if (!forwardMsgId.empty()) {
    auto forwardMsg = msg.mutable_msg_forward();
    forwardMsg->set_id(forwardMsgId);
    forwardMsg->set_ts(forwardMsgTs);
  }

  MsgReply reply;
  ClientContext context;
  Status status = stub_->SendMessage(&context, msg, &reply);
  if (!status.ok()) {
    throw std::runtime_error("Bad wire status");
  }
}

std::vector<Msg> ThinkererClient::RecvMessages(const std::string& uid, const std::string& password) {
  std::vector<Msg> ret;
  MsgReq req;
  req.set_uid(uid);
  req.set_password(password);

  Msgs reply;
  ClientContext context;
  Status status = stub_->RecvMessages(&context, req, &reply);
  if (!status.ok()) {
    throw std::runtime_error("Bad wire status");
  }

  if (!reply.error().empty()) {
    throw std::runtime_error(reply.error());
  }

  for (const auto& m : reply.messages()) {
    ret.push_back(m);
  }
  return ret;
}

bool ThinkererClient::Register(const std::string& username, const std::string& password) {
  UserRegister req;
  MsgReply reply;
  ClientContext context;

  req.set_username(username);
  req.set_password(password);

  Status status = stub_->Register(&context, req, &reply);
  if (!status.ok()) {
    throw std::runtime_error("Bad wire status");
  }
  return true;
}