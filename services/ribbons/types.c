#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "constants.h"
#include "types.h"

struct Channel *create_channel(int id, const char *name, const char *password, char *key) {
    struct Channel *channel = calloc(sizeof(struct Channel), 1);
    if (!channel) {
        perror("calloc failed");
        return NULL;
    }
    channel->id = id;
    strncpy(channel->name, name, NAME_SIZE);
    strncpy(channel->password, password, PASSWORD_SIZE);
    channel->key = key;
    return channel;
}

struct Post *create_post(char *text, size_t text_length) {
    struct Post *post = calloc(sizeof(struct Post), 1);
    if (!post) {
        perror("calloc failed");
        return NULL;
    }
    post->text = text;
    post->text_length = text_length;
    return post;
}

void append_post(struct Post **head, struct Post *post){
    if (!*head){
        *head = post;
        return;
    }
    struct Post *current = *head;
    while (current->next) {
        current = current->next;
    }
    current->next = post;
}

void delete_posts(struct Channel *channel) {
    ITERATE_POSTS(channel, post, free(post));
}

void delete_channel(struct Channel* channel){
    free(channel->key);
    delete_posts(channel);
    free(channel);
}