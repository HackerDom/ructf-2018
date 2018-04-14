#include <unistd.h>
#include <syscall.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "constants.h"

char *generate_key() {
    char *key = malloc(KEY_SIZE);
    if (syscall(SYS_getrandom,key, KEY_SIZE, 0) != KEY_SIZE) {
        free(key);
        perror("getrandom failed");
        return 0;
    }
    return key;
}

char *encrypt(char *data, size_t data_size, const char *key) {
    for (int i = 0; i < data_size; i++) {
        data[i] ^= key[i % KEY_SIZE];
    }
    return data;
}
