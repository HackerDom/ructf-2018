#include "cim.h"
#include <string.h>

long cGetArgv(long x, char* buff, long* bufflen) {
	long reslen;
	char** argv;
	char* res;

	if (__rargc() < x || x < 0)
	{
		bufflen = 0;
		return 1;
	}

	argv = (char **)__rargv();
	res = argv[x];
	strncpy(buff, res, *bufflen);
	reslen = strlen(res);
	if (reslen < *bufflen)
		*bufflen = reslen;

	return 0;
}
