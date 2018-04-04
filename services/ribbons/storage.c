#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include "constants.h"
#include "types.h"

int last_channel_id = -1;

void write_str(char *str, FILE *file) {
    size_t len = strlen(str);
    fwrite(&len, sizeof(size_t), 1, file);
    fwrite(str, sizeof(char), len, file);
}

char *read_str(FILE *file) {
    size_t len;

    if (fread(&len, sizeof(size_t), 1, file) != 1)
        return 0;

    char *result = calloc(len+1, sizeof(char));
    if (!result)
        return 0;

    fread(result, sizeof(char), len, file);
    return result;
}

void write_post(struct Post *post, FILE *file) {
    write_str(post->text, file);
}

struct Post *read_post(FILE *file) {
    char *text = read_str(file);
    return text ? create_post(text) : 0;
}

FILE *open_channel_file(int channel_id, char *mode) {
    char filename[255];
    sprintf(filename, "%s/%d", FOLDER, channel_id);
    return fopen(filename, mode);
}

struct Channel *read_channel(FILE *file, int channel_id) {
    char name[NAME_SIZE];
    char password[NAME_SIZE];
    char *key;

    if (fread(name, sizeof(char), NAME_SIZE, file) != NAME_SIZE ||
        fread(password, sizeof(char), PASSWORD_SIZE, file) != PASSWORD_SIZE)
        return 0;

    key = read_str(file);
    if (!key)
        return 0;

    struct Channel *channel = create_channel(channel_id, name, password, key);

    while (!feof(file)) {
        append_post(&channel->posts, read_post(file));
    }
    return channel;
}

struct Channel *load_channel(int channel_id) {
    FILE * f = open_channel_file(channel_id, "rb");
    if (f == NULL)
        return 0;
    struct Channel *channel = read_channel(f, channel_id);
    fclose(f);
    return channel;
}

int validate_channel(struct Channel *channel){
    if (!channel->key)
        return 0;
    int result = 0;
    for (int i = 0; i < KEY_SIZE; i++)
        result &= channel->key[i];
    return result;
}

void save_channel(struct Channel *channel) {
    // prevents crash while writing to file
    validate_channel(channel);

    FILE * f = open_channel_file(channel->id, "wb");
    if (f == NULL)
        return;
    fwrite(channel->name, sizeof(char), NAME_SIZE, f);
    fwrite(channel->password, sizeof(char), PASSWORD_SIZE, f);
    write_str(channel->key, f);
    struct Post *post = channel->posts;
    while (post) {
        write_post(post, f);
        post = post->next;
    }
    fclose(f);
}

FILE *open_last_id_file(char *mode) {
    char filename[255];
    sprintf(filename, "%s/last_id", FOLDER);
    return fopen(filename, mode);
}

void load_last_id() {
    last_channel_id = 0;
    FILE *f = open_last_id_file("rb");
    if (f == NULL)
        return;
    if (fread(&last_channel_id, sizeof(int), 1, f) != 1)
        last_channel_id = 0;
    fclose(f);
}

void save_last_id() {
    FILE *f = open_last_id_file("wb");
    if (f == NULL)
        return;
    fwrite(&last_channel_id, sizeof(int), 1, f);
    fclose(f);
}

int next_channel_id() {
    if (last_channel_id < 0) {
        load_last_id();
    }
    last_channel_id++;
    save_last_id();
    return last_channel_id;
}
