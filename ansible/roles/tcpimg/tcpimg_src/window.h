#ifndef WINDOW_H
#define WINDOW_H

#include <QWidget>
#include "tcpimg.h"

class Window : public QWidget
{
    Q_OBJECT

public:
    Window(QWidget *parent = 0);

    void paintEvent(QPaintEvent *event);

public slots:
    void putPoint(int coord, QList<QColor> colors);
    void updateNextPixel();

private:
    inline QRect posToRect(int pos);

    QPixmap pixmap;
    QPainter pixmapPainter;
    TCPImgServer server;

    QSet<int> repaintSet;

    QTimer timer;
};

#endif
