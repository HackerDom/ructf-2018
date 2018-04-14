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

std::string randomString(size_t length) {
  auto randchar = []() -> char
  {
      const char charset[] =
      "0123456789"
      "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
      "abcdefghijklmnopqrstuvwxyz";
      const size_t max_index = (sizeof(charset) - 1);
      return charset[ rand() % max_index ];
  };
  std::string str(length,0);
  std::generate_n( str.begin(), length, randchar );
  return str;
}

void put(ThinkererClient& client, const std::string& id, const std::string& flag) {
  client.SendMessage(randomString(15), id, flag);
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

void check(ThinkererClient& client) {
  const auto& message = randomString(10);
  const auto& from = randomString(5);
  const auto& to = randomString(5);
  const auto& forwardTo = randomString(5);

  std::cerr << "message:" << message << " from:" << from << " to:" << to << " forwardTo:" << forwardTo << std::endl;

  client.SendMessage(from, to, message);
  auto msgs = client.RecvMessages(from);
  std::string msgId;
  time_t msgTs;
  std::cerr << "[getID]" << std::endl;
  for (const auto& m : msgs) {
    std::cerr << m.id() << "\t" << m.from() << "\t" << m.to() << "\t" << m.message() << "\t" << m.ts() << std::endl;
    if (m.message() == message) {
      msgId = m.id();
      msgTs = m.ts();
      std::cerr << "Found: " << msgId << " " << msgTs << std::endl;
      break;
    }
  }

  if (msgId.empty()) {
    exit(ESTATUS::CORRUPT);
  }

  client.SendMessage(to, forwardTo, randomString(12), msgId, msgTs);

  std::cerr << "[get forwarded message]" << std::endl;
  msgs = client.RecvMessages(forwardTo);
  for (const auto& m : msgs) {
    std::cerr << m.id() << "\t" << m.from() << "\t" << m.to() << "\t" << m.message() << std::endl;
    if (m.message() == message) {
      exit(ESTATUS::OK);
    }
  }
  exit(ESTATUS::CORRUPT);
}

int main(int argc, char** argv) {
  srand(time(NULL));
  if (argc < 2) {
    std::cerr << "Should be at least 2 parametes" << std::endl;
    exit(1);
  }

  std::string command = argv[1];
  std::string host = argv[2];
  std::string id;
  std::string flag;

  if (command != "check") {
    id = argv[3];
    flag = argv[4];
  }

  std::cerr << "RUN:" << command << ' ' << host << ' ' << id << std::endl;

  ThinkererClient client(
      grpc::CreateChannel(host + ':' + PORT, grpc::InsecureChannelCredentials()));

  try {
    if (command == "check") {
      check(client);
    }

    if (command == "put") {
      put(client, id, flag);
    }

    if (command == "get") {
      get(client, id, flag);
    }
  } catch (std::exception& e) {
    std::cerr << "Host:" << host << " exception: " << e.what() << std::endl;
    exit(ESTATUS::MUMBLE);
  }

  exit(ESTATUS::CHECKER_ERROR);

  return 0;
}
