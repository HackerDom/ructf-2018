#include <QtWidgets>
#include <QtNetwork>

#include <stdlib.h>

#include "window.h"
#include "tcpimg.h"

const int SCALE = 4;

const int WIDTH = 1366 + 2;
const int HEIGHT = 768;

const int WIDTH_SCALED = WIDTH / SCALE;
const int HEIGHT_SCALED = HEIGHT / SCALE;

const int PIXEL_UPDATE_INTERVAL = 15;
const int PIXEL_UPDATE_NUM = 50;

Window::Window(QWidget *parent)
    : QWidget(parent), pixmap(WIDTH, HEIGHT), pixmapPainter(&pixmap), 
      server(WIDTH_SCALED*HEIGHT_SCALED)
{
    pixmap.fill(QColor("black"));

    if (!server.listen(QHostAddress::Any, 31337)) {
        qWarning() << tr("Unable to start the server: %1.").arg(server.errorString());
        exit(1);
    }

    connect(&server, SIGNAL(pointsArrived(int, QList<QColor>)), 
            this, SLOT(putPoint(int, QList<QColor>)));

    timer.setInterval(PIXEL_UPDATE_INTERVAL);
    connect(&timer, SIGNAL(timeout()), this, SLOT(updateNextPixel()));
    timer.start();

    setWindowFlags(Qt::CustomizeWindowHint);
    move(0, 0);
    resize(WIDTH, HEIGHT);

    show();
}

void Window::paintEvent(QPaintEvent *event) {
    QPainter painter;
    painter.begin(this);

    painter.drawPixmap(event->rect(), pixmap, event->rect());

    painter.end();
}

QRect Window::posToRect(int pos) {
    int x = (pos % WIDTH_SCALED) * SCALE;
    int y = (pos / WIDTH_SCALED) * SCALE;

    return QRect(x, y, SCALE, SCALE);
}

void Window::putPoint(int pos, QList<QColor> colors) {
    foreach (const QColor& color, colors) {
        QRect rect = posToRect(pos);
        if (rect.top() >= HEIGHT) {
            break;
        }

        pixmapPainter.fillRect(rect, color);
        repaintSet += pos;

        pos += 1;
    }
}

void Window::updateNextPixel() {
    for (int i = 0; i < PIXEL_UPDATE_NUM; i += 1) {
        QSet<int>::iterator it;
        it = repaintSet.begin();
        if(it == repaintSet.end()) {
            break;
        }
        int pos = *it;
        repaint(posToRect(pos));
        repaintSet.erase(it);
    }
}
