#include "thinkerer_auth.h"
#include "proto_utils.h"

#include <fstream>
#include <vector>
#include <time.h>

#include <google/protobuf/message.h>
#include <google/protobuf/io/coded_stream.h>
#include <google/protobuf/io/zero_copy_stream_impl.h>
#include <google/protobuf/io/zero_copy_stream.h>


ThinkererAuth::ThinkererAuth(const std::string& authFile) 
  : AuthFile(authFile)
{
  std::ifstream in(authFile, std::ios::binary);
  if (!in.good()) {
    return;
  }

  google::protobuf::io::IstreamInputStream inStream(&in);
  ReadDelimitedFrom(&inStream, &Auth);
}

ThinkererAuth::~ThinkererAuth() {
  FlushData();
}

bool ThinkererAuth::Register(const std::string username, const std::string& password) {
  WriteLock guard(Lock_);

  auto users = Auth.mutable_user_password();
  (*users)[username] = password;
  FlushData();
  return true;
}

bool ThinkererAuth::Check(const std::string username, const std::string& password) {
  ReadLock guard(Lock_);

  const auto& users = Auth.user_password();
  auto userIt = users.find(username);
  if (userIt == users.end()) {
    return false;
  }

  return (userIt->second == password);
}

void ThinkererAuth::FlushData() {
  std::ofstream out(AuthFile, std::ios::binary);
  google::protobuf::io::OstreamOutputStream outStream(&out);

  WriteDelimitedTo(Auth, &outStream);
  out.flush();
}