#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "frontend.h"
#include "types.h"

void input_string(char *prompt, char *buffer, int buf_size){
    printf(prompt);
    fgets(buffer, buf_size, stdin);
    buffer[strlen(buffer)-1] = '\0';
}

int input_number(char *prompt){
    printf(prompt);
    char num[10];
    fgets(num, 10, stdin);
    return atoi(num);
}

void menu() {
    puts("\nChoose action:\n");
    puts("(1) Add channel\n"
           "(2) Add post\n"
           "(3) Get channel key\n"
           "(4) Change channel password\n"
           "(5) View channel posts\n");
    int choice;
    char name[NAME_SIZE+1];
    char password[PASSWORD_SIZE+1];
    char new_password[PASSWORD_SIZE+6];
    char text_buffer[1000];
    int id;
    struct Channel *channel;

    choice = input_number(">");

    if (choice < 1 || choice > 5)
        return;

    if (choice != 1) {
        id = input_number("Enter channel id:");
        channel = get_channel_by_id(id);
        if (!channel) {
            puts("No such channel");
            return;
        }
        if (choice != 5) {
            input_string("Enter channel password:", password, 21);
            if (!auth(channel, password)) {
                puts("Password incorrect");
                return;
            }
        }
    }

    switch (choice) {
        case 1:
            input_string("Enter channel name:", name, sizeof(name));
            input_string("Enter channel password:", password, sizeof(password));
            id = add_channel(name, password);
            if (id)
                printf("# Created (id: %d)\n", id);
            else
                puts("# Failed");
            break;

        case 2:
            input_string("Enter text:", text_buffer, 1000);
            char *text = malloc(strlen(text_buffer));
            strcpy(text, text_buffer);
            if (add_post(channel, text))
                puts("# Created");
            else
                puts("# Failed");
            break;

        case 3:
            if (channel->key)
                puts(channel->key);
            else
                puts("# Failed");
            break;


        case 4:
            input_string("Enter new channel password:", new_password, sizeof(new_password));
            change_password(channel, new_password);
            puts("# Changed");
            break;

        case 5:
            printf("# Channel '%s' posts:\n", channel->name);
            struct Post *current = channel->posts;
            while (current) {
                puts("---");
                puts(current->text);
                puts("---");
                current = current->next;
            }
            puts("# End");
            break;
    }
}

int main() {
    while (1) {
        menu();
    }
    return 0;
}