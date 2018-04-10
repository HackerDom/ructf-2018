package(default_visibility = ["//visibility:public"])

cc_test(
    name = "test",
    size = "small",
    srcs = ["greeter_client_test.cc"],
    copts = ["-Iexternal/gtest/include"],
    tags = ["exclusive"],
    deps = [
        ":clientlib",
        "@com_google_googletest//:gtest",
    ],
)

cc_binary(
    name = "client",
    linkstatic = 1,
    srcs = ["greeter_client_main.cc"],
    deps = [":clientlib", "@boost//:program_options"],
)

cc_binary(
    name = "server",
    linkstatic = 1,
    srcs = ["greeter_server.cc"],
    deps = ["//helloworld/proto:cpp"],
)

cc_library(
    name = "clientlib",
    srcs = ["greeter_client.cc"],
    hdrs = ["greeter_client.h"],
    deps = ["//helloworld/proto:cpp"],
)
