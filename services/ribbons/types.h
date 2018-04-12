#ifndef RIBBONS_TYPES_H
#define RIBBONS_TYPES_H

#include <stddef.h>
#include "constants.h"


#define ITERATE_POSTS(channel, post_var, action) struct Post *(post_var) = (channel)->posts; \
    while (post_var) { \
        action; \
        (post_var) = (post_var)->next; \
    }

struct Channel {
    int id;
    char name[NAME_SIZE];
    char password[PASSWORD_SIZE];
    char *key;
    struct Post *posts;
};

struct Post {
    char *text;
    size_t text_length;
    struct Post *next;
};


struct Channel *create_channel(int id, const char *name, const char *password, char* key);
struct Post *create_post(char *text, size_t text_length);
void append_post(struct Post **head, struct Post *post);
void delete_posts(struct Channel *channel);
void delete_channel(struct Channel* channel);

#endif //RIBBONS_TYPES_H
