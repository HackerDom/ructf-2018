package(default_visibility = ["//visibility:public"])


load("@org_pubref_rules_protobuf//cpp:rules.bzl", "cc_proto_library")
#load("@org_pubref_rules_protobuf//csharp:rules.bzl", "csharp_proto_library")
#load("@org_pubref_rules_protobuf//go:rules.bzl", "go_proto_library")
#load("@org_pubref_rules_protobuf//gogo:rules.bzl", "gogo_proto_library")
load("@org_pubref_rules_protobuf//java:rules.bzl", "java_proto_library")
#load("@org_pubref_rules_protobuf//node:rules.bzl", "node_proto_library")
load("@org_pubref_rules_protobuf//objc:rules.bzl", "objc_proto_compile")
load("@org_pubref_rules_protobuf//protobuf:rules.bzl", "proto_compile")
load("@org_pubref_rules_protobuf//python:rules.bzl", "py_proto_library")
load("@org_pubref_rules_protobuf//ruby:rules.bzl", "ruby_proto_compile")

filegroup(
    name = "protos",
    srcs = ["thinkerer.proto"],
)

cc_proto_library(
    name = "cpp",
#    proto_deps = [
#        "//examples/proto:cpp",
#    ],
    protos = [":protos"],
    verbose = 0,
    with_grpc = True,
)

#csharp_proto_library(
#    name = "Helloworld",
#    proto_deps = [
#        "//examples/proto:csharp",
#    ],
#    protos = [":protos"],
#    verbose = 0,
#    with_grpc = True,
#)

#go_proto_library(
#    name = "go",
#    proto_deps = [
#        "//examples/proto:go_default_library",
#    ],
#    protos = [":protos"],
#    verbose = 0,
#    with_grpc = True,
#)

#java_proto_library(
#    name = "java",
#    proto_deps = [
#        "//examples/proto:java",
#    ],
#    protos = [":protos"],
#    verbose = 0,
#    with_grpc = True,
#)

# Commented out as this conflicts with go (same output file).
#
# gogo_proto_library(
#     name = "gogo",
#     proto_deps = [
#         "//examples/proto:go_default_library",
#     ],
#     protos = [":protos"],
#     verbose = 1,
#     with_grpc = True,
# )

#node_proto_library(
#    name = "node",
#    proto_deps = [
#        "//examples/proto:node",
#    ],
#    protos = [":protos"],
#    verbose = 0,
#    with_grpc = True,
#)

objc_proto_compile(
    name = "objc",
    protos = [":protos"],
    with_grpc = True,
    deps = [
        "//examples/proto:objc",
    ],
)

py_proto_library(
    name = "py",
    #proto_deps = [
    #    "//examples/proto:py",
    #],
    protos = [
        ":protos",
    ],
    with_grpc = True,
)

#ruby_proto_compile(
#    name = "ruby",
#    protos = [":protos"],
#    with_grpc = True,
#    deps = [
#        "//examples/proto:ruby",
#    ],
#)
