#pragma once

#include <google/protobuf/message.h>
#include <google/protobuf/io/coded_stream.h>
#include <google/protobuf/io/zero_copy_stream_impl.h>
#include <google/protobuf/io/zero_copy_stream.h>


bool WriteDelimitedTo(const google::protobuf::MessageLite& message, 
                      google::protobuf::io::ZeroCopyOutputStream* rawOutput);

bool ReadDelimitedFrom(google::protobuf::io::ZeroCopyInputStream* rawInput,
                       google::protobuf::MessageLite* message);
