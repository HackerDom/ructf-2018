#include <iostream>

#include "thinkerer_client.h"

#include <boost/program_options.hpp>
namespace po = boost::program_options;

int main(int argc, char** argv) {

  // Instantiate the client. It requires a channel, out of which the
  // actual RPCs are created. This channel models a connection to an
  // endpoint (in this case, localhost at port 50051). We indicate
  // that the channel isn't authenticated (use of
  // InsecureCredentials()).

  po::options_description desc("Allowed options");

  desc.add_options()
            ("help", "Helo message")
            ("send", "send message")
            ("recv", "recive messages")
            ("uid", po::value<std::string>(), "my uid")
            ("to", po::value<std::string>(), "send message to uid")
            ("message", po::value<std::string>(), "send message body")
            ("password"), po::value<std::string>(), "password")
            ("frwrd_id"), po::value<std::string>(), "forward message id")
        ;

  po::variables_map vm;
  po::store(po::parse_command_line(argc, argv, desc), vm);
  po::notify(vm); 

  if (vm.count("help")) {
    std::cout << desc << "\n";
    return 1;
  }

  ThinkererClient greeter(
      grpc::CreateChannel("localhost:50051", grpc::InsecureChannelCredentials()));

  if (vm.count("send")) {
    greeter.SendMessage(vm["uid"].as<std::string>(), vm["to"].as<std::string>(), vm["message"].as<std::string>());
    std::cerr << "Sent!" << std::endl;
  }

  if (vm.count("recv")) {
    const auto& uid = vm["uid"].as<std::string>();
    std::cerr << "Recv messages for " << uid << std::endl;
    const auto& msgs = greeter.RecvMessages(vm["uid"].as<std::string>());
    for (const auto& m : msgs) {
      std::cout << m.from() << "\t" << m.to() << "\t" << m.message() << std::endl;
    }
  }

  return 0;
}
