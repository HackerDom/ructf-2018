#include "proto_utils.h"

#include <string>
#include <iostream>

ProtoWriter::ProtoWriter(const std::string& filename)
    : Out(filename, std::ios::binary)
    , Adaptor(&Out)
    , Encoder(&Adaptor)
{}

void ProtoWriter::Write(const google::protobuf::Message& message) {
    const auto size = message.ByteSize();
    Buf.resize(size);
    message.serializeToArray(Buf[0], Buf.size());
    Encoder.WriteVarInt32(size);
    Encoder.WriteRaw(Buf[0], Buf.size());
}
