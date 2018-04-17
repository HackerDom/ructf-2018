#ifndef TCPTHREAD_H
#define TCPTHREAD_H

#include <QtWidgets>

#include <QThread>
#include <QTcpSocket>

class TCPImgThread : public QObject, public QRunnable
{
    Q_OBJECT

public:
    TCPImgThread(int socketDescriptor, int maxPos, QObject *parent);

    void run() override;

signals:
    void error(QTcpSocket::SocketError socketError);
    void pointsArrived(int coord, QList<QColor> colors);

private:
    int socketDescriptor;
    int maxPos;
};

#endif
