#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

long cCreateAndBind(int port, int backlog) {
	int sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd < 0) {
		perror("open socket");
		return -1;
	}

	int opt = 1;
	if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
		perror("setsockopt REUSEADDR");
		return -1;
	}

	struct sockaddr_in serv_addr;
	memset(&serv_addr, 0, sizeof(serv_addr));
	serv_addr.sin_family = AF_INET;
	serv_addr.sin_addr.s_addr = INADDR_ANY;
	serv_addr.sin_port = htons(port);

	if (bind(sockfd, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
		perror("bind");
		return -1;
	}

	if (listen(sockfd, backlog) < 0) {
		perror("listen");
		return -1;
	}

	return sockfd;
}

long cMakeSocketNonBlocking(int sockfd) {
	int flags = fcntl(sockfd, F_GETFL, 0);
	if (flags == -1) {
		perror("fcntl.get");
		return -1;
	}

	if (fcntl(sockfd, F_SETFL, flags | O_NONBLOCK) == -1) {
		perror("fcntl.set");
		return -1;
	}

	return 0;
}

long cAccept(int sockfd) {
	struct sockaddr in_addr;
	socklen_t in_len;
	int infd;

	in_len = sizeof(in_addr);
	infd = accept(sockfd, &in_addr, &in_len);
	if (infd >= 0)
		return infd;

	if (errno == EAGAIN || errno == EWOULDBLOCK)
		return -1;
	perror("accept");
	return -2;
}

long cClose(int fd) {
	int n = close(fd);
	if (n < 0) 
		perror("close");
	return n;
}

long cRead(int fd, char* buff, int size, int skip) {
	int readed;

	readed = read(fd, buff + skip, size - skip);
	if (readed >= 0)
		return readed;

	if (errno == EAGAIN || errno == EWOULDBLOCK)
		return -1;
	printf("socket %d buffer (%p, %d, %d): ", fd, buff, skip, size);
	fflush(stdout);
	perror("read");
	return -2;
}

long cWrite(int fd, char* buff, int size) {
	int sended;

	sended = write(fd, buff, size);
	if (sended >= 0)
		return sended;

	if (errno == EAGAIN || errno == EWOULDBLOCK)
		return -1;
	perror("write");
	return -2;
}
