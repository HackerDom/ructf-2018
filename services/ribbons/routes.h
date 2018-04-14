#ifndef RIBBONS_ROUTES_H
#define RIBBONS_ROUTES_H

#define ROUTE_CHANNEL_NEEDED 1
#define ROUTE_AUTH_NEEDED 2

typedef int (*RouteHandler) (struct Request *request, struct Response *response, struct Channel **channel);

struct Route {
    char method[10];
    char url[30];
    RouteHandler handler;
    unsigned int flags;
};

void register_routes();
int handle_request(struct Request *request, struct MHD_Response **mhd_response);

#endif //RIBBONS_ROUTES_H
