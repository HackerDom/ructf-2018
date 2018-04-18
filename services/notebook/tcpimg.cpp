#include "tcpimg.h"
#include "tcpthread.h"

#include <stdlib.h>

TCPImgServer::TCPImgServer(int maxPos, QObject *parent)
    : QTcpServer(parent), maxPos(maxPos)
{
    const int MAX_THREAD_COUNT = 32;
    QThreadPool::globalInstance()->setMaxThreadCount(MAX_THREAD_COUNT);
}

void TCPImgServer::incomingConnection(qintptr socketDescriptor)
{
    TCPImgThread *thread = new TCPImgThread(socketDescriptor, maxPos, this);
    QThreadPool::globalInstance()->start(thread);
}
