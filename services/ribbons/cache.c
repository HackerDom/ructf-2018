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

struct Channel *cache_find(int channel_id) {
    for (int i = 0; i < CHANNELS_CACHE_SIZE; i++) {
        if (channels_cache[i] && channels_cache[i]->id == channel_id) {
            return channels_cache[i];
        }
    }
    return 0;
}
