package(default_visibility = ["//visibility:public"])

cc_binary(
    name = "checker",
    linkstatic = 1,
    srcs = ["thinkerer_checker_main.cc"],
    deps = [":clientlib"],
)

cc_library(
    name = "clientlib",
    srcs = ["thinkerer_client.cc"],
    hdrs = ["thinkerer_client.h"],
    deps = ["//proto:cpp"],
)
