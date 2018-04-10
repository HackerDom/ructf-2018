#include <stdlib.h>

#ifndef RIBBONS_CRYPTO_H
#define RIBBONS_CRYPTO_H

char *generate_key();
char *encrypt(char *data, size_t data_size, const char *key);

#endif //RIBBONS_CRYPTO_H
