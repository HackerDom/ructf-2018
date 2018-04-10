#include <stdio.h>

#ifndef RIBBONS_STORAGE_H
#define RIBBONS_STORAGE_H

int next_channel_id();
struct Channel *load_channel(int channel_id);
void save_channel(struct Channel *channel);

void write_str(char *str, size_t length, FILE *file);
void write_channel_posts(struct Channel *channel, FILE *file);

#endif //RIBBONS_STORAGE_H
