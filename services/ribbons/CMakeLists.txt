cmake_minimum_required(VERSION 3.5)
project(ribbons)

set(CMAKE_C_STANDARD 99)

set(SOURCE_FILES main.c storage.c types.c constants.h types.h storage.h cache.c cache.h frontend.c frontend.h crypto.c crypto.h httpserver.c httpserver.h cli.c cli.h routes.c routes.h)
add_executable(ribbons ${SOURCE_FILES})
target_link_libraries(ribbons "/usr/lib/x86_64-linux-gnu/libmicrohttpd.so")