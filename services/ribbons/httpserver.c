#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <pthread.h>
#include <microhttpd.h>
#include "httpserver.h"
#include "routes.h"

int iterate_get(void *request, enum MHD_ValueKind kind, const char *key, const char *value) {
    if (strcmp(key, "channel_id") == 0) {
        ((struct Request *)request)->channel_id = (int) strtol(value, NULL, 10);
    }
}

int iterate_post (void *req, enum MHD_ValueKind kind, const char *key,
                  const char *filename, const char *content_type,
                  const char *transfer_encoding, const char *data,
                  uint64_t off, size_t size) {
    struct Request *request = req;
    if (strcmp(key, "name") == 0)
        strncpy(request->name, data, sizeof(request->name));
    if (strcmp(key, "password") == 0)
        strncpy(request->password, data, sizeof(request->password));
    if (strcmp(key, "new_password") == 0)
        strncpy(request->new_password, data, sizeof(request->new_password));
    if (strcmp(key, "text") == 0)
        strncpy(request->text, data, sizeof(request->text));
}

struct MHD_Response *empty_response;

struct Request request;
struct MHD_PostProcessor *postProcessor;

static int request_callback(
        void *param,
        struct MHD_Connection *connection,
        const char *url,
        const char *method,
        const char *version,
        const char *upload_data,
        size_t *upload_data_size,
        void **context)
{
    if (!*context) {
        // Headers received

        memset(&request, 0, sizeof(struct Request));
        postProcessor = NULL;
        *context = &request;
        return MHD_YES;
    }

    if (*upload_data_size != 0) {
        // Body received

        postProcessor = MHD_create_post_processor(
                connection, POSTBUFFERSIZE, iterate_post, &request);
        MHD_post_process(postProcessor, upload_data, *upload_data_size);

        *upload_data_size = 0;
        return MHD_YES;
    }

    MHD_get_connection_values(connection, MHD_GET_ARGUMENT_KIND, iterate_get, &request);

    struct MHD_Response *mhd_response = NULL;
    
    request.method = method;
    request.url = url;

    int status_code = handle_request(&request, &mhd_response);
    printf("%s %s %s %d\n", method, url, version, status_code);

    int ret = MHD_queue_response (connection, (unsigned int) status_code, mhd_response ? mhd_response : empty_response);
    if (mhd_response)
        MHD_destroy_response (mhd_response);
    if (postProcessor){
        MHD_destroy_post_processor(postProcessor);
    }
    return ret;
}


void run_server(uint16_t port) {
    register_routes();

    empty_response = MHD_create_response_from_buffer(0, 0, MHD_RESPMEM_PERSISTENT);

    struct MHD_Daemon *d;
    d = MHD_start_daemon (MHD_USE_EPOLL_INTERNAL_THREAD | MHD_USE_DEBUG | MHD_USE_ERROR_LOG,
                          port,
                          NULL, NULL, &request_callback, NULL,
                          MHD_OPTION_CONNECTION_TIMEOUT, (unsigned int) CONNECTION_TIMEOUT,
                          MHD_OPTION_END);
    if (d == NULL)
        return;
    pause();
    MHD_stop_daemon (d);
}