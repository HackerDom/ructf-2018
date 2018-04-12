#include <string.h>
#include <stdlib.h>
#include "constants.h"
#include "types.h"
#include "storage.h"

struct Channel *channels_cache[CHANNELS_CACHE_SIZE] = {0};
int tail_index = 0;

void cache_add(struct Channel *channel) {
    if (channels_cache[tail_index]) {
        delete_channel(channels_cache[tail_index]);
    }
    channels_cache[tail_index] = channel;
    tail_index = (tail_index + 1) % CHANNELS_CACHE_SIZE;
}

int find_index(int channel_id) {
    for (int i = 0; i < CHANNELS_CACHE_SIZE; i++) {
        if (channels_cache[i] && channels_cache[i]->id == channel_id) {
            return i;
        }
    }
    return -1;
}

struct Channel *cache_find(int channel_id) {
    int index = find_index(channel_id);
    return index != -1 ? channels_cache[index] : 0;
}

void cache_update(int channel_id, struct Channel *channel) {
    int index = find_index(channel_id);
    if (index != -1) {
        struct Channel *old_channel = channels_cache[index];
        free(old_channel->key);
        delete_posts(old_channel);
        memcpy(channels_cache[index], channel, sizeof(struct Channel));
        free(channel);
    } else {
        cache_add(channel);
    }
}