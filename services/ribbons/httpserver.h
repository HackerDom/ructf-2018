#include <stdlib.h>
#include <stdint.h>
#include "types.h"

#ifndef RIBBONS_HTTPSERVER_H
#define RIBBONS_HTTPSERVER_H

#define POSTBUFFERSIZE 512

struct Request {
    const char *method;
    const char *url;
    int channel_id;
    char name[20];
    char password[20];
    char new_password[20];
    char text[1000];
};

struct Response {
    char *buffer;
    size_t buffer_size;
};

void run_server(uint16_t port);

#endif //RIBBONS_HTTPSERVER_H
