package(default_visibility = ["//visibility:public"])

# cc_binary(
#     name = "client",
#     linkstatic = 1,
#     srcs = ["thinkerer_client_main.cc"],
#     deps = [":clientlib", "@boost//:program_options"],
# )

cc_binary(
    name = "server",
    linkstatic = 1,
    srcs = ["thinkerer_server.cc"],
    deps = ["//proto:cpp", ":messagestor", ":auth"],
)

cc_library(
    name = "messagestor",
    srcs = ["thinkerer_stor.cc"],
    hdrs = ["thinkerer_stor.h"],
    deps = ["//proto:cpp", "@boost//:thread", ":proto_utils"],
)

cc_library(
    name = "auth",
    srcs = ["thinkerer_auth.cc"],
    hdrs = ["thinkerer_auth.h"],
    deps = ["//proto:cpp", "@boost//:thread", ":proto_utils"],
)

cc_library(
    name = "proto_utils",
    srcs = ["proto_utils.cc"],
    hdrs = ["proto_utils.h"],
    deps = ["//proto:cpp"],
)
