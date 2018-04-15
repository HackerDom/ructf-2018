#include <iostream>
#include <functional>
#include "client/thinkerer_client.h"

enum ESTATUS {
  OK = 101,
  CORRUPT = 102,
  MUMBLE = 103,
  DOWN = 104,
  CHECKER_ERROR = 110
};

const auto PORT = "50051";
const std::string SALT = "sv46kmfdjCCu7Dsjn00jsSx@343e2356Jhgvds";
const std::string SALT_B = "f44tsgsdfvsfvsldfgm43gwejrngkj456hertg";

std::string getPassword(const std::string& id) {
  return std::to_string(std::hash<std::string>()(id + SALT));
}

std::string randomString(size_t length) {
  auto randchar = []() -> char
  {
      const char charset[] =
      "0123456789"
      //"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
      "abcdefghijklmnopqrstuvwxyz";
      const size_t max_index = (sizeof(charset) - 1);
      return charset[ rand() % max_index ];
  };
  std::string str(length,0);
  std::generate_n( str.begin(), length, randchar );
  return str;
}

void put(ThinkererClient& client, const std::string& id, const std::string& flag, const size_t vuln) {
  const auto usernameFrom = randomString(4);
  const auto passFrom = getPassword(usernameFrom);
  std::string msgId;
  if (vuln == 2) {
    msgId = randomString(10);
  }

  client.Register(usernameFrom, passFrom);
  client.Register(id, getPassword(id));
  client.SendMessage(usernameFrom, passFrom, id, flag, msgId);
  exit(ESTATUS::OK);
}

void get(ThinkererClient& client, const std::string& id, const std::string& flag) {
    std::cerr << "Recv messages for " << id << std::endl;
    const auto& msgs = client.RecvMessages(id, getPassword(id));
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
  auto message = randomString(10);
  const auto& from = randomString(5);
  const auto& to = randomString(5);
  const auto& forwardTo = randomString(5);

  std::cerr << "message:" << message << " from:" << from << " to:" << to << " forwardTo:" << forwardTo << std::endl;

  client.Register(from, getPassword(from));
  client.Register(to, getPassword(to));
  client.Register(forwardTo, getPassword(forwardTo));

  client.SendMessage(from, getPassword(from), to, message, "");
  auto msgs = client.RecvMessages(from, getPassword(from));
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
    exit(ESTATUS::MUMBLE);
  }

  client.SendMessage(to, getPassword(to), forwardTo, "", "", msgId, msgTs);

  std::cerr << "[get forwarded message]" << std::endl;
  msgs = client.RecvMessages(forwardTo, getPassword(forwardTo));
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
  if (argc < 1) {
    std::cerr << "Should be at least 1 parametes" << std::endl;
    exit(1);
  }

  std::string command = argv[1];

  if (command == "info") {
    std::cout << "vulns: 1:1" << std::endl;
    exit(101);
  }

  if (argc < 2) {
    std::cerr << "Should be at least 2 parametes" << std::endl;
    exit(1);
  }


  std::string host = argv[2];
  std::string id;
  std::string flag;

  if (command != "check") {
    id = argv[3];
    flag = argv[4];
  }

  if (command == "info") {
    std::cout << "vulns: 1:1" << std::endl;
    exit(101);
  }

  std::cerr << "RUN:" << command << ' ' << host << ' ' << id << std::endl;

  ThinkererClient client(
      grpc::CreateChannel(host + ':' + PORT, grpc::InsecureChannelCredentials()));

  try {
    if (command == "check") {
      check(client);
    }

    if (command == "put") {
      uint vuln = 1;
      if (argc > 6) {
        vuln = std::stoi(argv[5]);
      }
      put(client, id, flag, vuln);
    }

    if (command == "get") {
      get(client, id, flag);
    }
  } catch (std::exception& e) {
    std::cerr << "Host:" << host << " exception: " << e.what() << std::endl;
    std::string exc = e.what();
    if (exc.find("Bad username or password") != std::string::npos) {
      exit(ESTATUS::MUMBLE);
    }
    exit(ESTATUS::DOWN);
  }

  exit(ESTATUS::CHECKER_ERROR);

  return 0;
}
