#include <stdlib.h>

#ifndef NEWS_CRYPTO_H
#define NEWS_CRYPTO_H

char *generate_key();
char *encrypt(char *data, size_t data_size, const char *key);

#endif //NEWS_CRYPTO_H
