package(default_visibility = ["//visibility:public"])

cc_binary(
    name = "client",
    linkstatic = 1,
    srcs = ["thinkerer_client_main.cc"],
    deps = [":clientlib", "@boost//:program_options"],
)

cc_binary(
    name = "server",
    linkstatic = 1,
    srcs = ["thinkerer_server.cc"],
    deps = ["//proto:cpp", ":messagestor"],
)

cc_library(
    name = "clientlib",
    srcs = ["thinkerer_client.cc"],
    hdrs = ["thinkerer_client.h"],
    deps = ["//proto:cpp"],
)

cc_library(
    name = "messagestor",
    srcs = ["thinkerer_stor.cc"],
    hdrs = ["thinkerer_stor.h"],
    deps = ["//proto:cpp"],
)
