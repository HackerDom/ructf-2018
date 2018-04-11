#include <QApplication>
#include <QtCore>

#include <stdlib.h>

#include "window.h"

int main(int argc, char *argv[])
{
    qRegisterMetaType<QList<QColor> >("QList<QColor>");

    QApplication app(argc, argv);
    Window window;
    app.exec();
    return 0;
}
