#ifndef NEWS_FRONTEND_H
#define NEWS_FRONTEND_H

struct Channel *get_channel_by_id(int id);
int auth(struct Channel *channel, char *password);

int add_channel(char *name, char *password);
int add_post(struct Channel *channel, char *text);
void change_password(struct Channel *channel, char *new_password);

#endif //NEWS_FRONTEND_H
