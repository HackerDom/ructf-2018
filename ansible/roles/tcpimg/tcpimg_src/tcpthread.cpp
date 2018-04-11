#include "tcpthread.h"

#include <QtNetwork>

TCPImgThread::TCPImgThread(int socketDescriptor, int maxPos, QObject *parent)
    : socketDescriptor(socketDescriptor), maxPos(maxPos)
{
    connect(this, SIGNAL(pointsArrived(int, QList<QColor>)), 
            parent, SIGNAL(pointsArrived(int, QList<QColor>)), Qt::QueuedConnection);
}

void TCPImgThread::run()
{
    const int TIMEOUT = 5000;
    const int GLOBAL_TIMEOUT = 60000;

    QDateTime start_datetime = QDateTime::currentDateTime();

    QTcpSocket tcpSocket;
    if (!tcpSocket.setSocketDescriptor(socketDescriptor)) {
        emit error(tcpSocket.error());
        return;
    }

    char buf;
    qint64 byte_pos = 0;
    int r = 0, g = 0, b = 0;

    while(tcpSocket.waitForReadyRead(TIMEOUT)) {
        QList<QColor> colors;
        int pos = byte_pos / 3;

        while (tcpSocket.getChar(&buf)) {
            if (byte_pos % 3 == 0) {
                r = (unsigned char) buf;
            } else if (byte_pos % 3 == 1) {
                g = (unsigned char) buf;
            } else if (byte_pos % 3 == 2) {
                b = (unsigned char) buf;

                QColor color(r, g, b);
                if(pos >= maxPos) {
                    emit pointsArrived(pos, colors);
                    tcpSocket.disconnectFromHost();
                    return;
                } 
                colors << color;
            }

            byte_pos += 1;
        }
        emit pointsArrived(pos, colors);
        if(start_datetime.msecsTo(QDateTime::currentDateTime()) > GLOBAL_TIMEOUT) {
            break;
        }
    }

    tcpSocket.disconnectFromHost();
}
