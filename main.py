import gui
import os
import sys
import time
import qdarkstyle
from PyQt4 import QtGui, QtCore


def main():
    """
    Entry point to PLEASE application
    :return:
    """
    app = QtGui.QApplication(sys.argv)

    # SplashScreen
    source_path = os.path.dirname(gui.__file__)
    # print(source_path)
    graphics_path = os.path.join(source_path, 'icons')
    # print(graphics_path)
    splash_picture = QtGui.QPixmap(os.path.join(graphics_path, 'pLEASE.png'))
    # print(os.path.join(graphics_path, 'pLEASE.png'))
    splash = QtGui.QSplashScreen(splash_picture, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_picture.mask())
    splash.show()
    time.sleep(3.5)

    # Start UI
    view = gui.Viewer()
    splash.finish(view)
    max_ht = view.max_height
    max_wd = view.max_width

    # Small screens
    if max_ht <= 800 and max_wd <= 1280:
        view.showMaximized()
    view.raise_()

    if view.Style:
        # Note:
        # If qdarkstyle were to drop support for PyQt in future versions this line would break
        app.setStyleSheet(qdarkstyle.load_stylesheet(pyside=False))
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
