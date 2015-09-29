import gui
import sys
import terminal
import qdarkstyle
from PyQt4 import QtGui


def main():
    """

    :return:
    """
    app = QtGui.QApplication(sys.argv)
    view = gui.Viewer()
    max_ht = view.max_height
    max_wd = view.max_width

    if max_ht <= 800 and max_wd <= 1280:
        view.showMaximized()
    view.raise_()

    if view._Style:
        app.setStyleSheet(qdarkstyle.load_stylesheet(pyside=False))
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
