"""
This module contains classes pertinent
to creating the main GUI for the data
analysis suite

Maxwell Grady 2015
"""
import data
import terminal
import sys
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import styles as pls
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

        self.already_catching_output = False  # flag for re-routing sys.stdout

        # begin GUI setup
        self.init_UI()
        self.init_Data()

        if self._ERROR:
            # re-route sys.stdout to console window
            self.init_Console()

        # final action
        self.show()

    # Top-Level Initialization Functions
    # These functions simply place calls to second-level init functions in an orderly manner
    # or are brief enough to not need any separate functions

    def init_UI(self):
        """
        Setup GUI elements
        :return none:
        """
        self.init_styles()
        self.init_tabs()
        self.init_menu()
        self.init_layout()

    def init_Data(self):
        """

        :return none:
        """
        self.leeddat = data.LeedData()
        self.leemdat = data.LeemData()
        self.has_loaded_data = False

    def init_Plot_Axes(self):
        """

        :return none:
        """
        pass

    def init_Img_Axes(self):
        """

        :return none:
        """

    def init_Console(self):
        """

        :return none:
        """
        if self.already_catching_output:
            return
        self.message_console = terminal.ErrorConsole()
        self.message_console.setWindowTitle('Message Console')
        self.message_console.setMinimumWidth(self.max_width/4)
        self.message_console.setMinimumHeight(self.max_height/5)
        self.message_console.move(0,0)
        self.message_console.setFocus()
        self.message_console.raise_()
        self.already_catching_output = True
        self.welcome()

    # Second Level initialization functions
    # These functions do the runt of the UI, image, and plot initialization
    # they sometimes delegate to third level functions in order to keep
    # functions short and ordered

    def init_styles(self):
        """
        setup dictionary variable containing QSS style strings
        :return none:
        """
        pstyles = pls.pyLEEM_Styles()
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
        self.tabs.addTab(self.LEED_Tab, "LEED-IV")
        self.tabs.addTab(self.LEEM_Tab, "LEEM-IV")
        self.tabs.addTab(self.Config_Tab, "CONFIG")

        # call third-level init functions for each tab individually
        self.init_LEED_Tab()
        self.init_LEEM_Tab()
        self.init_Config_Tab()

    def init_LEED_Tab(self):
        """

        :return none:
        """
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

    def init_LEEM_Tab(self):
        """

        :return none:
        """
        self.LEEM_fig, (self.LEEM_ax, self.IV_ax) = plt.subplots(1, 2, figsize=(3,6))
        self.LEEM_canvas = FigureCanvas(self.LEEM_fig)
        self.LEEM_canvas.setParent(self.LEEM_Tab)
        self.LEEM_toolbar = NavigationToolbar(self.LEEM_canvas, self)

        LEEM_Tab_Layout_V1 = QtGui.QVBoxLayout()
        LEEM_Tab_Layout_H1 = QtGui.QHBoxLayout()

        LEEM_Tab_Layout_V1.addWidget(self.LEEM_canvas)
        # LEED_Tab_Layout_V1.addStretch(1)
        LEEM_Tab_Layout_V1.addWidget(self.LEEM_toolbar)

        self.LEEM_Tab.setLayout(LEEM_Tab_Layout_V1)

    def init_Config_Tab(self):
        """

        :return none:
        """
        pass

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
        loadLEEdAction = QtGui.QAction('Load LEED Data', self)
        loadLEEdAction.setShortcut('Ctrl+D')
        loadLEEdAction.triggered.connect(self.load_LEED_Data)
        LEEDMenu.addAction(loadLEEdAction)

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
    def welcome():
        """

        :return none:
        """
        print("Welcome to pythone Low-energy Electron Analyis SuitE: pLEASE")
        print("Begin by loading a LEED or LEEM data set")


    @staticmethod
    def Quit():
        print('Exiting ...')
        QtCore.QCoreApplication.instance().quit()

    # Core Functionality

    def load_LEED_Data(self):
        """
        Helper function for loading data
        Queries user for what type of data to load
        Attempts to match user input to valid data types
        Then calls appropriate loading function
        :return none:
        """
        entry, ok = QtGui.QInputDialog.getText(self, "Please Enter Data Type to Load",
                                              "Enter a valid data type from list: TIFF, PNG, DAT")
        if not ok:
            print('Loading Canceled ...')
            return
        else:
            entry = str(entry)  # convert from QString to String
            valid_extensions = ['TIFF', 'TIF' 'PNG', 'DAT']
            if not (entry in valid_extensions) and not (entry in [k.lower() for k in valid_extensions]):
                print("Error - Invalid data type entered")
                print("Please enter a data type from the following choices:")
                print("TIFF, TIF, PNG, DAT")
                self.load_LEED_Data()
                return
            else:
                if entry == 'TIFF' or entry == 'tiff' or entry == 'TIF' or entry == 'tif':
                    new_dir = str(QtGui.QFileDialog.getExistingDirectory(self, "Select directory containing TIFF files"))
                    if new_dir == '':
                        print('Loading Canceled ...')
                        return
                    print('New Data Directory set to {}'.format(new_dir))
                    self.leeddat.dat_3d = self.leeddat.load_LEED_TIFF(new_dir)
                    self.LEED_IV_ax.set_aspect('auto')
                    self.LEED_img_ax.imshow(self.leeddat.dat_3d[:, :, -1], cmap=cm.Greys_r)
                    self.LEED_IV_canvas.draw()
                    self.has_loaded_data = True

                elif entry == 'PNG' or entry == 'png':
                    new_dir = str(QtGui.QFileDialog.getExistingDirectory(self, "Select directory containing PNG files"))
                    if new_dir == '':
                        print('Loading Canceled ...')
                        return
                    print('New Data Directory set to {}'.format(new_dir))
                    self.leeddat.dat_3d = self.leeddat.load_LEED_TIFF(new_dir)
                    return

                else:
                    new_dir = str(QtGui.QFileDialog.getExistingDirectory(self, "Select directory containing DAT files"))
                    if new_dir == '':
                        print('Loading Canceled ...')
                        return
                    print('New Data Directory set to {}'.format(new_dir))

                    entry, ok = QtGui.QInputDialog.getInt(self, "Choose Image Height", "Enter Positive Int >= 2", value=544, min=2, max=2000)
                    if not ok:
                        print("Loading Raw Data Canceled ...")
                        return
                    else:
                        self.leeddat.ht = entry

                    entry, ok = QtGui.QInputDialog.getInt(self, "Choose Image Width", "Enter Positive Int >= 2", value=576, min=2, max=2000)
                    if not ok:
                        print("Loading Raw Data Canceled ...")
                        return
                    else:
                        self.leeddat.wd = entry

                    self.leeddat.dat_3d = self.leeddat.load_LEED_TIFF(new_dir)
                    self.LEED_IV_ax.set_aspect('auto')
                    self.LEED_img_ax.imshow(self.leeddat.dat_3d[:, :, -1], cmap=cm.Greys_r)
                    self.LEED_IV_canvas.draw()
                    self.has_loaded_data = True
                    return
