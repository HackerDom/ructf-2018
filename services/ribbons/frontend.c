#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/types.h>
#include "constants.h"
#include "types.h"
#include "storage.h"
#include "cache.h"
#include "crypto.h"


struct Channel *get_channel_by_id(int id) {
    struct Channel *channel = cache_find(id);
    if (!channel) {
        channel = load_channel(id);
        if (!channel){
            printf("Channel %d not found\n", id);
            return 0;
        }
        cache_add(channel);
    }
    return channel;
}

int auth(struct Channel *channel, char *password) {
    return strncmp(channel->password, password, PASSWORD_SIZE) == 0;
}

struct Channel *add_channel(char *name, char *password) {
    char *key = generate_key();
    if (key == 0) {
        return 0;
    }
    struct Channel *channel = create_channel(next_channel_id(), name, password, key);
    if (!channel) {
        return 0;
    }
    save_channel(channel);
    cache_add(channel);
    return channel;
}

int add_post(struct Channel *channel, char *text) {
    size_t text_length = strlen(text);
    struct Post *post = create_post(encrypt(text, text_length, channel->key), text_length);
    if (!post) {
        return 0;
    }
    append_post(&channel->posts, post);
    save_channel(channel);
    return 1;
}

void change_password(struct Channel *channel, char *new_password) {
    memset(channel->password, 0, sizeof(channel->password));
    memcpy(channel->password, new_password, strlen(new_password));
    save_channel(channel);
}

void update_channel(int channel_id) {
    cache_update(channel_id, load_channel(channel_id));
}