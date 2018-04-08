/*
 *
 * Copyright 2015, Google Inc.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 *
 *     * Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above
 * copyright notice, this list of conditions and the following disclaimer
 * in the documentation and/or other materials provided with the
 * distribution.
 *     * Neither the name of Google Inc. nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */

#include <iostream>

#include "greeter_client.h"

// Constructor with "initialization list"
GreeterClient::GreeterClient(std::shared_ptr<Channel> channel)
  : stub_(Greeter::NewStub(channel)) {}

void GreeterClient::SendMessage(const std::string& from, 
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

std::vector<Msg> GreeterClient::RecvMessages(const std::string& uid) {
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

std::string GreeterClient::SayHello(const std::string& user) {
  // Data we are sending to the server.
  HelloRequest request;
  request.set_name(user);

  // Container for the data we expect from the server.
  HelloReply reply;

  // Context for the client. It could be used to convey extra information to
  // the server and/or tweak certain RPC behaviors.
  ClientContext context;

  // The actual RPC.
  Status status = stub_->SayHello(&context, request, &reply);

  // Act upon its status.
  if (status.ok()) {
    return reply.message();
  } else {
    return "RPC failed";
  }
}
