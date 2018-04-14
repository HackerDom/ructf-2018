#include "picohttpparser.h"
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

const char* authHeader = "Authorization";
const size_t authHeaderLength = 13;

const char* contentLengthHeader = "Content-length";
const size_t contentLengthHeaderLength = 14;

size_t min(size_t a, size_t b) {
	return a < b ? a : b;
}

char getHeader(const char* header, const size_t headerLength, const struct phr_header h, char * outHeader, long* outLength) {
	if (headerLength != h.name_len)
		return 0;
	if (!strncasecmp(header, h.name, headerLength)) {
		if ((long)h.value_len > *outLength)
			return -1;
		memcpy(outHeader, h.value, h.value_len);
		*outLength = h.value_len;
		return 1;
	}
	return 0;
}

long cTryParse(char* buff, int len, char* method, long* methodLength, char* path, long* pathLength, char* auth, long* authLength, long* contentLength) {
	const size_t max_num_headers = 100;
	const long contentLengthMaxLength = 10;
	const char *m, *p;
	int pret, minor_version;
	struct phr_header headers[max_num_headers];
	size_t method_len, path_len, num_headers = max_num_headers, i;
	char hasAuth, parseResult;
	long contentLengthLength = contentLengthMaxLength;
	char contentLengthBuffer[contentLengthMaxLength + 1];

	pret = phr_parse_request(buff, len, &m, &method_len, &p, &path_len, &minor_version, headers, &num_headers, 0);

	if (pret < 0)
		return pret;	

	if ((long)method_len > *methodLength)
		return -1;

	if ((long)path_len > *pathLength)
		return -1;

	memcpy(method, m, method_len);
	*methodLength = method_len;

	memcpy(path, p, path_len);
	*pathLength = path_len;

	hasAuth = 0;
	*contentLength = -1;
	for (i = 0; i < num_headers; ++i) {

		parseResult = getHeader(authHeader, authHeaderLength, headers[i], auth, authLength);
		if (parseResult < 0)
			return -1;
		if (parseResult > 0)
			hasAuth = 1;

		parseResult = getHeader(contentLengthHeader, contentLengthHeaderLength, headers[i], contentLengthBuffer, &contentLengthLength);
		if (parseResult < 0)
			return -1;
		if (parseResult > 0) {
			contentLengthBuffer[contentLengthLength] = 0;
			*contentLength = strtol(contentLengthBuffer, NULL, 10);
		}
	}

	if (!hasAuth)
			*authLength = 0;

	return pret;
}
