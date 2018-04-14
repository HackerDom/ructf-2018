#pragma once

#include <string>
#include <iostream>

#include <google/protobuf/message.h>


class ProtoWriter {
private:
    ProtoWriter(const std::string& filename);
    void Write(const google::protobuf::Message& message);

private:
    std::ofstream Out;
    ::google::protobuf::io::TCopyingOutputStreamAdaptor Adaptor;
    ::google::protobuf::io::CodedOutputStream Encoder;
    std::vector<char> Buf;
};
