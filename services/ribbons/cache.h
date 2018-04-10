#ifndef RIBBONS_CACHE_H
#define RIBBONS_CACHE_H

void cache_add(struct Channel *channel);
struct Channel *cache_find(int channel_id);
void cache_update(int channel_id, struct Channel *channel);

#endif //RIBBONS_CACHE_H
