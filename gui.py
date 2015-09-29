"""
This module contains classes pertinent
to creating the main GUI for the data
analysis suite

Maxwell Grady 2015
"""
import sys
import matplotlib.pyplot as plt
import pyLEEM_Styles as PLS
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from PyQt4 import QtGui, QtCore


class Viewer(QtGui.QWidget):
    """

    """
    _Style = True
    _DEBUG = False
    _ERROR = True

    def __init__(self, parent=None):
        """

        :param leed:
        :param parent:
        :return none:
        """
        super(Viewer, self).__init__(parent)
        self.setWindowTitle("LEED/LEEM Image Analysis in python with Qt")
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.max_width = resolution.width()
        self.max_height = resolution.height()
        # Set App size to be 0.75 * screen width and 0.75 * screen height
        self.setGeometry(0, 0, int(0.75*self.max_width), int(0.75*self.max_height))
        # self.setGeometry(0,0,1000,800)

        # Center on Screen
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

        # begin GUI setup
        self.init_UI()

        # final action
        self.show()

    def init_UI(self):
        """
        Setup GUI elements
        :return none:
        """
        self.init_styles()
        self.init_tabs()
        self.init_menu()
        self.init_layout()

    def init_styles(self):
        """
        setup dictionary variable containing QSS style strings
        :return none:
        """
        pstyles = PLS.pyLEEM_Styles()
        self.styles = pstyles.get_styles()  # get_styles() returns a dictionary of key, qss string pairs

    def init_tabs(self):
        """
        Setup QTabWidgets
        One Tab for LEEM
        One Tab for LEED
        One Tab for Settings/Config

        :return:
        """
        self.tabs = QtGui.QTabWidget()
        self.tabs.setStyleSheet(self.styles['tab'])

        self.LEED_Tab = QtGui.QWidget()
        self.LEEM_Tab = QtGui.QWidget()
        self.Config_Tab = QtGui.QWidget()
        self.tabs.addTab(self.LEED_Tab, "LEED-FFT")
        self.tabs.addTab(self.LEEM_Tab, "LEEM-IV")
        self.tabs.addTab(self.Config_Tab, "CONFIG")

        # Setup LEED Tab
        self.LEED_IV_fig, (self.LEED_img_ax, self.LEED_IV_ax) = plt.subplots(1, 2, figsize=(6,6), dpi=100)
        self.LEED_IV_canvas = FigureCanvas(self.LEED_IV_fig)
        self.LEED_IV_canvas.setParent(self.LEED_Tab)
        self.LEED_IV_toolbar = NavigationToolbar(self.LEED_IV_canvas, self)

        LEED_Tab_Layout_V1 = QtGui.QVBoxLayout()
        LEED_Tab_Layout_H1 = QtGui.QHBoxLayout()

        LEED_Tab_Layout_V1.addWidget(self.LEED_IV_canvas)
        # LEED_Tab_Layout_V1.addStretch(1)
        LEED_Tab_Layout_V1.addWidget(self.LEED_IV_toolbar)

        self.LEED_Tab.setLayout(LEED_Tab_Layout_V1)


    def init_menu(self):
        """
        Setup Menu bar at top of main window
        :return none:
        """
        if sys.platform=='darwin':
            QtGui.qt_mac_set_native_menubar(False)

        self.menubar = QtGui.QMenuBar()
        self.menubar.setStyleSheet(self.styles['menu'])

        # File Menu
        fileMenu = self.menubar.addMenu('File')
        exitAction = QtGui.QAction('Quit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Quit PyLEEM')
        exitAction.triggered.connect(self.Quit)
        fileMenu.addAction(exitAction)

        # LEED Menu
        LEEDMenu = self.menubar.addMenu('LEED Actions')

        # LEEM Menu
        LEEMMenu = self.menubar.addMenu('LEEM Actions')

        # Settings Menu
        settingsMenu = self.menubar.addMenu('Settings')

    def init_layout(self):
        """
        Setup layout of main Window usig Hbox and VBox
        :return none:
        """

        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(self.menubar)
        vbox1.addWidget(self.tabs)
        self.setLayout(vbox1)

    @staticmethod
    def Quit():
        print('Exiting ...')
        QtCore.QCoreApplication.instance().quit()


