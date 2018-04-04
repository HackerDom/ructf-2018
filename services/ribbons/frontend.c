#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>
#include <syscall.h>
#include "constants.h"
#include "types.h"
#include "storage.h"
#include "cache.h"


struct Channel *get_channel_by_id(int id) {
    struct Channel *channel = cache_find(id);
    if (!channel) {
        channel = load_channel(id);
        if (!channel)
            return 0;
        cache_add(channel);
    }
    return channel;
}

int auth(struct Channel *channel, char *password) {
    return strcmp(channel->password, password) == 0;
}

char *generate_key() {
    char *key = malloc(KEY_SIZE);
    if (syscall(SYS_getrandom,key, KEY_SIZE, 0) != KEY_SIZE) {
        return 0;
    }
    return key;
}

int add_channel(char *name, char *password) {
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
    return channel->id;
}

int add_post(struct Channel *channel, char *text) {
    struct Post *post = create_post(text);
    if (!post) {
        return 0;
    }
    append_post(&channel->posts, post);
    save_channel(channel);
    return 1;
}

void change_password(struct Channel *channel, char *new_password) {
    memcpy(channel->password, new_password, strlen(new_password));
    save_channel(channel);
}

void update_channel(int channel_id) {
    cache_update(channel_id, load_channel(channel_id));
}