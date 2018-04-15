#include <stdio.h>
#include <string.h>
#include <microhttpd.h>
#include <wait.h>
#include "frontend.h"
#include "httpserver.h"
#include "types.h"
#include "storage.h"
#include "routes.h"

#define ROUTES_COUNT 5

struct Route routes[ROUTES_COUNT];

int handle_add_channel(struct Request *request, struct Response *response, struct Channel **channel) {
    if (!strlen(request->name) || !strlen(request->password))
        return MHD_HTTP_BAD_REQUEST;

    *channel = add_channel(request->name, request->password);

    if (!*channel) 
        return MHD_HTTP_INTERNAL_SERVER_ERROR;

    response->buffer = malloc(16);
    if (!response->buffer){
        perror("malloc failed");
        return MHD_HTTP_INTERNAL_SERVER_ERROR;
    }
    sprintf(response->buffer, "id:%d", (*channel)->id);
    response->buffer_size = strlen(response->buffer);
    return MHD_HTTP_CREATED;
}

int handle_add_post(struct Request *request, struct Response *response, struct Channel **channel) {
    if (!strlen(request->text))
        return MHD_HTTP_BAD_REQUEST;

    char *text = malloc(strlen(request->text) + 1);
    if (!text){
        perror("malloc failed");
        return MHD_HTTP_INTERNAL_SERVER_ERROR;
    }

    strcpy(text, request->text);

    if (!add_post(*channel, text))
        return MHD_HTTP_INTERNAL_SERVER_ERROR;

    return MHD_HTTP_CREATED;
}

int handle_get_key(struct Request *request, struct Response *response, struct Channel **channel) {
    response->buffer = (*channel)->key;
    response->buffer_size = KEY_SIZE;
    return MHD_HTTP_OK;
}

int handle_change_password(struct Request *request, struct Response *response, struct Channel **channel) {
    if (!strlen(request->new_password))
        return MHD_HTTP_BAD_REQUEST;

    change_password(*channel, request->new_password);
    return MHD_HTTP_OK;
}

char *serialize_channel_data(struct Channel *channel, size_t *buffer_size) {
    char *buffer = NULL;
    FILE *f = open_memstream(&buffer, buffer_size);
    if (!f){
        perror("open_memstream failed");
        return NULL;
    }
    // FIXME Possible key address leak
    write_str(channel->name, strlen(channel->name), f);
    write_channel_posts(channel, f);
    fclose(f);
    return buffer;
}

int handle_view_channel(struct Request *request, struct Response *response, struct Channel **channel) {
    response->buffer = serialize_channel_data(*channel, &response->buffer_size);
    return response->buffer ? MHD_HTTP_OK : MHD_HTTP_INTERNAL_SERVER_ERROR;
}

void fill_route(struct Route *route, char *method, char *url, RouteHandler handler, unsigned int flags) {
    strcpy(route->method, method);
    strcpy(route->url, url);
    route->handler = handler;
    route->flags = flags;
}

void register_routes() {
    fill_route(&routes[0], "POST", "/api/add_channel", handle_add_channel, 0);
    fill_route(&routes[1], "POST", "/api/add_post", handle_add_post, ROUTE_CHANNEL_NEEDED | ROUTE_AUTH_NEEDED);
    fill_route(&routes[2], "POST", "/api/key", handle_get_key, ROUTE_CHANNEL_NEEDED | ROUTE_AUTH_NEEDED);
    fill_route(&routes[3], "POST", "/api/change_password", handle_change_password, ROUTE_CHANNEL_NEEDED | ROUTE_AUTH_NEEDED);
    fill_route(&routes[4], "GET", "/api/view", handle_view_channel, ROUTE_CHANNEL_NEEDED);
}

struct Route *find_route(const char *method, const char *url) {
    for (int i = 0; i < ROUTES_COUNT; i++) {
        if (strcmp(method, routes[i].method) == 0 && strcmp(url, routes[i].url) == 0) {
            return &routes[i];
        }
    }
    return 0;
}

int handle_route(struct Route *route, struct Request *request, struct Response *response, struct Channel **channel) {
    if (route->flags & ROUTE_CHANNEL_NEEDED){
        *channel = get_channel_by_id(request->channel_id);
        if (!*channel) {
            return MHD_HTTP_NOT_FOUND;
        }
        if (route->flags & ROUTE_AUTH_NEEDED) {
            if (!strlen(request->password)) {
                return MHD_HTTP_BAD_REQUEST;
            }
            if (!auth(*channel, request->password)) {
                return MHD_HTTP_FORBIDDEN;
            }
        }
    }

    return route->handler(request, response, channel);
}

int handle_request(struct Request *request, struct MHD_Response **mhd_response) {
    struct Route *route = find_route(request->method, request->url);
    if (!route){
        printf("Route handler not found for %s %s\n", request->method, request->url);
        return MHD_HTTP_NOT_FOUND;
    }

    int affected_channel_id;
    int status_code;
    struct Response response;
    memset(&response, 0, sizeof(struct Response));

    int pipefd[2];
    if (pipe(pipefd) == -1) {
        perror("pipe failed");
        return MHD_HTTP_INTERNAL_SERVER_ERROR;
    }

    pid_t pid = fork();

    if (pid == -1) {

        perror("fork failed");
        return MHD_HTTP_INTERNAL_SERVER_ERROR;

    } else if (pid == 0) {

        struct Channel *channel = NULL;

        status_code = handle_route(route, request, &response, &channel);

        affected_channel_id = channel ? channel->id : 0;
        write(pipefd[1], &affected_channel_id, sizeof(int));
        write(pipefd[1], &status_code, sizeof(int));
        write(pipefd[1], &response.buffer_size, sizeof(size_t));
        write(pipefd[1], response.buffer, response.buffer_size);
        exit(0);

    } else {

        close(pipefd[1]);

        wait(NULL);

        int read_failed = 0;

        if (read(pipefd[0], &affected_channel_id, sizeof(int)) != sizeof(int) ||
            read(pipefd[0], &status_code, sizeof(int)) != sizeof(int) ||
            read(pipefd[0], &response.buffer_size, sizeof(size_t)) != sizeof(size_t)) {

            read_failed = 1;

        } else {
            response.buffer = calloc(response.buffer_size, 1);

            if (!response.buffer) {
                perror("calloc failed");
                read_failed = 1;
            }

            if (response.buffer && read(pipefd[0], response.buffer, response.buffer_size) != response.buffer_size){
                free(response.buffer);
                read_failed = 1;
            }
        }

        close(pipefd[0]);

        if (read_failed)
            return MHD_HTTP_INTERNAL_SERVER_ERROR;

        if (affected_channel_id)
            update_channel(affected_channel_id);

        *mhd_response = MHD_create_response_from_buffer(response.buffer_size, response.buffer, MHD_RESPMEM_MUST_FREE);

        return status_code;
    }

}