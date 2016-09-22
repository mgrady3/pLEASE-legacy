"""
# Attempt to set QT_API version through sip before loading any PyQt modules
import sys
if sys.version_info[0] == 2 and sys.version_info[1] >= 7:  # python 2.7
    try:
        import sip
        sip.setapi('QString', 2)
        sip.setapi('QVariant', 2)
    except ImportError:
        print("Error: Failed to import sip; this is required by PyQt; Exiting ...")
        sys.exit(1)
elif sys.version_info[0] == 3:  # python 3
    try:
        import sip
        sip.setapi('QString', 2)  # redundant in Py3
        sip.setapi('QVariant', 2)  # redundant in Py3
    except ImportError:
        print("Error: Failed to import sip; this is required by PyQt; Exiting ...")
        sys.exit(1)
else:
    print("Error: Unsupported python version; PLEASE supports only python >= 2.7; Exiting ...")
    sys.exit(1)
"""
# The Above is now deprecated when switching to PyQt5

import gui
import os
import sys
import time
# import traceback  # intentionally left commented out to allow traceback to print
# PyQt5 will call QtCore.qFata() for any unhandled exceptions
# This can make debugging difficult
import qdarkstyle
from PyQt5 import QtCore, QtGui, QtWidgets

if QtCore.QT_VERSION >= 0x50501:
    def custom_excepthook(type_, value, traceback_):
        traceback.print_exception(type_, value, traceback_)
    old_excepthook = sys.excepthook
    sys.excepthook = custom_excepthook

# Not working ...
# Mac MenuBar Workaround
# if sys.platform == 'darwin':
#   QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_DontUseNativeMenuBar, on=True)


def main():
    """
    Entry point to PLEASE application
    :return:
    """
    app = QtWidgets.QApplication(sys.argv)

    # SplashScreen
    source_path = os.path.dirname(gui.__file__)
    # print(source_path)
    graphics_path = os.path.join(source_path, 'icons')
    # print(graphics_path)
    splash_picture = QtGui.QPixmap(os.path.join(graphics_path, 'pLEASE.png'))
    # print(os.path.join(graphics_path, 'pLEASE.png'))
    splash = QtWidgets.QSplashScreen(splash_picture, QtCore.Qt.WindowStaysOnTopHint)
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
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
