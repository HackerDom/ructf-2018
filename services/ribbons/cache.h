#ifndef NEWS_CACHE_H
#define NEWS_CACHE_H

void cache_add(struct Channel *channel);
struct Channel *cache_find(int channel_id);

#endif //NEWS_CACHE_H
