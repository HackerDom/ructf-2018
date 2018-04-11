#ifndef TCPIMG_H
#define TCPIMG_H

#include <QtWidgets>

#include <QTcpServer>

class TCPImgServer : public QTcpServer
{
    Q_OBJECT

public:
    TCPImgServer(int maxPos, QObject *parent = 0);

signals:
    void pointsArrived(int coord, QList<QColor>colors);

protected:
    void incomingConnection(qintptr socketDescriptor) override;

private:
    int maxPos;
};

#endif
