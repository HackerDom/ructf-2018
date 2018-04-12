#include <iostream>

#include "thinkerer_client.h"

enum ESTATUS {
  OK = 101,
  CORRUPT = 102,
  MUMBLE = 103,
  DOWN = 104,
  CHECKER_ERROR = 110
};

const auto PORT = "50051";

void put(ThinkererClient& client, const std::string& id, const std::string& flag) {
  client.SendMessage("CHANGE_ME", id, flag);
  exit(ESTATUS::OK);
}

void get(ThinkererClient& client, const std::string& id, const std::string& flag) {
    std::cerr << "Recv messages for " << id << std::endl;
    const auto& msgs = client.RecvMessages(id);
    bool found = false;
    for (const auto& m : msgs) {
      found = found || m.message() == flag;
      std::cerr << m.from() << "\t" << m.to() << "\t" << m.message() << "\tflag found:" << found << std::endl;
    }

    if (found) {
      exit(ESTATUS::OK);
    }

    exit(ESTATUS::CORRUPT);
}

int main(int argc, char** argv) {
  if (argc < 5) {
    std::cerr << "Should be at least 4 parametes" << std::endl;
    exit(1);
  }

  std::string command = argv[1];
  std::string host = argv[2];
  std::string id = argv[3];
  std::string flag = argv[4];

  if (command == "check") {
    exit(ESTATUS::OK);
  }

  std::cerr << "RUN:" << command << ' ' << host << ' ' << id << std::endl;

  ThinkererClient client(
      grpc::CreateChannel(host + ':' + PORT, grpc::InsecureChannelCredentials()));

  if (command == "put") {
    put(client, id, flag);
  }

  if (command == "get") {
    get(client, id, flag);
  }

  exit(ESTATUS::CHECKER_ERROR);

  return 0;
}
