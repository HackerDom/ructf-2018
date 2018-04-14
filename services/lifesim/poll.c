#include <stdio.h>
#include <sys/epoll.h>

long cGetEpoll() {
	int epoll = epoll_create1(0);
	if (epoll < 0) {
		perror("epoll_create1");
		return -1;
	}

	return epoll;
}

long cAddReadConnect(int epollfd, int fd) {
	struct epoll_event event;

	event.data.fd = fd;
	event.events = EPOLLIN | EPOLLET;
	if (epoll_ctl(epollfd, EPOLL_CTL_ADD, fd, &event) < 0) {
		perror("epoll_ctl.add.read");
		return -1;
	}
	return 0;
}

long cRemoveReadConnect(int epollfd, int fd) {
	struct epoll_event event;
	
	event.data.fd = fd;
	event.events = EPOLLIN;
	if (epoll_ctl(epollfd, EPOLL_CTL_DEL, fd, &event) < 0) {
		perror("epoll_ctl.del.read");
		return -1;
	}
	return 0;
}

long cAddWriteConnect(int epollfd, int fd) {
	struct epoll_event event;
	
	event.data.fd = fd;
	event.events = EPOLLOUT | EPOLLET;
	if (epoll_ctl(epollfd, EPOLL_CTL_ADD, fd, &event) < 0) {
		perror("epoll_ctl.add.write");
		return -1;
	}
	return 0;
}

long cRemoveWriteConnect(int epollfd, int fd) {
	struct epoll_event event;
	
	event.data.fd = fd;
	event.events = EPOLLOUT;
	if (epoll_ctl(epollfd, EPOLL_CTL_DEL, fd, &event) < 0) {
		perror("epoll_ctl.del.write");
		return -1;
	}
	return 0;
}

long cGetConnect(int epollfd) {
	int n;
	struct epoll_event event;

	n = epoll_wait(epollfd, &event, 1, 1);
	if (n == 0)
		return 0;

	if ((event.events & EPOLLERR) || (event.events & EPOLLHUP))
		return -event.data.fd;

	return event.data.fd;
}
