#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include "constants.h"
#include "types.h"

int last_channel_id = -1;

void write_str(char *str, size_t length, FILE *file) {
    fwrite(&length, sizeof(size_t), 1, file);
    fwrite(str, sizeof(char), length, file);
}

char *read_str(size_t *length, FILE *file) {
    *length = 0;

    if (fread(length, sizeof(size_t), 1, file) != 1)
        return 0;

    char *result = calloc(*length+1, sizeof(char));
    if (!result){
        perror("calloc failed");
        return 0;
    }

    fread(result, sizeof(char), *length, file);
    return result;
}

void write_post(struct Post *post, FILE *file) {
    write_str(post->text, post->text_length, file);
}

struct Post *read_post(FILE *file) {
    size_t text_length;
    char *text = read_str(&text_length, file);
    return text ? create_post(text, text_length) : 0;
}

FILE *open_channel_file(int channel_id, char *mode) {
    char filename[255];
    sprintf(filename, "%s/%d", FOLDER, channel_id);
    FILE *file = fopen(filename, mode);
    if (!file)
        printf("Can't open file for channel %d\n", channel_id);
    return file;
}

struct Channel *read_channel(FILE *file, int channel_id) {
    char name[NAME_SIZE];
    char password[PASSWORD_SIZE];
    char *key = malloc(KEY_SIZE);

    if (!key) {
        perror("malloc failed");
        return 0;
    }

    if (fread(name, sizeof(char), NAME_SIZE, file) != NAME_SIZE ||
        fread(password, sizeof(char), PASSWORD_SIZE, file) != PASSWORD_SIZE ||
        fread(key, sizeof(char), KEY_SIZE, file) != KEY_SIZE) {

        free(key);
        return 0;
    }

    struct Channel *channel = create_channel(channel_id, name, password, key);
    if (!channel) {
        free(key);
        return 0;
    }

    while (!feof(file)) {
        struct Post *post = read_post(file);
        if (!post)
            break;
        append_post(&channel->posts, post);
    }
    return channel;
}

struct Channel *load_channel(int channel_id) {
    FILE * f = open_channel_file(channel_id, "rb");
    if (f == NULL) 
        return 0;
    struct Channel *channel = read_channel(f, channel_id);
    if (!channel) {
        fprintf(stderr, "Channel %d reading failed", channel_id);
    }
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

void write_channel_posts(struct Channel *channel, FILE *file) {
    ITERATE_POSTS(channel, post, write_post(post, file))
}

void save_channel(struct Channel *channel) {
    // prevents crash while writing to file
    validate_channel(channel);

    FILE * f = open_channel_file(channel->id, "wb");
    if (f == NULL)
        return;
    fwrite(channel->name, sizeof(char), NAME_SIZE, f);
    fwrite(channel->password, sizeof(char), PASSWORD_SIZE, f);
    fwrite(channel->key, sizeof(char), KEY_SIZE, f);
    write_channel_posts(channel, f);
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
