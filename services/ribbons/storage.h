#ifndef NEWS_STORAGE_H
#define NEWS_STORAGE_H

int next_channel_id();
struct Channel *load_channel(int channel_id);
void save_channel(struct Channel *channel);

#endif //NEWS_STORAGE_H
