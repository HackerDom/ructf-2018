#include <whitedb/dbapi.h>
#include <whitedb/indexapi.h>
#include <string.h>
#include <stdio.h>

void* dbCredentials;
void* dbData;

const char WAIT = 1;
const char OK = 0;
const char ERROR = -1;
const char NOTFOUND = -2;
const char NOTEQUALS = -3;

long cInitDB(char* credentialsName, long credentialsSize, char* dataName, long dataSize) {
	dbCredentials = wg_attach_database(credentialsName, credentialsSize);
	dbData = wg_attach_database(dataName, dataSize);
	if (dbCredentials == NULL || dbData == NULL)
		return ERROR;
	return OK;
}

char checkCredentials(char* name, char* password) {
	void* rec;
	char* p;
	
	rec = wg_find_record_str(dbCredentials, 0, WG_COND_EQUAL, name, NULL);
	if (rec == NULL)
		return NOTFOUND;

	p = wg_decode_str(dbCredentials, wg_get_field(dbCredentials, rec, 1));
	if (strcmp(password, p))
		return NOTEQUALS;
	else
		return OK;
}

long cAddCredentials(char* name, char* password) {
	wg_int lock;
	void* rec;
	char checkResult;

	lock = wg_start_write(dbCredentials);
	if (!lock)
		return WAIT;

	checkResult = checkCredentials(name, password);
	if (checkResult != NOTFOUND) {
		wg_end_write(dbCredentials, lock);
		return checkResult;
	}

	rec = wg_create_record(dbCredentials, 2);
	if (rec != NULL) {
		if (wg_set_str_field(dbCredentials, rec, 0, name) >= 0 && wg_set_str_field(dbCredentials, rec, 1, password) >= 0) {
			wg_end_write(dbCredentials, lock);
			return OK;
		}
	}

	wg_end_write(dbCredentials, lock);
	return ERROR;
}

long cCheckCredentials(char* name, char* password) {
	wg_int lock;
	char checkResult;
	lock = wg_start_read(dbCredentials);
	if (!lock)
		return WAIT;

	checkResult = checkCredentials(name, password);

	wg_end_read(dbCredentials, lock);
	if (checkResult == OK)
		return OK;
	else
		return NOTFOUND;
}

long cWriteData(char* name, char* data) {
	wg_int lock;
	void* rec;

	lock = wg_start_write(dbData);
	if (!lock)
		return WAIT;

	rec = wg_create_record(dbData, 2);
	if (rec != NULL) {
		if (wg_set_str_field(dbData, rec, 0, name) >= 0 && wg_set_str_field(dbData, rec, 1, data) >= 0) {
			wg_end_write(dbData, lock);
			return OK;
		}
	}

	wg_end_write(dbData, lock);
	return ERROR;
}

long cGetNextData(char* name, char* data, long* dataLength, long* current) {
	wg_int lock;
	void* rec;
	char* p;
	long plen;

	lock = wg_start_read(dbData);
	if (!lock)
		return WAIT;

	rec = wg_find_record_str(dbData, 0, WG_COND_EQUAL, name, (void*)*current);
	if (rec == NULL) {
		wg_end_read(dbData, lock);
		return NOTFOUND;
	}

	p = wg_decode_str(dbData, wg_get_field(dbData, rec, 1));
	wg_end_read(dbData, lock);

	plen = strlen(p);
	strncpy(data, p, *dataLength);
	if (plen < *dataLength)
		*dataLength = plen;
	*current = (long)rec;

	return OK;
}

long cGetNextUser(char* data, long* dataLength, long* current) {
	wg_int lock;
	void* rec;
	char* p;
	long plen;

	lock = wg_start_read(dbCredentials);
	if (!lock)
		return WAIT;

	rec = *current == 0 
		? wg_get_first_record(dbCredentials) 
		: wg_get_next_record(dbCredentials, (void*)*current);
	if (rec == NULL) {
		wg_end_read(dbCredentials, lock);
		return NOTFOUND;
	}

	p = wg_decode_str(dbCredentials, wg_get_field(dbCredentials, rec, 0));
	wg_end_read(dbCredentials, lock);

	plen = strlen(p);
	strncpy(data, p, *dataLength);
	if (plen < *dataLength)
		*dataLength = plen;
	*current = (long)rec;

	return OK;
}
