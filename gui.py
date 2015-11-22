"""
This module contains classes pertinent
to creating the main GUI for the data
analysis suite

Maxwell Grady 2015
"""
# local project imports
import data
import os
import terminal
import LEEMFUNCTIONS as LF

import time
import sys

import matplotlib.cm as cm
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import multiprocessing as mp  # this may be removed as a dependency
import numpy as np
import pandas as pd
import progressbar as pb
import seaborn as sns
import styles as pls
from matplotlib import colorbar
from matplotlib import colors as clrs
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from PyQt4 import QtGui, QtCore
from scipy.stats import linregress as lreg


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
        self.init_Data()
        self.init_UI()
        self.init_Plot_Axes()
        self.init_Img_Axes()

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
        self.hasplotted_leem = False
        self.hasplotted_leed = False
        self.hasdisplayed_leed = False
        self.hasdisplayed_leem = False
        self.border_color = (58/255., 83/255., 155/255.)  # unused

        self.rect_count = 0
        self.max_leed_click = 10
        self.rects = []
        self.rect_coords = []
        self.shifted_rects = []
        self.shifted_rect_coords = []
        self.current_selections = []
        self.smoothed_selections = []  # staging for smoothed data
        self.current_plotted_data = []  # store only curves currently displayed
        self.cor_data = None  # placeholder for corrected data to be output as text
        self.ex_back = None  # placeholder for extracted background to output as text
        self.raw_selections = None  # placeholder for raw data to output as text
        self.avg_back = None  # placeholder for average background curve to output as text

        self.colors = sns.color_palette("Set2", 10)
        self.smooth_colors = sns.color_palette("Set2", 10)

        self.smooth_leed_plot = False
        self.smooth_window_type = 'hanning'  # default value
        self.smooth_wndow_len = 8  # default value
        self.smooth_file_output = False

        self.background = []
        self.background_curves = []
        self.use_avg = False
        self.last_avg = []

        self.circs = []
        self.leem_IV_list = []
        self.leem_IV_mask = []
        self.click_count = 0
        self.max_leem_click = 7
        self.count_energy_range = '' # string of energy range used in plot labels

        self.num_one_min = 0
        self.hascountedminima = False

    def init_Plot_Axes(self):
        """

        :return none:
        """
        # Format LEED IV Axis
        self.LEED_IV_ax.set_ylabel('Intensity [arb. units]', fontsize=16)
        self.LEED_IV_ax.set_xlabel('Energy [eV]', fontsize=16)
        self.LEED_IV_ax.set_title("LEED I(V)", fontsize=20)
        if self._Style:
            self.LEED_IV_ax.set_title("LEED I(V)", fontsize=20, color='white')
            self.LEED_IV_ax.set_ylabel('Intensity [arb. units]', fontsize=16, color='white')
            self.LEED_IV_ax.set_xlabel('Energy [eV]', fontsize=16, color='white')
            self.LEED_IV_ax.tick_params(labelcolor='w', top='off', right='off')
        rect = self.LEED_IV_fig.patch
        if not self._Style:
            rect.set_facecolor((189/255., 195/255., 199/255.))
        else: rect.set_facecolor((68/255., 67/255., 67/255.))

        # Format LEEM IV Axis
        if not self._Style:
            self.LEEM_IV_ax.set_title("LEEM I(V)", fontsize=20)
            self.LEEM_IV_ax.set_ylabel("Intensity (arb. units)", fontsize=16)
            self.LEEM_IV_ax.set_xlabel("Energy (eV)", fontsize=16)
            self.LEEM_IV_ax.tick_params(labelcolor='b', top='off', right='off')
        else:
            self.LEEM_IV_ax.set_title("LEEM I(V)", fontsize=20, color='white')
            self.LEEM_IV_ax.set_ylabel("Intensity (arb. units)", fontsize=16, color='white')
            self.LEEM_IV_ax.set_xlabel("Energy (eV)", fontsize=16, color='white')
            self.LEEM_IV_ax.tick_params(labelcolor='w', top='off', right='off')

        rect = self.LEEM_fig.patch
        # 228, 241, 254
        if not self.style:
            rect.set_facecolor((189/255., 195/255., 199/255.))
        else: rect.set_facecolor((68/255., 67/255., 67/255.))
        # rect.set_facecolor((236/255., 236/255., 236/255.))  # alter the background color

        plt.style.use('fivethirtyeight')

    def init_Img_Axes(self):
        """

        :return none:
        """
        # Format LEED Image Axis
        self.LEED_img_ax.spines['top'].set_color('none')
        self.LEED_img_ax.spines['bottom'].set_color('none')
        self.LEED_img_ax.spines['left'].set_color('none')
        self.LEED_img_ax.spines['right'].set_color('none')
        self.LEED_img_ax.tick_params(labelcolor='w', top='off', bottom='off',
                                 left='off', right='off')
        self.LEED_img_ax.get_xaxis().set_visible(False)
        self.LEED_img_ax.get_yaxis().set_visible(False)
        if not self._Style:
            self.LEED_img_ax.set_title('LEED Image', fontsize=20)
        else: self.LEED_img_ax.set_title('LEED Image', fontsize=20, color='white')

        # Format LEEM Image Axis
        if not self._Style:
            self.LEEM_ax.set_title('LEEM Image: E= 0 eV', fontsize=20)
        else: self.LEEM_ax.set_title('LEEM Image: E= 0 eV', fontsize=20, color='white')

        [self.LEEM_ax.spines[k].set_visible(True) for k in ['top', 'bottom', 'left', 'right']]
        self.LEEM_ax.get_xaxis().set_visible(False)
        self.LEEM_ax.get_yaxis().set_visible(False)

    def init_Console(self):
        """

        :return none:
        """
        if self.already_catching_output:
            return
        self.message_console = terminal.ErrorConsole()
        self.message_console.setWindowTitle('Message Console')
        self.message_console.setMinimumWidth(self.max_width/3)
        self.message_console.setMinimumHeight(self.max_height/3)
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
        self.LEED_IV_fig.canvas.mpl_connect('button_release_event', self.leed_click)

    def init_LEEM_Tab(self):
        """

        :return none:
        """
        self.LEEM_fig, (self.LEEM_ax, self.LEEM_IV_ax) = plt.subplots(1, 2, figsize=(6,6))
        self.LEEM_canvas = FigureCanvas(self.LEEM_fig)
        self.LEEM_canvas.setParent(self.LEEM_Tab)
        # Hey look, now it expands just like we wanted ...
        self.LEEM_canvas.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Expanding)
        self.LEEM_toolbar = NavigationToolbar(self.LEEM_canvas, self)

        # divide layout into three main containers
        LEEM_Tab_Main_VBox = QtGui.QVBoxLayout()
        LEEM_Tab_Image_Slider_HBox = QtGui.QHBoxLayout()
        LEEM_Tab_ToolBar_HBox = QtGui.QHBoxLayout()  # may be implemented later

        # Slider Layout
        self.image_slider = QtGui.QSlider(QtCore.Qt.Horizontal, self.LEEM_Tab)
        self.image_slider.setMaximumHeight(200)
        self.image_slider.valueChanged[int].connect(self.update_image_slider)
        self.image_slider.setTickInterval(10)
        self.image_slider.setTickPosition(QtGui.QSlider.TicksAbove)

        self.image_slider_label = QtGui.QLabel(self)
        self.image_slider_label.setText("Electron Energy [eV]")

        self.image_slider_value_label = QtGui.QLabel(self)
        self.image_slider_value_label.setText("0"+"eV")

        LEEM_Tab_Image_Slider_HBox.addWidget(self.image_slider_label)
        LEEM_Tab_Image_Slider_HBox.addWidget(self.image_slider)
        LEEM_Tab_Image_Slider_HBox.addWidget(self.image_slider_value_label)

        LEEM_Tab_Main_VBox.addWidget(self.LEEM_canvas)
        LEEM_Tab_Main_VBox.addLayout(LEEM_Tab_Image_Slider_HBox)
        LEEM_Tab_Main_VBox.addWidget(self.LEEM_toolbar)

        self.LEEM_Tab.setLayout(LEEM_Tab_Main_VBox)
        self.LEEM_fig.canvas.mpl_connect('button_release_event', self.leem_click)

    def init_Config_Tab(self):
        """

        :return none:
        """
        config_Tab_groupbox = QtGui.QGroupBox()
        config_Tab_bottom_button_Hbox = QtGui.QHBoxLayout()
        config_Tab_group_button_box = QtGui.QHBoxLayout()
        config_Tab_Vbox = QtGui.QVBoxLayout()

        self.quitbut = QtGui.QPushButton('Quit', self)
        self.quitbut.clicked.connect(self.Quit)

        self.set_energy__leem_but = QtGui.QPushButton('Set Energy LEEM', self)
        self.set_energy__leem_but.clicked.connect(lambda: self.set_energy_parameters('leem'))

        self.set_energy__leed_but = QtGui.QPushButton('Set Energy LEED', self)
        self.set_energy__leed_but.clicked.connect(lambda: self.set_energy_parameters('leed'))

        buts = [self.set_energy__leem_but, self.set_energy__leed_but]

        config_Tab_group_button_box.addStretch(1)
        for b in buts:
            config_Tab_group_button_box.addWidget(b)
            config_Tab_group_button_box.addStretch(1)
        config_Tab_groupbox.setStyleSheet(self.styles['group'])
        config_Tab_groupbox.setLayout(config_Tab_group_button_box)

        config_Tab_Vbox.addWidget(config_Tab_groupbox)
        config_Tab_Vbox.addStretch(1)
        config_Tab_bottom_button_Hbox.addStretch(1)
        config_Tab_bottom_button_Hbox.addWidget(self.quitbut)
        config_Tab_Vbox.addLayout(config_Tab_bottom_button_Hbox)
        self.Config_Tab.setLayout(config_Tab_Vbox)

    def init_menu(self):
        """
        Setup Menu bar at top of main window
        :return none:
        """
        if sys.platform == 'darwin':
            QtGui.qt_mac_set_native_menubar(False)

        self.menubar = QtGui.QMenuBar()
        self.menubar.setStyleSheet(self.styles['menu'])

        # File Menu
        fileMenu = self.menubar.addMenu('File')

        outputLEEMAction = QtGui.QAction('Output LEEM to Text', self)
        outputLEEMAction.setShortcut('Ctrl+O')
        outputLEEMAction.triggered.connect(lambda: self.output_to_text(data='LEEM', smth=self.smooth_file_output))
        fileMenu.addAction(outputLEEMAction)

        exitAction = QtGui.QAction('Quit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Quit PyLEEM')
        exitAction.triggered.connect(self.Quit)
        fileMenu.addAction(exitAction)


        # LEED Menu
        LEEDMenu = self.menubar.addMenu('LEED Actions')
        loadLEEDAction = QtGui.QAction('Load LEED Data', self)
        loadLEEDAction.setShortcut('Ctrl+D')
        loadLEEDAction.triggered.connect(self.load_LEED_Data)
        LEEDMenu.addAction(loadLEEDAction)

        extractAction = QtGui.QAction('Extract I(V)', self)
        extractAction.setShortcut('Ctrl+E')
        extractAction.setStatusTip('Extract I(V) from current selections')
        extractAction.triggered.connect(self.plot_leed_IV)
        LEEDMenu.addAction(extractAction)

        subtractAction = QtGui.QAction('Subtract Background', self)
        subtractAction.setShortcut('Ctrl+B')
        subtractAction.triggered.connect(self.subtract_background)
        LEEDMenu.addAction(subtractAction)

        averageAction = QtGui.QAction('Average I(V)', self)
        averageAction.setShortcut('Ctrl+A')
        averageAction.setStatusTip('Average currently selected I(V) curves')
        averageAction.triggered.connect(self.average_current_IV)
        LEEDMenu.addAction(averageAction)

        shiftAction = QtGui.QAction('Shift Selecttions', self)
        shiftAction.setShortcut('Ctrl+S')
        shiftAction.setStatusTip('Shift User Selections based on Beam Maximum')
        shiftAction.triggered.connect(self.shift_user_selection)
        LEEDMenu.addAction(shiftAction)

        clearAction = QtGui.QAction('Clear Current I(V)', self)
        clearAction.setShortcut('Ctrl+C')
        clearAction.setStatusTip('Clear Current Selected I(V)')
        clearAction.triggered.connect(self.clear_leed_click)
        LEEDMenu.addAction(clearAction)

        clearPlotsOnlyAction = QtGui.QAction('Clear Plots', self)
        clearPlotsOnlyAction.setShortcut('Ctrl+Alt+C')
        clearPlotsOnlyAction.setStatusTip('Clear Current Plots')
        clearPlotsOnlyAction.triggered.connect(self.clear_leed_plots_only)
        LEEDMenu.addAction(clearPlotsOnlyAction)

        # LEEM Menu
        LEEMMenu = self.menubar.addMenu('LEEM Actions')
        loadLEEMAction = QtGui.QAction('Load LEEM Data', self)
        loadLEEMAction.setShortcut('Meta+M')
        loadLEEMAction.triggered.connect(self.load_LEEM)
        LEEMMenu.addAction(loadLEEMAction)

        clearLEEMAction = QtGui.QAction('Clear Current I(V)', self)
        clearLEEMAction.setShortcut('Meta+C')
        clearLEEMAction.setStatusTip('Clear Current Selected I(V)')
        clearLEEMAction.triggered.connect(self.clear_LEEM_IV)
        LEEMMenu.addAction(clearLEEMAction)

        popLEEMAction = QtGui.QAction('Popout I()V', self)
        popLEEMAction.setShortcut('Meta+P')
        popLEEMAction.triggered.connect(self.popout_LEEM_IV)
        LEEMMenu.addAction(popLEEMAction)

        smoothLEEMAction = QtGui.QAction('Smooth Current I(V)', self)
        smoothLEEMAction.setShortcut('Meta+S')
        smoothLEEMAction.triggered.connect(lambda: self.smooth_current_IV(ax=self.LEEM_IV_ax, can=self.LEEM_canvas))
        LEEMMenu.addAction(smoothLEEMAction)

        countAction = QtGui.QAction('Count Layers', self)
        countAction.setShortcut('Meta+L')
        countAction.triggered.connect(self.count_helper)
        LEEMMenu.addAction(countAction)



        # Settings Menu
        settingsMenu = self.menubar.addMenu('Settings')
        smoothAction = QtGui.QAction('Toggle Data Smoothing', self)
        smoothAction.setShortcut('Ctrl+Shift+S')
        smoothAction.setStatusTip('Turn on/off Data Smoothing')
        smoothAction.triggered.connect(self.toggle_LEED_Smoothing)
        settingsMenu.addAction(smoothAction)

        setEnergyAction = QtGui.QAction('Set Energy Parameters', self)
        setEnergyAction.setShortcut('Ctrl+Shift+E')
        setEnergyAction.triggered.connect(lambda: self.set_energy_parameters(dat='LEEM'))
        settingsMenu.addAction(setEnergyAction)

        boxAction = QtGui.QAction('Set Integration Window', self)
        boxAction.setShortcut('Ctrl+Shift+B')
        boxAction.setStatusTip('Set Integration Window Radius')
        boxAction.triggered.connect(self.set_integration_window)
        settingsMenu.addAction(boxAction)

        setEnergyAction = QtGui.QAction('Set Energy Parameters', self)
        setEnergyAction.setShortcut('Ctrl+Shift+N')
        setEnergyAction.triggered.connect(lambda: self.set_energy_parameters(dat='LEED'))
        settingsMenu.addAction(setEnergyAction)

    def init_layout(self):
        """
        Setup layout of main Window usig Hbox and VBox
        :return none:
        """

        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(self.menubar)
        vbox1.addWidget(self.tabs)
        self.setLayout(vbox1)

    def closeEvent(self, event):
        """
        Override closeEvent() to call quit()
        If main window is closed - app will Quit instead of leaving the console open
        with the main window closed
        :param event: close event from main QWidget
        :return none:
        """
        self.Quit()

    @staticmethod
    def welcome():
        """
        :return none:
        """
        print("Welcome to python Low-energy Electron Analyis SuitE: pLEASE")
        print("Begin by loading a LEED or LEEM data set")
        return

    @staticmethod
    def Quit():
        """
        :return none:
        """
        print('Exiting ...')
        QtCore.QCoreApplication.instance().quit()
        return

    # Core Functionality:
    # LEED Functions and Processes #

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
                    print('New Data shape: {}'.format(self.leeddat.dat_3d.shape))
                    if self.leeddat.dat_3d.shape[2] != len(self.leeddat.elist):
                        print('! Warning: New Data does not match current energy parameters !')
                        print('Updating Energy parameters ...')
                        self.set_energy_parameters(dat='LEED')

                elif entry == 'PNG' or entry == 'png':
                    new_dir = str(QtGui.QFileDialog.getExistingDirectory(self, "Select directory containing PNG files"))
                    if new_dir == '':
                        print('Loading Canceled ...')
                        return
                    print('New Data Directory set to {}'.format(new_dir))
                    self.leeddat.dat_3d = self.leeddat.load_LEED_PNG(new_dir)
                    print('New Data shape: {}'.format(self.leeddat.dat_3d.shape))
                    if self.leeddat.dat_3d.shape[2] != len(self.leeddat.elist):
                        print('! Warning: New Data does not match current energy parameters !')
                        print('Updating Energy parameters ...')
                        self.set_energy_parameters(dat='LEED')

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

                    self.leeddat.dat_3d = self.leeddat.load_LEED_RAW(new_dir)
                    print('New Data shape: {}'.format(self.leeddat.dat_3d.shape))
                    if self.leeddat.dat_3d.shape[2] != len(self.leeddat.elist):
                        print('! Warning: New Data does not match current energy parameters !')
                        print('Updating Energy parameters ...')
                        self.set_energy_parameters(dat='LEED')

            self.LEED_IV_ax.set_aspect('auto')
            self.LEED_img_ax.imshow(self.leeddat.dat_3d[:, :, -1], cmap=cm.Greys_r)
            self.LEED_IV_canvas.draw()
            self.has_loaded_data = True
            return

    def set_energy_parameters(self, dat=None):
        """
        """
        if dat is None:
            return

        # Get Starting Energy in eV
        entry, ok = QtGui.QInputDialog.getDouble(self, "Enter Starting Energy in eV",
                                                 "Enter a decimal for Starting Energy in eV",
                                                 value=20.5, min=-500, max=5000)
        if not ok:
            print('New Energy settings canceled ...')
            return
        start_e = float(entry)

        # Get Final Energy in eV
        entry, ok = QtGui.QInputDialog.getDouble(self, "Enter Final Energy in eV (must be larger than Start Energy)",
                                                 "Enter a decimal for Final Energy > Start Energy",
                                                 value=150, min=-500, max=5000)
        if not ok:
            print('New Energy settings canceled ...')
            return
        final_e = float(entry)
        if final_e <= start_e:
            print('Error: Final Energy must be larger than Starting Energy')
            self.set_energy_parameters(dat)
            return

        # Get Energy Step in eV
        entry, ok = QtGui.QInputDialog.getDouble(self, "Enter Energy Step in eV",
                                                 "Enter a decimal for Energy Step >0.0",
                                                 value=0.5, min=0.000001, max=500)
        if not ok:
            print('New Energy settings canceled ...')
            return
        step_e = float(entry)
        self.leemdat.e_step = step_e
        energy_list = [start_e]
        while energy_list[-1] != final_e:
            energy_list.append(round(energy_list[-1]+step_e, 2))
        if dat == 'LEED':
            self.leeddat.elist = energy_list
        elif dat == 'LEEM':
            self.leemdat.elist = energy_list
        else:
            print('Error in set_energy_parameters: Invalid data type passed as parameter')
            return

    def leed_click(self, event):
        """
        Handle mouse-clicks in the main LEED Image Axis
        :param event: matplotlib button_release_event for mouse clicks
        :return none:
        """
        if not event.inaxes == self.LEED_img_ax:
            # discard clicks that originate outside the image axis
            return
        if not self.has_loaded_data:
            return
        if self._DEBUG:
            print('LEED Click registered ...')

        if self.rect_count <= self.max_leed_click - 1:
            # not yet at maximum number of selected areas
            # print('User Clicked : {}'.format((event.xdata, event.ydata)))
            # print('Box xy = {}'.format((event.xdata-self.leeddat.box_rad, event.ydata-self.leeddat.box_rad)))
            # test = patches.Circle(xy=(event.xdata-self.leeddat.box_rad, event.ydata-self.leeddat.box_rad), radius=1, color='b')

            self.rects.append(patches.Rectangle(xy=[event.xdata-self.leeddat.box_rad, event.ydata-self.leeddat.box_rad],
                                                width=2*self.leeddat.box_rad,
                                                height=2*self.leeddat.box_rad,
                                                fill=False))
            # self.LEED_img_ax.add_patch(test)
            self.rect_coords.append((event.ydata, event.xdata))  # store location of central pixel in (r,c) format

            self.LEED_img_ax.add_artist(self.rects[-1])
            self.rects[-1].set_lw(1)
            self.rects[-1].set_color(self.colors[self.rect_count])

            self.rect_count += 1
            self.LEED_IV_canvas.draw()
        else:
            print('Resetting Click Count and Clearing Current Patches ...')
            self.clear_leed_click()

    def clear_leed_click(self):
        """

        :return none:
        """
        self.rect_count = 0
        self.LEED_IV_ax.clear()
        self.current_selections = []
        while self.rects:
            self.rects.pop().remove()
        # while self.shifted_rects:
        #    self.shifted_rects.pop().remove()
        self.rects = []
        self.rect_coords = []
        self.shifted_rects = []
        self.shifted_rect_coords = []
        # self.init_Plots()
        self.hasplotted_leed = False
        self.LEED_IV_canvas.draw()

    def clear_leed_plots_only(self):
        """

        :return none:
        """
        print('Clearing Plots ...')
        self.LEED_IV_ax.clear()
        self.LEED_IV_canvas.draw()

    def plot_leed_IV(self):
        """
        Loop through currently selected integration windows
        Extract Intensities from each window
        Plot I(V) then draw to canvas
        :return none:
        """
        self.hasplotted_leed = True

        if (self.rect_count == 0) or (not self.rects) or (not self.rect_coords):
            # no data selected; do nothing
            print('No Data Selected to Plot')
            return

        if self.leeddat.dat_3d.shape[2] != len(self.leeddat.elist):
            print("! Warning Data does not match current Energy Parameters !")
            print("Can not plot data due to mismatch ...")
            # TODO add update energy function
            return

        for idx, tup in enumerate(self.rect_coords):
            # generate 3d slice of main data array
            # this represents the integration window projected along the third array axis
            int_win = self.leeddat.dat_3d[tup[0]-self.leeddat.box_rad:tup[0]+self.leeddat.box_rad,
                                          tup[1]-self.leeddat.box_rad:tup[1]+self.leeddat.box_rad,
                                          :]
            ilist = [img.sum() for img in np.rollaxis(int_win, 2)]
            if self.smooth_leed_plot:
                print('Plotting and Storing Smoothed Data ...')
                self.current_selections.append((LF.smooth(ilist, self.smooth_window_len, self.smooth_window_type), self.smooth_colors[idx]))
                self.LEED_IV_ax.plot(self.leeddat.elist, LF.smooth(ilist, self.smooth_window_len, self.smooth_window_type),
                                     color=self.smooth_colors[idx])

            else:
                print('Plotting and Storing Raw Data ...')
                self.current_selections.append((ilist, self.colors[idx]))
                self.LEED_IV_ax.plot(self.leeddat.elist, ilist, color=self.colors[idx])

        self.LEED_IV_canvas.draw()
        return

    def average_current_IV(self):
        """
        Average the I values of the current selected curves then re-plot the average versus elist.
        Useful for plotting symmetric curves and also checking average background.
        :return none:
        """
        if (self.rect_count == 0) or (not self.rects) or (not self.rect_coords):
            print('Not Data Selected to Plot')
            return
        current_curves = []
        for idx, tup in enumerate(self.rect_coords):
            int_win = self.leeddat.dat_3d[tup[0] - self.leeddat.box_rad:tup[0] + self.leeddat.box_rad,
                                          tup[1] - self.leeddat.box_rad:tup[1] + self.leeddat.box_rad,
                                          :]
            current_curves.append([img.sum() for img in np.rollaxis(int_win, 2)])

        # calculate average intensity at each point given all entries in current_curves
        # this creates a single list of intensity values to be plotted against energy

        average_int = [float(sum(l))/float(len(l)) for l in zip(*current_curves)]

        if self.use_avg:
            print('Local Average Background Stored')
            self.background = average_int
        else:
            print('Average I(V) curve data stored')
            self.last_average = average_int
        self.use_avg = False
        self.LEED_IV_ax.clear()
        self.LEED_IV_ax.plot(self.leeddat.elist, average_int, color=self.colors[-1])
        self.LEED_IV_ax.set_title('Average I(V) of Currently Selected Curves')
        self.LEED_IV_canvas.draw()

    def toggle_LEED_Smoothing(self):
        """

        :return none:
        """

        if self.smooth_leed_plot:
            # smoothing already enabled - disable it
            self.smooth_leed_plot = False
            self.smooth_file_output = False
            print('Smoothing Disabled ...')
            return
        # Otherwise smoothing was disabled
        # now Query user for settings and enable smoothing

        # Query user for window type
        msg = '''Please enter the window type to use for data smoothing:\n
        Acceptable entries are flat, hanning, hamming, bartlett, or blackman
              '''
        entry, ok = QtGui.QInputDialog.getText(self, "Choose Window Type", msg)
        if not ok:
            return
        else:
            if entry not in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
                #print '''Invalid Entry - try again: acceptable entries are\n
                #      flat, hanning, hamming, bartlett, or blackman '''
                reply = QtGui.QMessageBox.question(self, 'Invalid Entry:', 'Invalid Entry for Smoothing Window:\nTry again?',
                                                   QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                   QtGui.QMessageBox.No)
                if reply == QtGui.QMessageBox.Yes:
                    self.toggle_LEED_Smoothing()
                    return
                else: return
            else:
                self.smooth_window_type = str(entry)

        # Query user for window length
        entry, ok = QtGui.QInputDialog.getInt(self, "Choose Window Length", "Enter Positive Even Int >= 4", value=14, min=4, max=40)
        if not ok:
            return
        else:
            if not (entry % 2 == 0) and (entry >= 4):
                print('Window_Length entry, {}, was odd - Using next even integer {}.'.format(entry, entry + 1))
                entry += 1
                self.smooth_window_len = int(entry)
            else:
                self.smooth_window_len = int(entry)
        self.smooth_leed_plot = True
        self.smooth_file_output = True
        print('Smoothing Enabled: Window = {}; Window Length = {}'.format(self.smooth_window_type, self.smooth_window_len))
        return

    def set_integration_window(self):
        """

        :return none:
        """
        entry, ok = QtGui.QInputDialog.getInt(self, "Set Integration Window Half Length",
                                              "Enter a valid integer >= 2.", value=20, min=2, max=2000)
        if not ok:
            return
        self.leeddat.box_rad = entry
        print('New Integration Window set to {} x {}.'.format(2*self.leeddat.box_rad, 2*self.leeddat.box_rad))

    def subtract_background(self):
        """
        For all curves currently selected, perform a background subtraction
        This is accomplished by calculating the average intensity of the perimeter
        of each integration window and subtracting this value from each pixel in the
        integration window. This is repeated for each energy value so that the background
        subtracted can change as a function of energy.
        It may be useful to analyze the function I_back(V) at a later time thus for each curve
        the background which was subtracted is stored as a list of intensities so they can be
        plotted against Energy.
        :return none:
        """
        if not self.hasplotted_leed:
            return

        self.background_curves = []
        print('Starting Background Subtraction Procedure ...')
        for idx, tup in enumerate(self.rect_coords):
            data_subset = self.leeddat.dat_3d[tup[0]-self.leeddat.box_rad:tup[0]+self.leeddat.box_rad,
                                              tup[1]-self.leeddat.box_rad:tup[1]+self.leeddat.box_rad,
                                              :]
            adj_ilist = []  # create list to hold adjusted intensities
            # iterate over each image in the data subset

            # manually cast to int16 to prevent integer overflow when subtracting from an array of unsigned integers!!!

            bkgnd = []
            for img in np.rollaxis(data_subset, 2).astype(np.int16):
                # perimeter sum
                ps = (img[0, 0:] + img[0:, -1] + img[-1, :] + img[0:, 0]).sum()  # sum edges
                ps -= (img[0,0] + img[0, -1] + img[-1, -1] + img[-1, 0])  # subtract corners for double counting

                num_pixels = 2*(2*(2*self.leeddat.box_rad)-2)
                ps /= num_pixels
                bkgnd.append(ps)  # store average perimeter pixel value

                if self._DEBUG:
                    print("Average Background calculated as {}".format(ps))
                    print("Raw Sum: {}".format(img.sum()))

                img -= int(ps)  # subtract background from each pixel

                if self._DEBUG:
                    print("Adjusted Sum: {}".format(img[img >= 0].sum()))
                    print img

                # calculate new total intensity of the integration window counting only positive values
                # there should be no negatives but we discard them just incase
                adj_ilist.append(img[img >= 0].sum())

            self.background_curves.append(bkgnd)

            self.current_selections.append((adj_ilist, self.colors[idx]))

        avg_background = [sum(l)/len(l) for l in zip(*self.background_curves)]
        print("Finished Subtracting Background ...")
        print("Re-plotting original data and corrected data")

        # pop out a new window and plot side by side
        # self.pop_window = QtGui.QWidget()
        self.pop_window1 = QtGui.QWidget()  # raw data
        self.pop_window2 = QtGui.QWidget()  # corrected data
        self.pop_window3 = QtGui.QWidget()  # extracted backgrounds
        self.pop_window4 = QtGui.QWidget()  # average background

        windows = [self.pop_window1, self.pop_window2, self.pop_window3, self.pop_window4]

        # figures and axes
        self.nfig1, self.nplot_ax1 = plt.subplots(1,1, figsize=(10,10), dpi=100)
        self.nfig2, self.nplot_ax2 = plt.subplots(1,1, figsize=(10,10), dpi=100)
        self.nfig3, self.nplot_ax3 = plt.subplots(1,1, figsize=(10,10), dpi=100)
        self.nfig4, self.nplot_ax4 = plt.subplots(1,1, figsize=(10,10), dpi=100)

        axlist = [self.nplot_ax1, self.nplot_ax2, self.nplot_ax3, self.nplot_ax4]

        # canvases
        self.ncanvas1 = FigureCanvas(self.nfig1)  # raw data
        self.ncanvas2 = FigureCanvas(self.nfig2)  # corrected data
        self.ncanvas3 = FigureCanvas(self.nfig3)  # extracted backgrounds
        self.ncanvas4 = FigureCanvas(self.nfig4)  # average background
        self.ncanvas1.setParent(self.pop_window1)  # raw data
        self.ncanvas2.setParent(self.pop_window2)  # corrected data
        self.ncanvas3.setParent(self.pop_window3)  # extracted backgrounds
        self.ncanvas4.setParent(self.pop_window4)  # average background

        canvases = [self.ncanvas1, self.ncanvas2, self.ncanvas3, self.ncanvas4]

        # toolbars
        self.nmpl_toolbar1 = NavigationToolbar(self.ncanvas1, self.pop_window1)  # raw data
        self.nmpl_toolbar2 = NavigationToolbar(self.ncanvas2, self.pop_window2)  # corrected data
        self.nmpl_toolbar3 = NavigationToolbar(self.ncanvas3, self.pop_window3)  # extracted backgrounds
        self.nmpl_toolbar4 = NavigationToolbar(self.ncanvas4, self.pop_window4)  # average background

        # format layout in pop_windows
        # raw data
        nvbox = QtGui.QVBoxLayout()
        nvbox.addWidget(self.ncanvas1)
        nhbox = QtGui.QHBoxLayout()
        nvbox.addLayout(nhbox)
        nvbox.addWidget(self.nmpl_toolbar1)
        # raw data output button
        rawoutbut = QtGui.QPushButton("Output to Text", self)
        rawoutbut.clicked.connect(lambda: self.output_to_text(data=self.raw_selections, smth=self.smooth_file_output))  # output button
        nhbox.addStretch(1)
        nhbox.addWidget(rawoutbut)
        self.pop_window1.setLayout(nvbox)

        # corrected data
        nvbox = QtGui.QVBoxLayout()
        nvbox.addWidget(self.ncanvas2)
        nhbox = QtGui.QHBoxLayout()

        nhbox.addWidget(self.nmpl_toolbar2)
        # corrected data output button
        coroutputbutton = QtGui.QPushButton("Output to Text", self)
        coroutputbutton.clicked.connect(lambda: self.output_to_text(data=self.cor_data, smth=self.smooth_file_output))  # output button
        nhbox.addStretch(1)
        nhbox.addWidget(coroutputbutton)
        nvbox.addLayout(nhbox)
        self.pop_window2.setLayout(nvbox)

        # extracted backgrounds
        nvbox = QtGui.QVBoxLayout()
        nvbox.addWidget(self.ncanvas3)
        nhbox = QtGui.QHBoxLayout()
        nvbox.addLayout(nhbox)
        nhbox.addWidget(self.nmpl_toolbar3)
        # extracted background output button
        exbackoutbut = QtGui.QPushButton("Output to Text", self)
        exbackoutbut.clicked.connect(lambda: self.output_to_text(data=self.ex_back, smth=self.smooth_file_output))  # output button
        nhbox.addStretch(1)
        nhbox.addWidget(exbackoutbut)
        self.pop_window3.setLayout(nvbox)

        # average background
        nvbox = QtGui.QVBoxLayout()
        nvbox.addWidget(self.ncanvas4)
        nhbox = QtGui.QHBoxLayout()
        nvbox.addLayout(nhbox)
        nvbox.addWidget(self.nmpl_toolbar4)
        avgbackoutbut = QtGui.QPushButton("Output to Text", self)
        avgbackoutbut.clicked.connect(lambda: self.output_to_text(data=self.avg_back, smth=self.smooth_file_output))  # output button
        nhbox.addStretch(1)
        nhbox.addWidget(avgbackoutbut)
        self.pop_window4.setLayout(nvbox)

        num_curves = len(self.current_selections)
        last_raw_curve_idx = num_curves/2 -1
        if self._DEBUG:
            print("Number of total curves to plot = {}".format(num_curves))
            print("Index of last raw curve = {}".format(last_raw_curve_idx))

        avg_bknd_curve_list = []
        a = []

        # raw data
        self.raw_selections = self.current_selections[0:last_raw_curve_idx +1]
        for tup in self.current_selections[0:last_raw_curve_idx +1]:
            # plot raw data for all currently selected curves

            self.nplot_ax1.plot(self.leeddat.elist, tup[0], color=tup[1])

        # corrected data
        for tup in self.current_selections[last_raw_curve_idx + 1:]:
            avg_bknd_curve_list.append(tup[0])
            a = [sum(l)/len(l) for l in zip(*avg_bknd_curve_list )]
            # plot background corrected data for all currentyl selected curves
            self.nplot_ax2.plot(self.leeddat.elist, tup[0], color=tup[1])  # corrected data
            self.cor_data = tup[0]  # currently only works when one curve is selected

        # self.nplot_ax2.plot(self.leeddat.elist, a, color=self.colors[-1])

        # extracted backgrounds
        self.ex_back = self.background_curves
        for idx, l in enumerate(self.background_curves):
            # plot I_back(V) for each currently selected curve
            self.nplot_ax3.plot(self.leeddat.elist, l, color=self.colors[idx])

        # average background
        self.avg_back = avg_background
        self.nplot_ax4.plot(self.leeddat.elist, avg_background, color=self.colors[-1])

        # styles and labels
        titles = ["Raw Data", "Background Adjusted Data", "Calculated Background", "Averaged Background"]
        rect1 = self.nfig1.patch
        rect2 = self.nfig2.patch
        rect3 = self.nfig3.patch
        rect4 = self.nfig4.patch

        if not self._Style:
            rect1.set_facecolor((189/255., 195/255., 199/255.))
            rect2.set_facecolor((189/255., 195/255., 199/255.))
            rect3.set_facecolor((189/255., 195/255., 199/255.))
            rect4.set_facecolor((189/255., 195/255., 199/255.))

            for idx, ax in enumerate(axlist):
                    ax.set_title(titles[idx], color='k')
                    ax.set_xlabel("Energy [eV]", color='k')
                    ax.set_ylabel("Intensity [arb. units]", color='k')
                    ax.tick_params(labelcolor='k', top='off', right='off')

        else:

            rect1.set_facecolor((68/255., 67/255., 67/255.))
            rect2.set_facecolor((68/255., 67/255., 67/255.))
            rect3.set_facecolor((68/255., 67/255., 67/255.))
            rect4.set_facecolor((68/255., 67/255., 67/255.))

            for idx, ax in enumerate(axlist):
                    ax.set_title(titles[idx], color='w')
                    ax.set_xlabel("Energy [eV]", color='w')
                    ax.set_ylabel("Intensity [arb. units]", color='w')
                    ax.tick_params(labelcolor='w', top='off', right='off')

        for can in canvases:
            can.draw()

        for w in windows:
            w.show()

    def output_to_text(self, data=None, smth=False):
        """
        Write out data to text files in columar format
        :param data: container for data to be output; may be single list or list of lists
        :param smth: bool to decide if smooth() should be applied to data before output; default to False
        :return none:
        """
        if data is None:
            # no data passed as input; do nothing
            print('No Data!!! ...')
            return
        multi_output = False  # boolean flag for whether or not outputting multiple files is needed
        subtype = None  # type check for possible sub-containers in main data container

        if data == 'LEEM':
            # handle LEEM output
            if not self.hasplotted_leem:
                return
            if not os.path.exists(os.path.join(self.leemdat.data_dir, 'ivout')):
                os.path.mkdir(os.path.join(self.leemdat.data_dir, 'ivout'))
            leem_out_dir = os.path.join(self.leemdat.data_dir, 'ivout')
            for tup in self.leem_IV_list:
                outfile = os.path.join(leem_out_dir, str(tup[2])+'-'+str(tup[3])+'.txt')
                dicout = {'I': tup[1], 'E': tup[0]}
                outdf = pd.DataFrame(dicout)
                print('Writing Output File: {} ...'.format(outfile))
                outdf.to_csv(outfile, sep='\t', index=False)
            return

        # else - handle LEED output
        if type(data) is list:
            # check for sub-containers
            if type(data[0]) is list:
                # main data is a container of containers
                # there may be multiple curves to output into separate files
                multi_output = True
                subtype = 'list'
            elif type(data[0]) is tuple:
                # main data is a container of containers
                # there may be multiple curves to output into separate files
                multi_output = True
                subtype = 'tuple'
            elif type(data[0]) is int or type(data[0]) is float:
                # main data container is simply a list of numbers
                # only one output file is needed
                multi_output = False
                subtype = None
            else:
                print("Invalid Call to output_to_text()")
                print("data param should be list, list of lists, or list of tuples")
                return
        else:
            print("Invalid Call to output_to_text()")
            print("data param should be list, list of lists, or list of tuples")
            return

        # Begin File Output Logic
        # Query User for directory to output to
        out_dir = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory for File Output",
                                                             options=QtGui.QFileDialog.ShowDirsOnly))
        out_dir = LF.parse_dir(out_dir)  # get rid of trailing '/untitled/' if it exists
        if out_dir == '':
            print('File Output Canceled...')
            return
        instrc = """ Enter name for textfile. No Spaces, No Extension.
    If multiple files are to be output - the same base name will be used for each.
    A consecutive number will be appended to the end of the file name.
                """
        # Query User for filename
        entry, ok = QtGui.QInputDialog.getText(self, "Enter Filename without Extension", instrc)
        if not ok:
            print("File Output Canceled ...")
            return
        entry = str(entry)  # convert from QString to String
        if not multi_output:
            # handle single file output
            name = entry + '.txt'
            if smth:
                # generate smoothed (V, I) pairs
                smth_dat = LF.smooth(data, self.smooth_window_len, self.smooth_window_type)
                IV_combo = [(self.leeddat.elist[index], smth_dat[index]) for index, _ in enumerate(self.leeddat.elist)]
            else:
                # generate raw (V, I) pairs
                IV_combo = [(self.leeddat.elist[index], data[index]) for index, _ in enumerate(self.leeddat.elist)]
            print('Writing Text Output: {}'.format(os.path.join(out_dir, name)))
            with open(os.path.join(out_dir, name), 'w') as f:
                for tup in IV_combo:
                    f.write(str(tup[0]) + '\t' + str(tup[1]) + '\n')

        else:
            # handle multiple file output
            # loop over each subcontainer in the main data construct
            for idx, cnt in enumerate(data):
                name = entry + '_' + str(idx + 1) + '.txt'
                if smth:
                    # generate smoothed (V, I) pairs
                    if subtype == 'list':
                        smth_dat = LF.smooth(data[idx], self.smooth_window_len, self.smooth_window_type)
                    elif subtype == 'tuple':
                        smth_dat = LF.smooth(data[idx][0], self.smooth_window_len, self.smooth_window_type)
                    else:
                        print('Error in data type passed to output_to_text()')
                        print('File output canceled ...')
                        return
                    IV_combo = [(self.leeddat.elist[index], smth_dat[index]) for index, _ in enumerate(self.leeddat.elist)]
                else:
                    # generate raw (V, I) pairs
                    if subtype == 'list':
                        IV_combo = [(self.leeddat.elist[index], data[idx][index]) for index, _ in enumerate(self.leeddat.elist)]
                    elif subtype == 'tuple':
                        IV_combo = [(self.leeddat.elist[index], data[idx][0][index]) for index, _ in enumerate(self.leeddat.elist)]
                    else:
                        print('Error in data type passed to output_to_text()')
                        print('File output canceled ...')
                        return
                print('Writing Text Output: {}'.format(os.path.join(out_dir, name)))
                with open(os.path.join(out_dir, name), 'w') as f:
                    for tup in IV_combo:
                        f.write(str(tup[0]) + '\t' + str(tup[1]) + '\n')
        print('Done Writing Files ...')

    def shift_user_selection(self):
        self.shifted_rects = []
        self.shifted_rect_coords = []
        for tup in self.rect_coords:
            int_win = self.leeddat.dat_3d[tup[0]-self.leeddat.box_rad:tup[0]+self.leeddat.box_rad,
                                          tup[1]-self.leeddat.box_rad:tup[1]+self.leeddat.box_rad,
                                          :]

            maxLoc = LF.find_local_maximum(int_win[:, :, -1])  # (x,y)
            # print('Old Beam Center: (r,c) =  {}'.format(tup))
            r_u, c_u = tup  # user selected coordinates
            c_3, r_3 = maxLoc  # beam center offset relative to top left corner of integration window
            new_xy = (c_u + c_3 - 2*self.leeddat.box_rad, r_u + r_3 - 2*self.leeddat.box_rad)
            # print('New Beam Center: (r,c) = {}'.format((r_u - self.leeddat.box_rad + r_3,
            #                                            c_u - self.leeddat.box_rad + c_3)))

            self.shifted_rects.append(patches.Rectangle(xy=new_xy,
                                                        width=2*self.leeddat.box_rad,
                                                        height=2*self.leeddat.box_rad,
                                                        fill=False
                                                        ))
            self.shifted_rect_coords.append((r_u + r_3 - self.leeddat.box_rad,
                                             c_u + c_3 - self.leeddat.box_rad))  # beam center in (r,c) coordinates

        # remove currently selected rectangles
        while self.rects:
            self.rects.pop().remove()
        # plot corrected rectangles
        for idx, _ in enumerate(self.shifted_rects):
            self.LEED_img_ax.add_artist(self.shifted_rects[idx])
            self.shifted_rects[idx].set_lw(1)
            self.shifted_rects[idx].set_color(self.colors[idx])
            self.LEED_IV_canvas.draw()
        self.rects = self.shifted_rects[:]
        self.rect_coords = self.shifted_rect_coords[:]

    # Core Functionality:
    # LEEM Functions and Processes #

    def load_LEEM(self):
        """

        :return none:
        """
        if self.hasplotted_leem:
            # if curves already displayed, just clear the IV plots
            # reset any plotting variables
            self.clear_LEEM_IV()
        self.LEEM_ax.clear()
        self.LEEM_IV_ax.clear()
        prev_ddir = self.leemdat.data_dir  # in case of error in loading data, keep reference to previous data directory
        ddir = QtGui.QFileDialog.getExistingDirectory(self, "Select Data Directory")  # note this is a QString

        if ddir == '':
            # Error Loading Data
            print('Error Loading LEEM Data ...')
            return
        self.leemdat.data_dir = str(ddir)  # manually cast from QString to String
        self.leemdat.img_mask_count_dir = os.path.join(str(ddir), 'img_mask_count')
        if not os.path.exists(self.leemdat.img_mask_count_dir):
            os.mkdir(self.leemdat.img_mask_count_dir)
        print('Setting LEEM Data directory to {}'.format(self.leemdat.data_dir))

        # Use manual dialog creation to set size and text properly
        id = QtGui.QInputDialog(self)
        id.setInputMode(QtGui.QInputDialog.IntInput)
        id.setLabelText("Enter Positive Integer >= 2")
        id.setWindowTitle("Enter Image Height in Pixels")
        id.setIntMinimum(2)
        id.setIntMaximum(10000)
        id.resize(400, 300)
        ok = id.exec_()
        entry = id.intValue()

        if not ok:
            print("Loading Raw Data Canceled ...")
            return
        else:
            self.leemdat.ht = entry

        # Use manual dialog creation to set size and text properly
        id = QtGui.QInputDialog(self)
        id.setInputMode(QtGui.QInputDialog.IntInput)
        id.setLabelText("Enter Positive Integer >= 2")
        id.setWindowTitle("Enter Image Width in Pixels")
        id.setIntMinimum(2)
        id.setIntMaximum(10000)
        id.resize(400, 300)
        ok = id.exec_()
        entry = id.intValue()

        if not ok:
            print("Loading Raw Data Canceled ...")
            return
        else:
            self.leemdat.wd = entry

        try:
            self.leemdat.dat_3d = LF.process_LEEM_Data(self.leemdat.data_dir,
                                                       self.leemdat.ht,
                                                       self.leemdat.wd)
        except ValueError:
            print('Error Loading LEEM Data: Please Recheck Image Settings')
            print('Resetting data directory to previous setting, {}'.format(prev_ddir))
            return

        # Assuming that data loading was successful - self.leemdat.dat_3d is now a 3d numpy array
        # Generate energy list to correspond to the third array axis
        print('Data Loaded successfully: {}'.format(self.leemdat.dat_3d.shape))
        self.set_energy_parameters(dat='LEEM')
        self.format_slider()
        self.hasdisplayed_leem = True

        if not self.has_loaded_data:
            self.update_image_slider(self.leemdat.dat_3d.shape[2]-1)
            self.has_loaded_data = True
            return
        self.update_image_slider(0)
        return

    def format_slider(self):
        self.image_slider.setRange(0, self.leemdat.dat_3d.shape[2]-1)

    def update_image_slider(self, value):
        """
        Update the Slider label value to the new electron energy
        Call show_LEEM_Data() to display the correct LEEM image
        :argument value: integer value from slider representing filenumber
        :return none:
        """

        self.image_slider_value_label.setText(str(
                                    LF.filenumber_to_energy(
                                                            self.leemdat.elist,
                                                            value)) + " eV")
        self.show_LEEM_Data(self.leemdat.dat_3d, value)

    def clear_LEEM_IV(self):
        """

        :return none:
        """
        if not self.hasplotted_leem:
            return
        if not self.circs:
            self.circs = []  # is this redundant?
        else:
            while self.circs:
                self.circs.pop().remove()
        self.LEEM_IV_ax.clear()
        self.init_Plot_Axes()
        self.click_count = 0
        self.leem_IV_list = []
        self.leem_IV_mask = []
        if not self._Style:
            self.LEEM_ax.set_title('LEEM Image: E= ' + str(LF.filenumber_to_energy(self.leemdat.elist,
                                                                                   self.leemdat.curimg)), fontsize=16)
        else:
            self.LEEM_ax.set_title('LEEM Image: E= ' + str(LF.filenumber_to_energy(self.leemdat.elist,
                                                                                   self.leemdat.curimg)), fontsize=16, color='white')
        self.LEEM_canvas.draw()


    def show_LEEM_Data(self, data, imgnum):
        """

        :param data:
        :param imgnum:
        :return none:
        """
        self.leemdat.curimg = imgnum
        img = data[0:, 0:, self.leemdat.curimg]

        if self._Style:
            self.LEEM_ax.set_title('LEEM Image: E= ' + str(LF.filenumber_to_energy(self.leemdat.elist, self.leemdat.curimg)) +' eV', fontsize=16, color='white')
        else:
            self.LEEM_ax.set_title('LEEM Image: E= ' + str(LF.filenumber_to_energy(self.leemdat.elist, self.leemdat.curimg)) +' eV', fontsize=16)

        self.LEEM_ax.imshow(img, cmap=cm.Greys_r)
        self.LEEM_canvas.draw()
        return

    def leem_click(self, event):
        """
        Handle mouse click events that originate from/in the LEEM image axis
        :param event: mpl mouse_click_event
        :return none:
        """
        if not self.hasdisplayed_leem:
            return

        if event.inaxes == self.LEEM_ax:

            self.click_count += 1
            if self.click_count <= self.max_leem_click:
                self.circs.append(plt.Circle((event.xdata, event.ydata),
                                             radius=3,
                                             fc=self.colors[self.click_count-1]))
                self.LEEM_ax.add_patch(self.circs[-1])
                self.LEEM_canvas.draw()
            else:
                self.click_count = 1
                self.LEEM_IV_ax.clear()
                self.leem_IV_list = []
                while self.circs:
                    self.circs.pop().remove()
                self.circs.append(plt.Circle((event.xdata, event.ydata),
                                             radius=3,
                                             fc=self.colors[self.click_count-1]))
                self.LEEM_ax.add_patch(self.circs[-1])
                self.LEEM_canvas.draw()
            self.plot_leem_IV(event)
        return

    def plot_leem_IV(self, event):
        """
        Load intensity data from the nearest pixel to the mouseclick into the leemdat construct
        Update current (X,Y) parameters
        Plot intensity against energy
        :param event: mpl mouse_click_event
        :return none:
        """
        self.hasplotted_leem = True
        # Grab the nearest pixel value from matplotlib floats
        self.leemdat.curX = int(event.xdata)
        self.leemdat.curY = int(event.ydata)
        self.leemdat.ilist=[]

        # swap X and Y for R, C format
        # test easier method for generating list

        # OLD:
        # for i in self.leemdat.dat_3d[self.leemdat.curY,
        #                            self.leemdat.curX, :]:
        #   self.leemdat.ilist.append(i)

        self.leemdat.ilist = list(self.leemdat.dat_3d[
                                  self.leemdat.curY,
                                  self.leemdat.curX, :
                                  ])


        if len(self.leemdat.elist) != len(self.leemdat.ilist):
            print('Error in Energy List Size')
            return

        self.LEEM_IV_ax.plot(self.leemdat.elist, self.leemdat.ilist, color=self.colors[self.click_count-1])
        self.leem_IV_list.append((self.leemdat.elist, self.leemdat.ilist,
                                  self.leemdat.curX, self.leemdat.curY,
                                  self.click_count-1)) # color stored by click count index
        self.leem_IV_mask.append(0)
        self.init_Plot_Axes()
        self.LEEM_canvas.draw()

    def popout_LEEM_IV(self):
        """

        :return:
        """
        if not self.hasplotted_leem or len(self.leem_IV_list) == 0:
            return

        self.pop_window_lm = QtGui.QWidget()
        self.pop_window_lm.setMinimumHeight(0.35*self.max_height)
        self.pop_window_lm.setMinimumWidth(0.45*self.max_width)
        self.nfig_lm, self.nplot_ax_lm = plt.subplots(1,1, figsize=(8,6), dpi=100)
        self.ncanvas_lm = FigureCanvas(self.nfig_lm)
        self.ncanvas_lm.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Expanding)
        self.popsmoothbut = QtGui.QPushButton("Smooth I(V)")
        self.popsmoothbut.clicked.connect(lambda: self.smooth_current_IV(self.nplot_ax_lm, self.ncanvas_lm))
        self.nmpl_toolbar_lm = NavigationToolbar(self.ncanvas_lm, self.pop_window_lm)

        nvbox = QtGui.QVBoxLayout()
        nvbox.addWidget(self.ncanvas_lm)
        nhbox = QtGui.QHBoxLayout()
        nhbox.addWidget(self.nmpl_toolbar_lm)
        nhbox.addStretch(1)
        nhbox.addWidget(self.popsmoothbut)
        nvbox.addLayout(nhbox)
        self.pop_window_lm.setLayout(nvbox)

        for tup in self.leem_IV_list:
            self.nplot_ax_lm.plot(tup[0], tup[1], color=self.colors[tup[4]])
        rect = self.nfig_lm.patch
        if self._Style:
            rect.set_facecolor((68/255., 67/255., 67/255.))
            self.nplot_ax_lm.set_title("LEEM I(V)", fontsize=12, color='w')
            self.nplot_ax_lm.set_ylabel("Intensity (arb. units)", fontsize=12, color='w')
            self.nplot_ax_lm.set_xlabel("Energy (eV)", fontsize=12, color='w')
            self.nplot_ax_lm.xaxis.label.set_color('w')
            self.nplot_ax_lm.yaxis.label.set_color('w')
            self.nplot_ax_lm.tick_params(labelcolor='w', top='off', right='off')

        else:
            rect.set_facecolor((189/255., 195/255., 199/255.))
            self.nplot_ax_lm.set_title("LEEM I(V)", fontsize=12)
            self.nplot_ax_lm.set_ylabel("Intensity (arb. units)", fontsize=12)
            self.nplot_ax_lm.set_xlabel("Energy (eV)", fontsize=12)
        self.ncanvas_lm.draw()
        self.pop_window_lm.show()

    def smooth_current_IV(self, ax, can):
        """
        Apply data smoothing algorithm to currently plotted I(V) curves
        :param ax: mpl axis element which ill be plotting data
        :param can: canvas containing ax which needs to call draw() to update the image
        :return none:
        """
        if not self.hasplotted_leem or len(self.leem_IV_list) == 0:
            return
        ax.clear()

        # Query user for window type
        msg = '''Please enter the window type to use for data smoothing:\n
        Acceptable entries are flat, hanning, hamming, bartlett, or blackman
              '''
        entry, ok = QtGui.QInputDialog.getText(self, "Choose Window Type", msg)
        if not ok:
            return
        else:
            if entry not in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
                #print '''Invalid Entry - try again: acceptable entries are\n
                #      flat, hanning, hamming, bartlett, or blackman '''
                reply = QtGui.QMessageBox.question(self, 'Invalid Entry:', 'Invalid Entry for Smoothing Window:\nTry again?',
                                                   QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                   QtGui.QMessageBox.No)
                if reply == QtGui.QMessageBox.Yes:
                    self.smooth_curIV(ax, can)
                    return

                else: return
            else:
                self.smooth_window_type = str(entry)

        # Query user for window length
        entry, ok = QtGui.QInputDialog.getInt(self, "Choose Window Length", "Enter Positive Even Int >= 4", value=14, min=4, max=40)
        if not ok:
            return
        else:
            if not (entry % 2 == 0) and (entry >= 4):
                print 'Window_Length entry, %i, was odd - Using next even integer %i' % (entry, entry + 1)
                entry += 1
                self.smooth_window_len = int(entry)

            else:
                self.smooth_window_len = int(entry)

        for idx, tup in enumerate(self.leem_IV_list):
            ax.plot(tup[0], LF.smooth(tup[1], self.smooth_window_len, self.smooth_window_type), color=self.colors[tup[4]])
        if self._Style:
            ax.set_title("LEEM I(V)-Smoothed", fontsize=16, color='w')
            ax.set_ylabel("Intensity (arb. units)", fontsize=16, color='w')
            ax.set_xlabel("Energy (eV)", fontsize=16, color='w')
        else:
            ax.set_title("LEEM I(V)-Smoothed", fontsize=16)
            ax.set_ylabel("Intensity (arb. units)", fontsize=16)
            ax.set_xlabel("Energy (eV)", fontsize=16)
        can.draw()

    def count_layers_old(self):
        """
        Attempt to count the number of minima for each I(V) curve by iterating over all
        pixels in the topmost image in the most efficient way using np.nditer()

        This method iterates over the 3d numpy array in stored memory order

        Each I(V) curve is first smoothed with a boxcar window convolution in order
        to remove noise in the data.

        The main data array is sub-set for each curve extraction to only pull the data
        in the relevant energy range so as to save computational time when calculating
        numeric derivatives

        :return none:
        """
        if not self.hasdisplayed_leem or len(self.leemdat.elist) <= 2:
            return

        reply = QtGui.QMessageBox.question(self, "Continue?", "Mapping the number of layers may take 2-10 mins. \n" +
                                                          "Are you sure you want to continue?", QtGui.QMessageBox.Yes|
                                                           QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.No:
            return

        # SKIP Loading PRE-Computed Image Mask for now

        # default values for energy window
        def_min_e = 0
        def_max_e = 5.1

        # query user to set minimum energy
        min_e, ok = QtGui.QInputDialog.getDouble(self,"Set Minimum Energy", "Input a float value for Min Energy greater or equal to 0.",
                                             0, 0, 10, 1)
        if not ok:
            min_e = def_min_e  # use default if input was canceled

        # query and set max energy
        max_e, ok = QtGui.QInputDialog.getDouble(self,"Set Maximum Energy", "Input a float value for Max Energy less than or equal to 15.",
                                             0, 0, 10, 1)
        if not ok:
            max_e = def_max_e  # use default if input was canceled

        min_index = self.leemdat.elist.index(min_e)
        max_index = self.leemdat.elist.index(max_e)

        # string of energy range used in plot labels
        self.count_energy_range = '[' + str(min_e)+', '+str(max_e - self.leemdat.e_step) +']'
        self.img_mask_count = np.zeros((self.leemdat.ht, self.leemdat.wd))
        top_image = self.leemdat.dat_3d[0:, 0:, 0]  # topmost image in I(V) set
        data_cut = self.leemdat.dat_3d[0:, 0:, min_index:max_index]
        ecut = self.leemdat.elist[min_index:max_index]

        num_flat = 0  # used for testing purposes
        num_non_flat = 0  # used for testing purposes
        flat_coords = []  # used for testing purposes
        self.num_one_min = 0  # reset count of single minima curves
        self.hascountedminima = True

        # BEGIN CALCULATION
        # prog = pb.ProgressBar(fd=sys.stdout, maxval=self.leemdat.ht*self.leemdat.wd).start()
        # pixnum = 0
        print('Starting I(V) analysis ...')
        t_start = time.time()
        it = np.nditer(top_image, flags=['multi_index'])  # numpy iterator
        while not it.finished:
            print('\n')
            r = it.multi_index[0]  # row index
            c = it.multi_index[1]  # column index
            IV = list(data_cut[r, c, 0:])  # I(V) data set for the current pixel
            # Smooth the dataset using the convolution method
            # apply a flat window of 10*e_step length in energy units
            SIV = LF.smooth(IV, 10, 'flat')

            # check if curve is approximately flat
            check = self.check_flat(ecut, SIV)
            if check[0]:
                # curve is flat
                num_flat += 1
                # manually set count value to 0
                self.img_mask_count[r,c] = 0
                if num_flat%1000 == 0:
                    flat_coords.append((r,c))
            else:
                # curve is not flat
                self.img_mask_count[r,c] = check[1]
                num_non_flat += 1
            # pixnum += 1
            # prog.update(value=pixnum)
            it.iternext()
        t_end = time.time()
        print('Done counting minima - total time elapsed = {}  minutes'.format(round(round((t_end - t_start), 2)/60.0, 1)))

        self.discrete_imshow(self.img_mask_count, cmap=cm.Spectral)

    def check_flat_old(self, xd, yd):
        """
        NOTE: Consider moving this function to data.py in the LeemData class
        :param xd: array-like set of x values
        :param yd: array-like set of y values
        :return: tuple of two elements: (boolean for curve is flat?, integer # of minima found)
        """
        mins = LF.count_minima_locations(xd, yd)
        if mins[0] >= 2:
            # two or more local minima found - begin linear regression analysis
            lr = lreg(xd[mins[1][0]:mins[1][-1]], yd[mins[1][0]:mins[1][-1]])
        else:
            # not enough minima found to compute linear regression
            lr = (0,0,0,0,0)
            self.num_one_min += 1

        slope = lr[0]  # currently un-used parameter
        cod = lr[2]**2  # coefficient of determination for linear fit
        isflat = False
        if cod >= self.leemdat.cod_thresh:
            isflat = True
        return (isflat, mins[0])

    @staticmethod
    def count_mins(data):
        num = 0
        locs = []
        sgn = np.sign(data[0])
        for point in data:
            if np.sign(point) != sgn and np.sign(point) == 1:
                num += 1
                locs.append(list(data).index(point))
            sgn = np.sign(point)
        if num >= 2:
            return (num, locs[0], locs[-1])
        else:
            # num min = 0 or 1
            # dummy indicies for location of minima
            return (num,  -1,  -1)

    def check_flat(self, data, thresh=5):
        '''

        :param data: 1d numpy array containing smoothed dI/dE data
        :param thresh: threshold value for
        :return:
        '''

        mins = self.count_mins(data)
        if mins[0] >= 2:
            data_subset = data[mins[1]:mins[2]]
            data_var = np.var(data_subset)
            if data_var <= thresh:
                return 0
            else:
                return mins[0]
        else:
            return mins[0]

    def count_helper(self):
        def_min_e = 0
        def_max_e = 5.1

        # query user to set minimum energy
        min_e, ok = QtGui.QInputDialog.getDouble(self,"Set Minimum Energy", "Input a float value for Min Energy greater or equal to 0.",
                                             0, 0, 10, 1)
        if not ok:
            min_e = def_min_e  # use default if input was canceled

        # query and set max energy
        max_e, ok = QtGui.QInputDialog.getDouble(self,"Set Maximum Energy", "Input a float value for Max Energy less than or equal to 15.",
                                             0, 0, 10, 1)
        if not ok:
            max_e = def_max_e  # use default if input was canceled

        min_index = self.leemdat.elist.index(min_e)
        max_index = self.leemdat.elist.index(max_e)


        self.count_layers_new(data=self.leemdat.dat_3d[:, :, min_index:max_index],
                              ecut=self.leemdat.elist[min_index:max_index])


    def count_layers_new(self, data, ecut):
        '''

        :param data: 3d numpy array of smooth data cut to specific data range
        :param ecut: 1d list of energy values cut to specific data range
        :return none:
        '''

        # calculate the derivative of input data
        diff_data = np.diff(data, axis=2) / np.diff(ecut)

        # smooth the derivative data
        smooth_diff_data = np.apply_along_axis(LF.smooth, 2, diff_data)

        # process pool
        pool = mp.Pool(2*mp.cpu_count())

        # create list of 1-d arrays as input to count_mins()
        ins = [smooth_diff_data[r,c, :] for r in range(data.shape[0])
                                        for c in range(data.shape[1])]
        # list of outputs from check_flat using pool.map()
        outs = pool.map(self.check_flat, ins)

        # convert back to np array and reshape
        outs = np.array(outs).reshape((data.shape[0], data.shape[1]))
        self.discrete_imshow(outs)

    def discrete_imshow(self, data, clrmp=cm.Spectral):
        '''

        :param data: 2d numpy array to be plotted
        :param clrmp: mpl color map
        :return none:
        '''

        max_val = np.max(data)
        min_val = np.min(data)
        cmap_list = [clrmp(i) for i in range(clrmp.N)]
        cmap_list[0] = (0,0,0, 1.0)  # custom 0 value color
        cmap = clrmp.from_list('Custom Colors', cmap_list, clrmp.N)

        bounds = np.linspace(min_val, max_val, (max_val - min_val)+1)
        norm = clrs.BoundaryNorm(bounds, cmap.N)

        self.count_window = QtGui.QWidget()
        self.cfig, self.cplot_ax = plt.subplots(1,1, figsize=(8,8), dpi=100)
        self.ccanvas = FigureCanvas(self.cfig)
        self.ccanvas.setParent(self.count_window)
        self.ccanvas.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Expanding)
        self.cmpl_toolbar = NavigationToolbar(self.ccanvas, self.count_window)

        cvbox = QtGui.QVBoxLayout()
        cvbox.addWidget(self.ccanvas)
        cvbox.addWidget(self.cmpl_toolbar)
        self.count_window.setLayout(cvbox)

        self.cplot_ax.imshow(data, interpolation='none', cmap=cmap)
        ax2 = self.cfig.add_axes([0.95, 0.1, 0.03, 0.8])
        cb = colorbar.ColorbarBase(ax2, cmap=cmap, norm=norm,
        spacing='proportional', ticks=bounds, boundaries=bounds, format='%1i')

        self.count_window.show()



    def old_discrete_imshow(self, data, cmap, title=None):
        """
        Create a color bar with discrete integer values with a scale set
        according to the max/min in your dta set

        courtesy of user2559070 @ stackoverflow.com
        :return none:
        """
        if title is None:
            # do this later
            pass
        self.count_window = QtGui.QWidget()
        self.cfig, self.cplot_ax = plt.subplots(1,1, figsize=(8,8), dpi=100)
        self.ccanvas = FigureCanvas(self.cfig)
        self.ccanvas.setParent(self.count_window)
        self.ccanvas.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Expanding)
        self.cmpl_toolbar = NavigationToolbar(self.ccanvas, self.count_window)

        cvbox = QtGui.QVBoxLayout()
        cvbox.addWidget(self.ccanvas)
        cvbox.addWidget(self.cmpl_toolbar)
        self.count_window.setLayout(cvbox)
        # Make Plot
        colors = cmap(np.linspace(0, 1, np.max(data) - np.min(data) + 1))
        cmap = clrs.ListedColormap(colors)

        img = self.cplot_ax.imshow(data, interpolation='none', cmap=cmap)
        plt.grid(False)
        ticks = np.arange(np.min(data), np.max(data) + 1)
        tickpos = np.linspace(ticks[0]+0.5, ticks[-1]-0.5, len(ticks))
        ax = plt.colorbar(img, ticks=tickpos)
        ax.set_ticklabels(ticks)
        plt.axis('off')
        self.cplot_ax.set_title('LEEM-I(V) Color Coded to # of minima Counted')
        self.count_window.show()



