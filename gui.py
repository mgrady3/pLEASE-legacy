"""
This module contains classes pertinent
to creating the main GUI for the data
analysis suite
Maxwell Grady 2015
"""
# local project imports
import data
import terminal
import LEEMFUNCTIONS as LF
import styles as pls
from config_widget import ConfigWidget
from experiment import Experiment
from ipyembed import embed_ipy
from qthreads import WorkerThread

# stdlib imports
import os
import pprint
import sys
import time
from operator import add, sub

# 3rd-party/scientific stack module imports
import yaml
import matplotlib.cm as cm
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import multiprocessing as mp  # this may be removed as a dependency
import numpy as np
import seaborn as sns
from matplotlib import colorbar
from matplotlib import colors as clrs
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from PyQt4 import QtGui, QtCore
from scipy.stats import linregress as lreg  # this should likely be in another file and not part of GUI


class Viewer(QtGui.QWidget):
    """
    Main GUI construct
    """
    # Config Flags - controlled via class properties
    _Style = True
    _DEBUG = False
    _ERROR = True

    def __init__(self, parent=None):
        """
        Initialize new GUI instance. Setup windows, menus, and UI elements.
        Setup Error Console and all plotting axes.
        :param parent:
            This is a Top-Level Widget ie. parent=None
        :return none:
        """
        super(Viewer, self).__init__(parent)
        self.setWindowTitle("PLEASE: Python Low-energy Electron Analysis SuitE")
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

        if self.Error:
            # re-route sys.stdout to console window
            self.init_Console()

        # final action
        self.setStyleSheet(self.styles['widget'])
        self.show()

    # Setup Class Property Accessor/Setter Methods:
    @property
    def Style(self):
        return self._Style

    @Style.setter
    def Style(self, value):
        self._Style = value

    @property
    def Debug(self):
        return self._DEBUG

    @Debug.setter
    def Debug(self, value):
        self._DEBUG = value

    @property
    def Error(self):
        return self._ERROR

    @Error.setter
    def Error(self, value):
        self.Error = value

    ###########################################################################################
    # Top-Level Initialization Functions
    # These functions simply place calls to second-level init functions in an orderly manner
    # or are brief enough to not need any separate functions
    ###########################################################################################

    def init_UI(self):
        """
        Setup GUI elements
        :return none:
        """
        self.init_Styles()
        self.init_Tabs()
        self.init_Menu()
        self.init_Layout()

    def init_Data(self):
        """
        Setup main data constructs
        Setup plotting flags
        :return none:
        """
        self.exp = None
        self.leeddat = data.LeedData()
        self.leemdat = data.LeemData()
        self.has_loaded_data = False
        self.hasplotted_leem = False
        self.hasplotted_leed = False
        self.hasdisplayed_leed = False
        self.hasdisplayed_leem = False
        self.border_color = (58 / 255., 83 / 255., 155 / 255.)  # unused

        self.current_leed_index = 0  # index of third axis for self.leeddat.dat3d
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
        self.smooth_leem_plot = False
        self.smooth_window_type = 'hanning'  # default value
        self.smooth_window_len = 8  # default value
        self.smooth_file_output = False

        self.background = []
        self.background_curves = []
        self.use_avg = False
        self.last_avg = []

        self.circs = []
        self.leem_IV_list = []
        self.leem_IV_mask = []
        self.click_count = 0
        self.max_leem_click = 7  # Should be kept less than or equal to number of colors minus 1
        self.count_energy_range = ''  # string of energy range used in plot labels

        self.num_one_min = 0
        self.hascountedminima = False

        self.LEEM_rect_enebaled = False
        self.leem_rects = []
        self.leem_rect_count = 0

    def init_Plot_Axes(self):
        """
        Setup embedded matplotlib plotting axes
        :return none:
        """
        # colors
        darker_grey = (43/255., 43/255., 43/255.)  # main widget backgorund color
        lighter_grey = (55/255., 55/255., 55/255.)  # Plot background color

        # Format LEED IV Axis
        self.LEED_IV_ax.set_ylabel('Intensity [arb. units]', fontsize=18)
        self.LEED_IV_ax.set_xlabel('Energy [eV]', fontsize=18)
        self.LEED_IV_ax.set_title("LEED I(V)", fontsize=18)
        if self.Style:
            self.LEED_img_ax.set_title("LEED Image", fontsize=18, color='white')
            self.LEED_IV_ax.set_title("LEED I(V)", fontsize=18, color='white')
            self.LEED_IV_ax.set_ylabel('Intensity [arb. units]', fontsize=18, color='white')
            self.LEED_IV_ax.set_xlabel('Energy [eV]', fontsize=18, color='white')
            self.LEED_IV_ax.tick_params(labelcolor='w', top='off', right='off')
        rect = self.LEED_IV_fig.patch
        if not self.Style:
            rect.set_facecolor((189/255., 195/255., 199/255.))
        else:
            # Old 
            # rect.set_facecolor((68/255., 67/255., 67/255.))
            # New Darker
            # rect.set_facecolor((36/255., 35/255., 35/255.))
            rect.set_facecolor(lighter_grey)


        # Format LEEM IV Axis
        if not self.Style:
            self.LEEM_IV_ax.set_title("LEEM I(V)", fontsize=18)
            self.LEEM_IV_ax.set_ylabel("Intensity (arb. units)", fontsize=18)
            self.LEEM_IV_ax.set_xlabel("Energy (eV)", fontsize=18)
            self.LEEM_IV_ax.tick_params(labelcolor='b', top='off', right='off')
        else:
            self.LEEM_IV_ax.set_title("LEEM I(V)", fontsize=18, color='white')
            self.LEEM_IV_ax.set_ylabel("Intensity (arb. units)", fontsize=18, color='white')
            self.LEEM_IV_ax.set_xlabel("Energy (eV)", fontsize=18, color='white')
            self.LEEM_IV_ax.tick_params(labelcolor='w', top='off', right='off')

        rect = self.LEEM_fig.patch
        # 228, 241, 254
        if not self.style:
            rect.set_facecolor((189/255., 195/255., 199/255.))
        else: 
            # Old 
            # rect.set_facecolor((68/255., 67/255., 67/255.))
            # New Darker
            # rect.set_facecolor((36/255., 35/255., 35/255.))
            rect.set_facecolor(lighter_grey)

        plt.style.use('fivethirtyeight')

    def init_Img_Axes(self):
        """
        Setup embedded matplotlib axes for displaying images
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
        if not self.Style:
            self.LEED_img_ax.set_title('LEED Image: E= 0 eV', fontsize=18)
        else: self.LEED_img_ax.set_title('LEED Image: E= 0 eV', fontsize=18, color='white')

        # Format LEEM Image Axis
        if not self.Style:
            self.LEEM_ax.set_title('LEEM Image: E= 0 eV', fontsize=18)
        else: self.LEEM_ax.set_title('LEEM Image: E= 0 eV', fontsize=18, color='white')

        [self.LEEM_ax.spines[k].set_visible(True) for k in ['top', 'bottom', 'left', 'right']]
        self.LEEM_ax.get_xaxis().set_visible(False)
        self.LEEM_ax.get_yaxis().set_visible(False)

    def init_Console(self):
        """
        Setup floating window with text box to capture Stdout and Stderr
        :return none:
        """
        if self.already_catching_output:
            return
        self.message_console = terminal.ErrorConsole()
        self.message_console.setWindowTitle('Message Console')
        self.message_console.setMinimumWidth(self.max_width/3)
        self.message_console.setMinimumHeight(self.max_height/3)
        self.message_console.move(0, 0)
        self.message_console.setFocus()
        self.message_console.raise_()
        self.already_catching_output = True
        self.pp = pprint.PrettyPrinter(indent=4, stream=self.message_console.stream)
        self.welcome()

    ###########################################################################################
    # Second Level initialization functions
    # These functions do the runt of the UI, image, and plot initialization
    # they sometimes delegate to third level functions in order to keep
    # functions short and ordered
    ###########################################################################################

    def init_Styles(self):
        """
        setup dictionary variable containing QSS style strings
        :return none:
        """
        pstyles = pls.PyLeemStyles()
        self.styles = pstyles.get_styles()  # get_styles() returns a dictionary of key, qss string pairs

    def init_Tabs(self):
        """
        Setup QTabWidgets
        One Tab for LEEM
        One Tab for LEED
        One Tab for Settings/Config
        :return:
        """

        self.tabs = QtGui.QTabWidget()
        self.tabs.setStyleSheet(self.styles['tab'])
        # self.configTabs = QtGui.QTabWidget()
        # self.configTabs.setStyleSheet(self.styles['tab'])

        self.LEED_Tab = QtGui.QWidget()
        self.LEEM_Tab = QtGui.QWidget()
        self.Config_Tab = QtGui.QWidget()
        self.tabs.addTab(self.LEED_Tab, "LEED-IV")
        self.tabs.addTab(self.LEEM_Tab, "LEEM-IV")
        self.tabs.addTab(self.Config_Tab, "CONFIG")

        # self.tabBarHBox.addWidget(self.tabs)
        # self.tabBarHBox.addStretch()
        # self.tabBarHBox.addWidget(self.configTabs)

        # call third-level init functions for each tab individually
        self.init_LEED_Tab()
        self.init_LEEM_Tab()
        self.init_Config_Tab()

    def init_LEED_Tab(self):
        """
        Setup GUI items for LEED analysis
        :return none:
        """
        self.LEED_IV_fig, (self.LEED_img_ax, self.LEED_IV_ax) = plt.subplots(1, 2, figsize=(6,6), dpi=100)
        self.LEED_IV_canvas = FigureCanvas(self.LEED_IV_fig)
        self.LEED_IV_canvas.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                          QtGui.QSizePolicy.Expanding)
        self.LEED_IV_canvas.setParent(self.LEED_Tab)
        self.LEED_IV_toolbar = NavigationToolbar(self.LEED_IV_canvas, self)

        LEED_Tab_Layout_V1 = QtGui.QVBoxLayout()
        LEED_Tab_Layout_H1 = QtGui.QHBoxLayout()
        LEED_Tab_Slider_HBox = QtGui.QHBoxLayout()

        # Slider Layout
        self.LEED_slider = QtGui.QSlider(QtCore.Qt.Horizontal, self.LEED_Tab)
        self.LEED_slider.setMaximumHeight(200)
        self.LEED_slider.setTickInterval(1)
        self.LEED_slider.setTickPosition(QtGui.QSlider.TicksAbove)
        self.LEED_slider.valueChanged[int].connect(self.update_LEED_slider)

        self.LEED_slider_label = QtGui.QLabel(self)
        self.LEED_slider_label.setText("Electron Energy [eV]")

        self.LEED_slider_value = QtGui.QLabel(self)
        self.LEED_slider_value.setText("0 eV")

        LEED_Tab_Slider_HBox.addWidget(self.LEED_slider_label)
        LEED_Tab_Slider_HBox.addWidget(self.LEED_slider)
        LEED_Tab_Slider_HBox.addWidget(self.LEED_slider_value)


        LEED_Tab_Layout_V1.addWidget(self.LEED_IV_canvas)
        # LEED_Tab_Layout_V1.addStretch(1)
        LEED_Tab_Layout_V1.addLayout(LEED_Tab_Slider_HBox)
        LEED_Tab_Layout_V1.addWidget(self.LEED_IV_toolbar)

        self.LEED_Tab.setLayout(LEED_Tab_Layout_V1)
        self.LEED_IV_fig.canvas.mpl_connect('button_release_event', self.LEED_click)

    def init_LEEM_Tab(self):
        """
        Setup GUI items for LEEM analysis
        :return none:
        """
        self.LEEM_fig, (self.LEEM_ax, self.LEEM_IV_ax) = plt.subplots(1, 2, figsize=(6,6), dpi=100)
        self.LEEM_canvas = FigureCanvas(self.LEEM_fig)
        self.LEEM_canvas.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Expanding)
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
        self.LEEM_click_handler = self.LEEM_fig.canvas.mpl_connect('button_release_event', self.leem_click)

    def init_Config_Tab(self):
        """
        Setup GUI items for CONFIG and SETTINGS
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

        self.toggle_debug = QtGui.QPushButton('Toggle Debug', self)
        self.toggle_debug.clicked.connect(self.toggle_debug_setting)

        self.swap_byte_order_LEED = QtGui.QPushButton('Swap LEED Bytes', self)
        self.swap_byte_order_LEED.clicked.connect(lambda: self.swap_byte_order(dat='LEED'))

        self.swap_byte_order_LEEM = QtGui.QPushButton('Swap LEEM Bytes', self)
        self.swap_byte_order_LEEM.clicked.connect(lambda: self.swap_byte_order(dat='LEEM'))

        buts = [self.set_energy__leem_but, self.set_energy__leed_but, self.toggle_debug,
                self.swap_byte_order_LEED, self.swap_byte_order_LEEM]

        config_Tab_group_button_box.addStretch(1)
        for b in buts:
            config_Tab_group_button_box.addWidget(b)
            config_Tab_group_button_box.addStretch(1)
        # config_Tab_groupbox.setStyleSheet(self.styles['group'])
        config_Tab_groupbox.setLayout(config_Tab_group_button_box)

        config_Tab_Vbox.addWidget(config_Tab_groupbox)
        config_Tab_Vbox.addStretch(1)
        config_Tab_bottom_button_Hbox.addStretch(1)
        config_Tab_bottom_button_Hbox.addWidget(self.quitbut)
        config_Tab_Vbox.addLayout(config_Tab_bottom_button_Hbox)
        self.Config_Tab.setLayout(config_Tab_Vbox)

    def init_Menu(self):
        """
        Setup Menu bar at top of main window
        :return none:
        """
        if sys.platform == 'darwin':
            QtGui.qt_mac_set_native_menubar(False)

        self.menubar = QtGui.QMenuBar()
        self.menubar.setStyleSheet(self.styles['menu'])

        # TODO: Reorganize all menu shortcuts
        # File Menu
        fileMenu = self.menubar.addMenu('File')

        genDatFileAction = QtGui.QAction('Generate Dat Files', self)
        genDatFileAction.triggered.connect(self.gen_dat_files_from_images)
        fileMenu.addAction(genDatFileAction)


        loadExperimentAction = QtGui.QAction('Load Experiment', self)
        loadExperimentAction.setShortcut('Ctrl+X')
        loadExperimentAction.triggered.connect(self.load_experiment)
        fileMenu.addAction(loadExperimentAction)


        outputLEEMAction = QtGui.QAction('Output LEEM to Text', self)
        outputLEEMAction.setShortcut('Ctrl+O')
        outputLEEMAction.triggered.connect(lambda: self.output_to_text(data='LEEM', smth=self.smooth_file_output))
        fileMenu.addAction(outputLEEMAction)

        outputLEEDAction = QtGui.QAction('Output LEED to Text', self)
        outputLEEDAction.setShortcut('Ctrl+Shift+O')
        outputLEEDAction.triggered.connect(lambda: self.output_LEED_to_Text(data=None, smth=self.smooth_file_output))
        fileMenu.addAction(outputLEEDAction)

        genConfigAction = QtGui.QAction("Generate Experiment Config File", self)
        genConfigAction.triggered.connect(self.gen_config_file)
        fileMenu.addAction(genConfigAction)

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
        extractAction.triggered.connect(self.plot_LEED_IV)
        LEEDMenu.addAction(extractAction)

        new_extractAction = QtGui.QAction('New Extract I(V)', self)
        new_extractAction.setShortcut('Ctrl+Shift+E')
        new_extractAction.setStatusTip('New Extract I(V) from current selections')
        new_extractAction.triggered.connect(self.new_leed_extract)
        LEEDMenu.addAction(new_extractAction)

        # Add submenu for background subtraction tasks
        backgroundMenu = LEEDMenu.addMenu('Background Subtraction')


        subtractAction = QtGui.QAction('Subtract Background', self)
        subtractAction.setShortcut('Ctrl+B')
        subtractAction.triggered.connect(self.subtract_background)
        backgroundMenu.addAction(subtractAction)

        selectBackgroundAction = QtGui.QAction('Select Background I(V)', self)
        selectBackgroundAction.triggered.connect(self.get_background_from_selections)
        backgroundMenu.addAction(selectBackgroundAction)

        displayBackgroundAction = QtGui.QAction('Display Background I(V)', self)
        displayBackgroundAction.triggered.connect(self.show_calculated_background)
        backgroundMenu.addAction(displayBackgroundAction)

        subtractStoredBackgroundAction = QtGui.QAction('Subtract Stored Background', self)
        subtractStoredBackgroundAction.triggered.connect(self.subtract_stored_background)
        backgroundMenu.addAction(subtractStoredBackgroundAction)

        # Add submenu for functiosn related to averaging I(V)
        averageMenu = LEEDMenu.addMenu('Averaging')

        averageAction = QtGui.QAction('Average I(V)', self)
        averageAction.setShortcut('Ctrl+A')
        averageAction.setStatusTip('Average currently selected I(V) curves')
        averageAction.triggered.connect(self.average_current_IV)
        averageMenu.addAction(averageAction)

        outputAverageAction = QtGui.QAction('Output Average I(V)', self)
        outputAverageAction.triggered.connect(self.output_average_LEED)
        averageMenu.addAction(outputAverageAction)

        """
        shiftAction = QtGui.QAction('Shift Selecttions', self)
        shiftAction.setShortcut('Ctrl+S')
        shiftAction.setStatusTip('Shift User Selections based on Beam Maximum')
        shiftAction.triggered.connect(self.shift_user_selection)
        LEEDMenu.addAction(shiftAction)
        """
        changeAction = QtGui.QAction('Change LEED Image by Energy', self)
        changeAction.setShortcut('Ctrl+G')
        changeAction.triggered.connect(self.show_LEED_image_by_energy)
        LEEDMenu.addAction(changeAction)

        clearAction = QtGui.QAction('Clear Current I(V)', self)
        clearAction.setShortcut('Ctrl+C')
        clearAction.setStatusTip('Clear Current Selected I(V)')
        clearAction.triggered.connect(self.clear_LEED_click)
        LEEDMenu.addAction(clearAction)

        clearPlotsOnlyAction = QtGui.QAction('Clear Plots', self)
        clearPlotsOnlyAction.setShortcut('Ctrl+Alt+C')
        clearPlotsOnlyAction.setStatusTip('Clear Current Plots')
        clearPlotsOnlyAction.triggered.connect(self.clear_LEED_plots_only)
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

        derivativeMenu = LEEMMenu.addMenu("Derivative")
        leemdIdVAction = QtGui.QAction("Plot dI/dV", self)
        leemdIdVAction.triggered.connect(self.plot_derivative)
        derivativeMenu.addAction(leemdIdVAction)

        countAction = QtGui.QAction('Count Layers', self)
        countAction.setShortcut('Meta+L')
        countAction.triggered.connect(self.count_helper)
        LEEMMenu.addAction(countAction)

        rectAction = QtGui.QAction("Select Rectangle", self)
        rectAction.setShortcut('Meta+R')
        rectAction.triggered.connect(self.LEEM_rectangular_selection)
        LEEMMenu.addAction(rectAction)

        # Settings Menu
        settingsMenu = self.menubar.addMenu('Settings')
        smoothAction = QtGui.QAction('Toggle Data Smoothing', self)
        smoothAction.setShortcut('Ctrl+Shift+S')
        smoothAction.setStatusTip('Turn on/off Data Smoothing')
        smoothAction.triggered.connect(self.toggle_smoothing)
        settingsMenu.addAction(smoothAction)

        setLEEMEnergyAction = QtGui.QAction('Set Energy Parameters', self)
        #setLEEMEnergyAction.setShortcut('Ctrl+Shift+E')
        setLEEMEnergyAction.triggered.connect(lambda: self.set_energy_parameters(dat='LEEM'))
        settingsMenu.addAction(setLEEMEnergyAction)

        boxAction = QtGui.QAction('Set Integration Window', self)
        boxAction.setShortcut('Ctrl+Shift+B')
        boxAction.setStatusTip('Set Integration Window Radius')
        boxAction.triggered.connect(self.set_integration_window)
        settingsMenu.addAction(boxAction)

        setLEEDEnergyAction = QtGui.QAction('Set LEED Energy Parameters', self)
        #setLEEDEnergyAction.setShortcut('Ctrl+Shift+N')
        setLEEDEnergyAction.triggered.connect(lambda: self.set_energy_parameters(dat='LEED'))
        settingsMenu.addAction(setLEEDEnergyAction)

        debugConsoleAction = QtGui.QAction('IPython', self)
        debugConsoleAction.triggered.connect(self.debug_console)
        settingsMenu.addAction(debugConsoleAction)

        # testButtonsAction = QtGui.QAction('Test Buttons', self)
        # testButtonsAction.triggered.connect(self.test_buttons)
        # settingsMenu.addAction(testButtonsAction)

    def init_Layout(self):
        """
        Setup layout of main Window usig Hbox and VBox
        :return none:
        """

        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(self.menubar)
        vbox1.addWidget(self.tabs)
        # vbox1.addLayout(self.tabBarHBox)
        self.setLayout(vbox1)

    def closeEvent(self, *args):
        """
        Override closeEvent() to call quit()
        If main window is closed - app will Quit instead of leaving the console open
        with the main window closed
        :param args:
            receive a close event from main QWidget along with any additional args.
        :return none:
        """
        self.Quit()

    def debug_console(self):
        """
        Open a new window with an embedded IPython REPL
        Some local variables will be passed into the namespace of
        the IPython kernel
        :return none:
        """
        print("Starting an IPython Session ... ")
        self.ipyconsole = QtGui.QWidget()
        self.ipyconsole.show()
        test_pass = {"leemdat": self.leemdat}

        # dict of vars to pass into namespace of the IPython kernel
        pass_through_vars = {}

        # fill variables to pass in a logical manner
        if self.hasdisplayed_leed:
            pass_through_vars["leeddat"] = self.leeddat
        if self.hasdisplayed_leem:
            pass_through_vars["leemdat"] = self.leemdat

        # CAUTION, Here be Dragons ...
        # pass_through_vars["main_gui"] = self     ##### DON'T DO THIS ####

        # matplotlib.pyplot may recursively start showing previous plots Inception style ...

        embed_ipy(self.ipyconsole, passthrough=pass_through_vars)
        return

    ###########################################################################################
    # Static Methods
    ###########################################################################################

    @staticmethod
    def welcome():
        """
        Called once on app open
        :return none:
        """
        print("Welcome to the Python Low-energy Electron Analyis SuitE: PLEASE")
        print("Author: Maxwell Grady - University of New Hampshire")
        print("Licensed under GPLv3")
        print("Visit http://www.github.com/mgrady3/pLEASE/ for more details.")
        print("#" * 63)
        print()
        print("Begin by loading a LEED or LEEM data set")

        return

    @staticmethod
    def Quit():
        """
        Exit program via Qt protocols instead of sys.exit()
        :return none:
        """
        print('Exiting ...')
        QtCore.QCoreApplication.instance().quit()
        return

    # This could be moved to LEEMFUNCTIONS.py
    @staticmethod
    def count_mins(data):
        """
        :return tuple:
        """
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
            return (num, -1, -1)

    @staticmethod
    def output_complete():
        """
        This function executes when receiving a finished() SIGNAL from a QThread object
        :return: none
        """
        # signals QThread has emitted a 'finished()' SIGNAL
        print('File output successfully')
        return


    """
    def test_buttons(self):

        self.new_widget= QtGui.QWidget()
        self.new_widget.setWindowTitle("Select Data Type")
        layout = QtGui.QVBoxLayout()
        option1 = QtGui.QCheckBox("Raw Data", self)
        option2 = QtGui.QCheckBox("Image Data", self)
        okbutton = QtGui.QPushButton("Ok", self)
        oklayout = QtGui.QHBoxLayout()
        oklayout.addStretch(1)
        oklayout.addWidget(okbutton)
        okbutton.clicked.connect(self.new_widget.close)

        layout.addWidget(option1)
        layout.addWidget(option2)
        layout.addLayout(oklayout)

        option1.stateChanged.connect(lambda: print("Option1 state changed to {}".format(option1.checkState())))
        option2.stateChanged.connect(lambda: print("Option2 state changed to {}".format(option2.checkState())))
        self.new_widget.setLayout(layout)
        self.new_widget.show()
    """

    def gen_dat_files_from_images(self):
        """
        Query user for directory containing image files and a directory to output data to
        Process each image, strip out header info, and write as raw data to file from numpy array
        :return:
        """

        # LEEMFUNCTIONS.gen_dat_files() requires:
        # input directory, output directory, filetype, image width, image height, image byte depth

        # Query User for directory containing image files
        infiledir = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory Containing \
                                                                     Image Files to Process"))
        # Query User for directory to output .dat files to
        outfiledir = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory to Output DAT files to"))

        # Query User for file type (TIFF, PNG)
        items = ["TIFF: .tif/.tiff", "PNG: .png"]
        extension, ok = QtGui.QInputDialog.getItem(self, "Select Image File Type", "Valid File Types:",
                                                   items, current=0, editable=False)
        if not ok:
            return

        if extension is not None:
            if extension.startswith("TIFF"):
                # Handle TIFF Files
                # print("TIFF")
                extension = '.tif'
            elif extension.startswith("PNG"):
                # Handle PNG files
                # print("PNG")
                extension = '.png'
        else:
            print("Error: invalid extension")
            return

        # Query User for Image Parameters: Ask to parse from YAML or input manually
        items = ["Manual Entry", "Parse Experiment YAML"]
        choice, ok = QtGui.QInputDialog.getItem(self, "Select Method to Input Image Parameters",
                                                "Manual or Parse from YAML", items, current=0, editable=False)
        if not ok:
            return
        print(choice)
        if choice == "Manual Entry":
            #
            width, ok = QtGui.QInputDialog.getInt(self, "Enter Image Width", "Image Width >= 2", value=2, min=2)
            if not ok:
                return

            height, ok = QtGui.QInputDialog.getInt(self, "Enter Image Height", "Image Height >= 2", value=2, min=2)
            if not ok:
                return

            items = ["1", "2"]
            depth, ok = QtGui.QInputDialog.getItem(self, "Select Image Byte Depth",
                                                   "Byte Depth: 1 (8bit) or 2 (16bit)", items, current=1, editable=False)
            depth = int(depth)  # cast string "1" or "2" to int
            if not ok:
                return

        elif choice == "Parse Experiment YAML":

            # Query User for directory containing Experiment YAML Config file
            filedir = str(QtGui.QFileDialog.getExistingDirectory(self, "Select directory containing Experiment YAML file"))
            files = [name for name in os.listdir(filedir) if name.endswith('.yaml') or name.endswith('.YAML')]
            if files:
                print("Found Experiment YAML file: {0}, Parsing Image Paramters from YAML".format(files[0]))
                exp = Experiment()
                exp.fromFile(os.path.join(filedir, files[0]))
                try:
                    width = exp.imw
                    height = exp.imh
                    bits = exp.bit
                    if bits == 16:
                        depth = 2
                    elif bits == 8:
                        depth = 1
                    else:
                        print("Error: Unknown image bit depth in YAML file {0}".format(os.path.join(filedir, files[0])))
                        return
                except AttributeError as e:
                    print("Error: Loaded Experiment does not contain appropriate Image Parameters ...")
                    return

                # TODO: put this into a separate QThread so as to not block the main UI for 10-30 seconds
                # call gen_dat_files with user entries
                LF.gen_dat_files(dirname=infiledir, outdirname=outfiledir, ext=extension,
                                 w=width, h=height, byte_depth=depth)

            else:
                print("No YAML file found in directory: {0}".format(filedir))
                return

            return
        else:
            print("Error: Unable to parse user selection")
            return

        # TODO: put this into a separate QThread so as to not block the main UI for 10-30 seconds
        # call gen_dat_files with user entries
        LF.gen_dat_files(dirname=infiledir, outdirname=outfiledir, ext=extension,
                         w=width, h=height, byte_depth=depth)



    ###########################################################################################
    # New Methods for loading Generic Experiments
    # All Necessary Parameters are loaded from YAML configuration file
    # Merged into master: 4/19/16
    ###########################################################################################

    def gen_config_file(self):
        """

        :return:
        """
        self.cw = ConfigWidget()
        self.connect(self.cw, QtCore.SIGNAL('output(PyQt_PyObject)'), self.retrieve_config_settings)
        self.connect(self.cw, QtCore.SIGNAL('close'), self.output_config)


    def retrieve_config_settings(self, settings):
        self.config_settings = settings

    def output_config(self):
        if self.config_settings:
            print("Outputting config settings to file  ...")

            tab = "    "  # translate '\t' = 4 spaces

            # Required params
            ddir = self.config_settings["Data Dir"]
            out_dir = self.config_settings["Output Dir"]
            file_name = self.config_settings["Output File Name"]
            exp_type = self.config_settings["Exp Type"]
            data_type = self.config_settings["Data Type"]
            im_wd = self.config_settings["Width"]
            im_ht = self.config_settings["Height"]
            min_energy = self.config_settings["Min Energy"]
            max_energy = self.config_settings["Max Energy"]
            step_energy = self.config_settings["Step Energy"]

            # Additional params
            if data_type == 'Image':
                image_type = self.config_settings["Image Type"]
                if image_type == 'TIFF':
                    file_ext = '.tiff'
                elif image_type == 'PNG':
                    file_ext = '.png'
                else:
                    print("Error: Unknown Image Type - Can't set file extension")
                    return
            elif data_type == 'Raw':
                file_ext = '.dat'
                bit_size = self.config_settings["Bits"]
                byte_order = self.config_settings["Byte Order"]
                if byte_order == "Big-Endian (Motorola)":
                    byte_order = 'B'
                else:
                    byte_order = 'L'

            else:
                print("Error: Unknown Data Type - Can't set file extension")
                return

            with open(os.path.join(out_dir, file_name), 'w') as f:
                f.write("Experiment:\n")
                f.write("# Required Parameters\n")
                f.write(tab + "Type:  {0}\n".format("\"" + exp_type + "\""))
                f.write(tab + "Name:  {0}\n".format("\"" + file_name + "\""))
                f.write(tab + "Data Type:  {0}\n".format("\"" + data_type + "\""))
                f.write(tab + "File Format:  {0}\n".format("\"" + file_ext + "\""))
                f.write(tab + "Image Parameters:\n")
                f.write(tab + tab + "Height:  {0}\n".format(str(im_ht)))
                f.write(tab + tab + "Width:  {0}\n".format(str(im_wd)))
                f.write(tab + "Energy Parameters:\n")
                f.write(tab + tab + "Min:  {0}\n".format(str(min_energy)))
                f.write(tab + tab + "Max:  {0}\n".format(str(max_energy)))
                f.write(tab + tab + "Step:  {0}\n".format(str(step_energy)))
                f.write(tab + "Data Path:  \"{0}\"\n".format(str(ddir)))
                f.write("\n")
                f.write("# Additional Parameters\n")
                if data_type == "Raw":
                    f.write(tab + "Bit Size:  {0}\n".format(str(bit_size)))
                    f.write(tab + "Byte Order:  {0}".format(str(byte_order)))
            print("Experiment YAML config file written to {0}".format(str(os.path.join(ddir, file_name))))


    def generate_config(self):
        """
        Query User for experiment settings
        Write settings to a YAML config file with .yaml extension
        This file can then be loaded via load_experiment() to
        load data into one of the main data constructs
        :return none:
        """
        # get path to data
        ddir = QtGui.QFileDialog.getExistingDirectory(self, "Select Data Directory")  # note this is a QString

        if ddir == '':
            # Error Loading Data
            print('Error Selecting Data Directory ...')
            return

        # get name for config file
        msg = """Please enter a name for the experiment config file.
        Do not include a file extension, one will be added automatically"""
        entry, ok = QtGui.QInputDialog.getText(self, "Enter name for experiment config file", msg)
        if not ok:
            print("Error getting file name ...")
            return
        file_name = str(entry) + '.yaml'

        # get experiment type (LEEM or LEED)
        msg="""Please enter experiment type: LEEM or LEED."""
        entry, ok = QtGui.QInputDialog.getText(self, "Enter experiment type", msg)
        if not ok:
            print("Error getting experiment type ...")
            return
        if entry not in ['LEEM', 'LEED', 'leem', 'leed']:
            print("Error getting experiment type ...")
            return
        exp_type = str(entry).upper()

        # get data type (Raw or Image)
        msg = """Please enter data type: Raw or Image."""
        entry, ok = QtGui.QInputDialog.getText(self, "Enter data type", msg)
        if not ok:
            print("Error getting data type ...")
            return
        if entry not in ["Raw", "Image", "raw", "image"]:
            print("Error getting data type ...")
            return
        if str(entry).startswith('R') or str(entry).startswith('r'):
            data_type = "Raw"
        else:
            data_type = "Image"

        # get file extension
        if data_type == "Raw":
            file_ext = '.dat'
        else:
            msg = """Please image file extension with no leading dot.
            Valid extensions are tif and png"""
            entry, ok = QtGui.QInputDialog.getText(self, "Enter file extension", msg)
            if not ok:
                print("Error getting file extension ...")
                return
            if str(entry).startswith('.'):
                file_ext = str(entry).split('.')[1]
            else:
                file_ext = str(entry)
            if file_ext not in ['tiff', 'TIFF', 'tif', 'TIF', 'png', 'PNG']:
                print("Error invalid file extension. Valid choices are tif and png")
                return
            elif file_ext in ['tiff', 'TIFF', 'tif', 'TIF']:
                file_ext = '.tif'
            elif file_ext in ['png', 'PNG']:
                file_ext = '.png'

        # get Image parameters
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
            print("Generation of Config File canceled ...")
            return
        else:
            im_ht = entry

        id = QtGui.QInputDialog(self)
        id.setInputMode(QtGui.QInputDialog.IntInput)
        id.setLabelText("Enter Positive Integer >= 2")
        id.setWindowTitle("Enter Image width in Pixels")
        id.setIntMinimum(2)
        id.setIntMaximum(10000)
        id.resize(400, 300)
        ok = id.exec_()
        entry = id.intValue()

        if not ok:
            print("Generation of Config File canceled ...")
            return
        else:
            im_wd = entry

        # Get starting energy in eV
        entry, ok = QtGui.QInputDialog.getDouble(self, "Enter Starting Energy in eV",
                                                     "Enter a decimal for Starting Energy in eV",
                                                     value=20.5, min=-500, max=5000)
        if not ok:
            print("Generation of Config File canceled ...")
            return
        min_energy = float(entry)

        # Get Final Energy in eV
        entry, ok = QtGui.QInputDialog.getDouble(self, "Enter Final Energy in eV (must be larger than Start Energy)",
                                                 "Enter a decimal for Final Energy > Start Energy",
                                                 value=150, min=-500, max=5000)
        if not ok:
            print("Generation of Config File canceled ...")
            return

        max_energy = float(entry)
        if max_energy <= min_energy:
            print('Error: Final Energy must be larger than Starting Energy')
            return

        # Get Energy Step in eV
        entry, ok = QtGui.QInputDialog.getDouble(self, "Enter Energy Step in eV",
                                                 "Enter a decimal for Energy Step >0.0",
                                                 value=0.5, min=0.000001, max=500)
        if not ok:
            print('New Energy settings canceled ...')
            return
        step_energy = float(entry)

        # get bit size if data_type is "Raw"
        if data_type == "Raw":
            id = QtGui.QInputDialog(self)
            id.setInputMode(QtGui.QInputDialog.IntInput)
            id.setLabelText("Enter Positive Integer >= 2")
            id.setWindowTitle("Enter Bit Size as integer: default 16bit.")
            id.setIntMinimum(2)
            id.setIntMaximum(64)
            id.resize(400, 300)
            ok = id.exec_()
            entry = id.intValue()
            if not ok:
                print("Error getting bit size ...")
                return
            bit_size = entry

            msg = """Please Enter Byte Order: Little (Intel) or Big (Motorola) Endian.
                Default to Little if you are unsure"""
            entry, ok = QtGui.QInputDialog.getText(self, "Enter Byte Order: Little or Big", msg)
            if not ok:
                print("Error getting byte order ...")
                return
            if str(entry).lower().startswith('l'):
                byte_order = 'L'
            elif str(entry).lower().startswith('b'):
                byte_order = 'B'
            else:
                print("Error getting byte order ...")
                print("Valid entries are Little or Big")
                return

        tab = "    "  # translate '\t' = 4 spaces

        # write user input to file using correct formatting for each line

        with open(os.path.join(ddir, file_name), 'w') as f:
            f.write("Experiment:\n")
            f.write("# Required Parameters\n")
            f.write(tab+"Type:  {0}\n".format("\""+exp_type+"\""))
            f.write(tab+"Name:  {0}\n".format("\""+file_name+"\""))
            f.write(tab+"Data Type:  {0}\n".format("\""+data_type+"\""))
            f.write(tab+"File Format:  {0}\n".format("\""+file_ext+"\""))
            f.write(tab+"Image Parameters:\n")
            f.write(tab+tab+"Height:  {0}\n".format(str(im_ht)))
            f.write(tab+tab+"Width:  {0}\n".format(str(im_wd)))
            f.write(tab+"Energy Parameters:\n")
            f.write(tab+tab+"Min:  {0}\n".format(str(min_energy)))
            f.write(tab+tab+"Max:  {0}\n".format(str(max_energy)))
            f.write(tab+tab+"Step:  {0}\n".format(str(step_energy)))
            f.write(tab+"Data Path:  \"{0}\"\n".format(str(ddir)))
            f.write("\n")
            f.write("# Additional Parameters\n")
            if data_type == "Raw":
                f.write(tab+"Bit Size:  {0}\n".format(str(bit_size)))
                f.write(tab+"Byte Order:  {0}".format(str(byte_order)))
        print("Experiment YAML config file written to {0}".format(str(os.path.join(ddir, file_name))))

    def load_experiment(self):
        """
        :return none
        """
        # On Windows 10 there seems to be an error where files are not displayed in the FileDialog
        # The user may select a directory they know to contain a .yaml file but no files are shown
        # one possible work around may be to use options=QtGui.QFileDialog.DontUseNativeDialog
        # but this changes the entire look and feel of the window. Thus is not an ideal solution

        # Old way:
        # new_dir = str(QtGui.QFileDialog.getExistingDirectory(self, "Select directory containing Experiment Config File"))
        # if new_dir == '':
        #                print('Loading Canceled ...')
        #                return
        # get .yaml file from selected dir
        # files = [name for name in os.listdir(new_dir) if (name.endswith('.yaml') or name.endswith('.yml'))]
        # if files:
        #    config = files[0]
        # else:
        #    print('No Config file found. Please Select a directory with a .yaml file')
        #    print('Loading Canceled ...')
        #    return

        # New way:
        yamlFilter = "YAML (*.yaml);;YML (*.yml);;All Files (*)"
        homeDir = os.getenv("HOME")
        fileName = QtGui.QFileDialog.getOpenFileName(parent=None,
                                                    caption="Select YAML Experiment Config File",
                                                    directory=homeDir,
                                                    filter=yamlFilter)
        if fileName:
            config = fileName  # string path to .yaml or .yml config file
        else:
            print('No Config file found. Please Select a directory with a .yaml file')
            print('Loading Canceled ...')
            return

        if self.exp is not None:
            # already loaded an experiment; save old experiment then load new
            self.prev_exp = self.exp

        self.exp = Experiment()
        # path_to_config = os.path.join(new_dir, config)
        self.exp.fromFile(config)
        print("New Data Path loaded from file: {}".format(self.exp.path))
        print("Loaded the following settings:")
        yaml.dump(self.exp.loaded_settings, stream=self.message_console.stream)
        # self.pp.pprint(exp.loaded_settings)

        if self.exp.exp_type == 'LEEM':
            self.load_LEEM_experiment()

        elif self.exp.exp_type == 'LEED':
            self.load_LEED_experiment()
        else:
            print("Error: Unrecognized Experiment Type in YAML Config file")
            print("Valid Experiment Types are LEEM or LEED")
            print("Please refer to Experiment.yaml for documentation on valid YAML config files")
            return

    def load_LEEM_experiment(self):
        """
        :return:
        """
        if self.exp is None:
            return
        if self.hasplotted_leem:
            # if curves already displayed, just clear the IV plots
            # reset any plotting variables
            self.clear_LEEM_IV()
        self.LEEM_ax.clear()
        self.LEEM_IV_ax.clear()
        # Make sure labels are correctly redrawn
        if self.Style:
            self.LEEM_IV_ax.set_title("LEEM I(V)", fontsize=18, color='white')
            self.LEEM_IV_ax.set_ylabel("Intensity (arb. units)", fontsize=18, color='white')
            self.LEEM_IV_ax.set_xlabel("Energy (eV)", fontsize=18, color='white')
            self.LEEM_IV_ax.tick_params(labelcolor='w', top='off', right='off')
            self.LEEM_ax.set_title("LEEM Image", fontsize=18, color='white')
        else:
            self.LEEM_IV_ax.set_title("LEEM I(V)", fontsize=18)
            self.LEEM_IV_ax.set_ylabel("Intensity (arb. units)", fontsize=18)
            self.LEEM_IV_ax.set_xlabel("Energy (eV)", fontsize=18)
            self.LEEM_IV_ax.tick_params(top='off', right='off')
            self.LEEM_ax.set_title("LEEM Image", fontsize=18)


        self.leemdat.data_dir = str(self.exp.path)  # manually cast from QString to String
        self.leemdat.img_mask_count_dir = os.path.join(self.exp.path, 'img_mask_count')
        self.leemdat.ht = self.exp.imh
        self.leemdat.wd = self.exp.imw

        # Shift focus to LEEM tab when loading LEEM data
        self.tabs.setCurrentWidget(self.LEEM_Tab)
        # self.LEEM_Tab.show()


        # if self.exp.data_type == 'Raw' or self.exp.data_type == 'raw' or self.exp.data_type == 'RAW':
        if self.exp.data_type.lower() == 'raw':

            try:
                self.thread = WorkerThread(task='LOAD_LEEM',
                                           path=self.leemdat.data_dir,
                                           imht=self.leemdat.ht,
                                           imwd=self.leemdat.wd,
                                           bits=self.exp.bit,
                                           byte=self.exp.byte_order)
                # disconnect any previously connected Signals/Slots
                self.disconnect(self.thread, QtCore.SIGNAL('output(PyQt_PyObject)'), self.retrieve_LEEM_data)
                self.disconnect(self.thread, QtCore.SIGNAL('finished()'), self.update_LEEM_img)
                # connect appropriate signals for loading LEED data
                self.connect(self.thread, QtCore.SIGNAL('output(PyQt_PyObject)'), self.retrieve_LEEM_data)
                self.connect(self.thread, QtCore.SIGNAL('finished()'), self.update_LEEM_img)
                self.thread.start()

                #self.leemdat.dat_3d = LF.process_LEEM_Data(self.leemdat.data_dir,
                #                                           self.leemdat.ht,
                #                                           self.leemdat.wd)
            except ValueError:
                print('Error Loading LEEM Experiment: Please Recheck YAML Settings')
                # print('Resetting data directory to previous setting, {}'.format(prev_ddir))
                return

        # elif self.exp.data_type == 'Image' or self.exp.data_type == 'image' or self.exp.data_type == 'IMAGE':
        elif self.exp.data_type.lower() == 'image':
            try:
                self.thread = WorkerThread(task='LOAD_LEEM_IMAGES',
                                           path=self.exp.path,
                                           ext=self.exp.ext)
                # disconnect any previously connected Signals/Slots
                self.disconnect(self.thread, QtCore.SIGNAL('output(PyQt_PyObject)'), self.retrieve_LEEM_data)
                self.disconnect(self.thread, QtCore.SIGNAL('finished()'), self.update_LEEM_img)
                # connect appropriate signals for loading LEED data
                self.connect(self.thread, QtCore.SIGNAL('output(PyQt_PyObject)'), self.retrieve_LEEM_data)
                self.connect(self.thread, QtCore.SIGNAL('finished()'), self.update_LEEM_img)
                self.thread.start()
            except ValueError:
                print('Error loading LEEM data from images. Please check YAML experiment config file')
                print('Required parameters to load images from YAML config: path, ext')
                print('Check for valid data path and valid file extensions: \'.tif\' and \'.png\'.')

    def load_LEED_experiment(self):
        """
        :return:
        """
        if self.exp is None:
            return

        if self.hasdisplayed_leed:
            self.clear_LEED_click()
            self.clear_LEED_plots_only()

        self.LEED_IV_ax.clear()
        self.LEED_img_ax.clear()
        self.leeddat.data_dir = self.exp.path
        self.leeddat.ht = self.exp.imh
        self.leeddat.wd = self.exp.imw

        # Shift focus to LEED tab when loading LEED data
        self.tabs.setCurrentWidget(self.LEED_Tab)
        # self.LEED_Tab.show()

        if self.exp.data_type.lower() == 'raw':
            try:
                self.thread = WorkerThread(task='LOAD_LEED',
                                           path=self.leeddat.data_dir,
                                           imht=self.leeddat.ht,
                                           imwd=self.leeddat.wd,
                                           bits=self.exp.bit,
                                           byte=self.exp.byte_order)

                # disconnect any previously connected Signals/Slots
                self.disconnect(self.thread, QtCore.SIGNAL('output(PyQt_PyObject)'), self.retrieve_LEED_data)
                self.disconnect(self.thread, QtCore.SIGNAL('finished()'), self.update_LEED_img)
                # connect appropriate signals for loading LEED data
                self.connect(self.thread, QtCore.SIGNAL('output(PyQt_PyObject)'), self.retrieve_LEED_data)
                self.connect(self.thread, QtCore.SIGNAL('finished()'), lambda: self.update_LEED_img(index=self.current_leed_index))
                self.thread.start()

            except ValueError:
                print('Error Loading LEED Experiment: Please Recheck YAML Settings')
                return

        elif self.exp.data_type.lower() == 'image':
            try:
                self.thread = WorkerThread(task='LOAD_LEED_IMAGES',
                                           ext=self.exp.ext,
                                           path=self.exp.path, byte=self.exp.byte_order)
                self.disconnect(self.thread, QtCore.SIGNAL('output(PyQt_PyObject)'), self.retrieve_LEED_data)
                self.disconnect(self.thread, QtCore.SIGNAL('finished()'), self.update_LEED_img)
                # connect appropriate signals for loading LEED data
                self.connect(self.thread, QtCore.SIGNAL('output(PyQt_PyObject)'), self.retrieve_LEED_data)
                self.connect(self.thread, QtCore.SIGNAL('finished()'),
                             lambda: self.update_LEED_img(index=self.current_leed_index))
                self.thread.start()
            except ValueError:
                print('Error Loading LEED Experiment from image files.')
                print('Please Check YAML settings in experiment config file')
                print('Required parameters: data path and data extension.')
                print('Valid data extenstions: \'.tif\', \'.png\', \'.jpg\'')
        # Ensure labels are redrawn correctly
        self.LEED_IV_ax.set_ylabel('Intensity [arb. units]', fontsize=18)
        self.LEED_IV_ax.set_xlabel('Energy [eV]', fontsize=18)
        self.LEED_IV_ax.set_title("LEED I(V)", fontsize=18)
        self.LEED_img_ax.set_title("LEED Image", fontsize=18)
        if self.Style:
            self.LEED_img_ax.set_title("LEED Image", fontsize=18, color='white')
            self.LEED_IV_ax.set_title("LEED I(V)", fontsize=18, color='white')
            self.LEED_IV_ax.set_ylabel('Intensity [arb. units]', fontsize=18, color='white')
            self.LEED_IV_ax.set_xlabel('Energy [eV]', fontsize=18, color='white')
            self.LEED_IV_ax.tick_params(labelcolor='w', top='off', right='off')
        # Ensure LEED Slider is updated to fit self.leeddat.dat3d
        self.format_LEED_slider()

    ###########################################################################################
    # Core Functionality:
    # LEED Functions and Processes
    ###########################################################################################

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
                if entry in ['TIFF', 'tiff', 'TIF', 'tif']:
                    new_dir = str(QtGui.QFileDialog.getExistingDirectory(self, "Select directory containing TIFF files"))
                    if new_dir == '':
                        print('Loading Canceled ...')
                        return
                    print('New Data Directory set to {}'.format(new_dir))

                    self.thread = WorkerThread(task='LOAD_LEED_IMAGES', path=new_dir, ext='.tif')

                    # disconnect any previously connected Signals/Slots
                    self.disconnect(self.thread, QtCore.SIGNAL('output(PyQt_PyObject)'), self.retrieve_LEED_data)
                    self.disconnect(self.thread, QtCore.SIGNAL('finished()'), self.update_LEED_img)
                    # connect appropriate signals for loading LEED data
                    self.connect(self.thread, QtCore.SIGNAL('output(PyQt_PyObject)'), self.retrieve_LEED_data)
                    self.connect(self.thread, QtCore.SIGNAL('finished()'),
                                 lambda: self.update_LEED_img(index=self.current_leed_index))
                    self.thread.start()

                    # self.leeddat.dat_3d = self.leeddat.load_LEED_TIFF(new_dir)
                    # print('New Data shape: {}'.format(self.leeddat.dat_3d.shape))
                    # if self.leeddat.dat_3d.shape[2] != len(self.leeddat.elist):
                    #    print('! Warning: New Data does not match current energy parameters !')
                    #    print('Updating Energy parameters ...')
                    #    self.set_energy_parameters(dat='LEED')
                    # self.current_leed_index = self.leeddat.dat_3d.shape[2]-1
                    # self.update_LEED_img(index=self.current_leed_index)

                elif entry in ['PNG', 'png']:
                    new_dir = str(QtGui.QFileDialog.getExistingDirectory(self, "Select directory containing PNG files"))
                    if new_dir == '':
                        print('Loading Canceled ...')
                        return
                    print('New Data Directory set to {}'.format(new_dir))
                    self.thread = WorkerThread(task='LOAD_LEED_IMAGES', path=new_dir, ext='.png')
                    # disconnect any previously connected Signals/Slots
                    self.disconnect(self.thread, QtCore.SIGNAL('output(PyQt_PyObject)'), self.retrieve_LEED_data)
                    self.disconnect(self.thread, QtCore.SIGNAL('finished()'), self.update_LEED_img)
                    # connect appropriate signals for loading LEED data
                    self.connect(self.thread, QtCore.SIGNAL('output(PyQt_PyObject)'), self.retrieve_LEED_data)
                    self.connect(self.thread, QtCore.SIGNAL('finished()'),
                                 lambda: self.update_LEED_img(index=self.current_leed_index))
                    self.thread.start()

                    # self.leeddat.dat_3d = self.leeddat.load_LEED_PNG(new_dir)
                    # print('New Data shape: {}'.format(self.leeddat.dat_3d.shape))
                    # if self.leeddat.dat_3d.shape[2] != len(self.leeddat.elist):
                    #    print('! Warning: New Data does not match current energy parameters !')
                    #    print('Updating Energy parameters ...')
                    #    self.set_energy_parameters(dat='LEED')
                    # self.current_leed_index = self.leeddat.dat_3d.shape[2]-1
                    # self.update_LEED_img(index=self.current_leed_index)

                else:
                    new_dir = str(QtGui.QFileDialog.getExistingDirectory(self, "Select directory containing DAT files"))
                    if new_dir == '':
                        print('Loading Canceled ...')
                        return
                    print('New Data Directory set to {}'.format(new_dir))

                    entry, ok = QtGui.QInputDialog.getInt(self, "Choose Image Height", "Enter Positive Int >= 2", value=544, min=2, max=8000)
                    if not ok:
                        print("Loading Raw Data Canceled ...")
                        return
                    else:
                        self.leeddat.ht = entry

                    entry, ok = QtGui.QInputDialog.getInt(self, "Choose Image Width", "Enter Positive Int >= 2", value=576, min=2, max=8000)
                    if not ok:
                        print("Loading Raw Data Canceled ...")
                        return
                    else:
                        self.leeddat.wd = entry

                    # redundant code is redundant
                    # self.leeddat.dat_3d = self.leeddat.load_LEED_RAW(new_dir)

                    self.thread = WorkerThread(task='LOAD_LEED', path=new_dir, imht=self.leeddat.ht, imwd=self.leeddat.wd)

                    # disconnect any previously connected Signals/Slots
                    self.disconnect(self.thread, QtCore.SIGNAL('output(PyQt_PyObject)'), self.retrieve_LEED_data)
                    self.disconnect(self.thread, QtCore.SIGNAL('finished()'), self.update_LEED_img)
                    # connect appropriate signals for loading LEED data
                    self.connect(self.thread, QtCore.SIGNAL('output(PyQt_PyObject)'), self.retrieve_LEED_data)
                    self.connect(self.thread, QtCore.SIGNAL('finished()'), lambda: self.update_LEED_img(index=self.current_leed_index))
                    self.thread.start()

            return

    def retrieve_LEED_data(self, dat):
        """
        Custom Slot to recieve data from a QThread object upon thread exit
        :param dat:
            numpy ndarray output by WorkerThread
        :return:
        """
        self.leeddat.dat_3d = dat
        self.current_leed_index = self.leeddat.dat_3d.shape[2]-1
        return

    def update_LEED_slider(self, value):
        """
        When LEED Slider is changed
        Place call to update_LEED_img()
        """
        if not self.hasdisplayed_leed:
            return

        # DEBUG
        # print(len(self.leeddat.elist))
        # print(value)
        self.LEED_slider_value.setText(str(LF.filenumber_to_energy(self.leeddat.elist, value)) + " eV")
        # set slider to value
        self.LEED_slider.setValue(value)
        self.update_LEED_img(value)

    def format_LEED_slider(self):
        """
        Reset the bounds on the LEEM image slider
        :return none
        """
        self.LEED_slider.setRange(0, self.leeddat.dat_3d.shape[2] - 1)

    def update_LEED_img(self, index=0):
        """
        Display LEED image by filenumber index
        :param index:
            int pointing to position along third axis in self.leeddat.dat3d numpy ndarray
        :return:
        """

        if self.leeddat.dat_3d.shape[2] != len(self.leeddat.elist):
            print('! Warning: New Data does not match current energy parameters !')
            print('Updating Energy parameters ...')
            self.set_energy_parameters(dat='LEED')
        self.LEED_IV_ax.set_aspect('auto')
        if index <= self.leeddat.dat_3d.shape[2]:
            self.LEED_img_ax.imshow(self.leeddat.dat_3d[:, :, index], cmap=cm.Greys_r)
        else:
            print('Image index out of bounds - displaying last image in stack ...')
            self.LEED_img_ax.imshow(self.leeddat.dat_3d[:, :, -1], cmap=cm.Greys_r)

        # format LEED_slider so that its values match with the third axis of self.leeddat.dat_3d
        self.format_LEED_slider()

        if not self.Style:
            self.LEED_img_ax.set_title('LEED Image: E= {} eV'.format(LF.filenumber_to_energy(self.leeddat.elist, index)),
                                   fontsize=18)
        else:
            self.LEED_img_ax.set_title('LEED Image: E= {} eV'.format(LF.filenumber_to_energy(self.leeddat.elist, index)),
                                   fontsize=18, color='white')

        self.LEED_IV_canvas.draw()
        self.has_loaded_data = True
        self.hasdisplayed_leed = True
        self.current_leed_index = index
        return

    def show_LEED_image_by_index(self):
        """
        Display slice from self.leeddat.dat3d according to integer index input by User
        :return none:
        """
        entry, ok = QtGui.QInputDialog.getInt(self, "Enter Image Number",
                                              "Enter an integer between 0 and {}".format(self.leeddat.dat_3d.shape[2]-1),
                                              value=self.leeddat.dat_3d.shape[2]-1,
                                              min=0,
                                              max=self.leeddat.dat_3d.shape[2]-1)
        if ok:
            self.update_LEED_img(index=entry)
        return

    def show_LEED_image_by_energy(self):
        """
        Display slice from self.leeddat.dat3d according to an energy value input by User in eV
        :return none:
        """
        entry, ok = QtGui.QInputDialog.getDouble(self, "Enter Image Number",
                                              "Enter an integer between {0} and {1}".format(self.leeddat.elist[0], self.leeddat.elist[-1]),
                                              value=int(len(self.leeddat.elist)/2),
                                              min=0,
                                              max=self.leeddat.elist[-1])
        if ok:
            self.update_LEED_img(index=LF.energy_to_filenumber(self.leeddat.elist, entry))
        return

    def set_energy_parameters(self, dat=None):
        """
        Set the energy list for either self.leeddat or self.leemdat
        If data was loaded from an experiment YAML config file, use the YAML settings
        Otherwise, have User manually enter settings
        :return none:
        """
        if dat is None:
            return

        if self.exp is not None:
            # get energy params from loaded config file

            if dat == 'LEEM' and self.exp.exp_type == 'LEEM':
                energy_list = [self.exp.mine]
                while energy_list[-1] != self.exp.maxe:
                    energy_list.append(round(energy_list[-1] + self.exp.stepe, 2))
                self.leemdat.elist = energy_list

            elif dat == 'LEEM' and self.prev_exp is not None:
                # dat = LEEM but most current exp is not a LEEM exp
                # check if another exp has been loaded and is a LEEM exp
                if self.prev_exp.exp_type == 'LEEM':
                    energy_list = [self.prev_exp.mine]
                    while energy_list[-1] != self.prev_exp.maxe:
                        energy_list.append(round(energy_list[-1] + self.prev_exp.stepe, 2))
                    self.leemdat.elist = energy_list

            elif dat == 'LEED' and self.exp.exp_type == 'LEED':
                energy_list = [self.exp.mine]
                while energy_list[-1] != self.exp.maxe:
                    energy_list.append(round(energy_list[-1] + self.exp.stepe, 2))
                self.leeddat.elist = energy_list

            elif dat == 'LEED' and self.prev_exp is not None:
                # dat = LEED but most current exp is not a LEED exp
                # check if another exp has been loaded and is a LEED exp
                if self.prev_exp.exp_type == 'LEED':
                    energy_list = [self.prev_exp.mine]
                    while energy_list[-1] != self.prev_exp.maxe:
                        energy_list.append(round(energy_list[-1] + self.prev_exp.stepe, 2))
                    self.leemdat.elist = energy_list

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

    def swap_byte_order(self, dat=None):
        """
        Change the byte order of data stored in numpy ndarray by invoking np.ndarray.swapbyteorder()
        This is useful if the data is loaded from an experiment YAML config file but the byteorder
        of the dat is unknown.
        :return:
        """
        if dat is None:
            return

        elif dat == 'LEED' and self.hasdisplayed_leed:
            self.leeddat.dat_3d = self.leeddat.dat_3d.byteswap()
            print('Byte order of current LEED data set has been swapped.')
            self.update_LEED_img(index=self.current_leed_index)

        elif dat == 'LEEM' and self.hasdisplayed_leem:
            self.leemdat.dat_3d = self.leemdat.dat_3d.byteswap()
            print('Byte order of current LEEM data set has been swapped.')
        else:
            print('Unknown Data type for Swap Byte Order ...')
        return

    def LEED_click(self, event):
        """
        Handle mouse-clicks in the main LEED Image Axis
        :param event:
            matplotlib button_release_event for mouse clicks
        :return none:
        """
        if not event.inaxes == self.LEED_img_ax:
            # discard clicks that originate outside the image axis
            return
        if not self.has_loaded_data:
            return
        if self.Debug:
            print('LEED Click registered ...')

        # Handle Edge cases:
        if (event.xdata - self.leeddat.box_rad) < 0 or \
           (event.ydata - self.leeddat.box_rad) < 0 or \
           (event.xdata + self.leeddat.box_rad) > self.leeddat.dat_3d.shape[1] or \
           (event.ydata + self.leeddat.box_rad) > self.leeddat.dat_3d.shape[0]:

            print("Click located too close to image edge.")
            print("No IV will be selected.")
            print("Use smaller integration window or data area further from edge.")
            return

        # We know the click was inside the image axis and not near the edge:
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
            self.clear_LEED_click()

    def clear_LEED_click(self):
        """
        Reset click count, rectangle coordinates, rectangle patches, and clear LEED IV plot
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

        if self.Style:
            self.LEED_IV_ax.set_title("LEED I(V)", fontsize=18, color='white')
            self.LEED_IV_ax.set_ylabel('Intensity [arb. units]', fontsize=18, color='white')
            self.LEED_IV_ax.set_xlabel('Energy [eV]', fontsize=18, color='white')
            self.LEED_IV_ax.tick_params(labelcolor='w', top='off', right='off')
        else:
            self.LEED_IV_ax.set_title("LEED I(V)", fontsize=18)
            self.LEED_IV_ax.set_ylabel('Intensity [arb. units]', fontsize=18)
            self.LEED_IV_ax.set_xlabel('Energy [eV]', fontsize=18)
            self.LEED_IV_ax.tick_params(labelcolor='w', top='off', right='off')

        self.LEED_IV_canvas.draw()
        return

    def clear_LEED_plots_only(self):
        """
        Clear LEED IV plot but leave the stored rectangle patches as is
        Useful if you want to toggle smoothing on and then re-plot the current selections
        :return none:
        """
        print('Clearing Plots ...')
        self.LEED_IV_ax.clear()
        if self.Style:
            self.LEED_IV_ax.set_title("LEED I(V)", fontsize=18, color='white')
            self.LEED_IV_ax.set_ylabel('Intensity [arb. units]', fontsize=18, color='white')
            self.LEED_IV_ax.set_xlabel('Energy [eV]', fontsize=18, color='white')
            self.LEED_IV_ax.tick_params(labelcolor='w', top='off', right='off')
        else:
            self.LEED_IV_ax.set_title("LEED I(V)", fontsize=18)
            self.LEED_IV_ax.set_ylabel('Intensity [arb. units]', fontsize=18)
            self.LEED_IV_ax.set_xlabel('Energy [eV]', fontsize=18)
            self.LEED_IV_ax.tick_params(labelcolor='w', top='off', right='off')
        self.LEED_IV_canvas.draw()

    def plot_LEED_IV(self):
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
            return
        tot_pix = (2*self.leeddat.box_rad)**2
        for idx, tup in enumerate(self.rect_coords):
            # generate 3d slice of main data array
            # this represents the integration window projected along the third array axis
            int_win = self.leeddat.dat_3d[int(tup[0]-self.leeddat.box_rad):int(tup[0]+self.leeddat.box_rad),
                                          int(tup[1]-self.leeddat.box_rad):int(tup[1]+self.leeddat.box_rad),
                                          :]
            # plot unaveraged intensity 3/30/2016
            # ilist = [img.sum()/tot_pix for img in np.rollaxis(int_win, 2)]

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
        self.leeddat.average_ilist = average_int

        if self.use_avg:
            print('Local Average Background Stored')
            self.background = average_int
        else:
            print('Average I(V) curve data stored')
            self.last_average = average_int
        self.use_avg = False
        self.LEED_IV_ax.clear()
        self.LEED_IV_ax.plot(self.leeddat.elist, average_int, color=self.colors[-1])
        if self.Style:
            self.LEED_IV_ax.set_title('Average I(V) of Currently Selected Curves', color='w')
            self.LEED_IV_ax.set_ylabel("Intensity (arb. units)", fontsize=18, color='w')
            self.LEED_IV_ax.set_xlabel("Energy (eV)", fontsize=18, color='w')
            self.LEED_IV_ax.tick_params(labelcolor='w', top='off', right='off')
        else:
            self.LEED_IV_ax.set_title('Average I(V) of Currently Selected Curves')
            self.LEED_IV_ax.set_ylabel("Intensity (arb. units)", fontsize=18)
            self.LEED_IV_ax.set_xlabel("Energy (eV)", fontsize=18)
            self.LEED_IV_ax.tick_params(labelcolor='b', top='off', right='off')
        print('Plotting Average LEED_I(V) ...')
        self.LEED_IV_canvas.draw()
        return

    def toggle_debug_setting(self):
        """
        Swap settings for Debug property
        :return: none
        """
        if self.Debug:
            print('Disabling Debug ...')
            self.Debug = False
        else:
            print('Enabling Debug ...')
            self.Debug = True
        return

    def toggle_smoothing(self):
        """
        Toggle settings for data smoothing
        Set file output flags appropriately when smoothing is enabled
        If smoothing is being enabled - query user for new settings
        :return none:
        """

        if self.smooth_leed_plot:
            # smoothing already enabled - disable it
            self.smooth_leem_plot = False
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
                    self.toggle_smoothing()
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
                print('Window_Length entry, {0}, was odd - Using next even integer {1}.'.format(entry, entry + 1))
                entry += 1
                self.smooth_window_len = int(entry)
            else:
                self.smooth_window_len = int(entry)
        self.smooth_leed_plot = True
        self.smooth_leem_plot = True
        self.smooth_file_output = True
        print('Smoothing Enabled: Window = {0}; Window Length = {1}'.format(self.smooth_window_type, self.smooth_window_len))
        return

    def set_integration_window(self):
        """
        Set new box radius for integration window
        Integration is a square of side length 2*(box radius)
        :return none:
        """
        entry, ok = QtGui.QInputDialog.getInt(self, "Set Integration Window Half Length",
                                              "Enter a valid integer >= 2.", value=20, min=2, max=2000)
        if not ok:
            return
        if self.hasplotted_leed:
            # Make sure User selected integration window is smaller than total data area
            if int(entry) >= int(self.leeddat.dat_3d.shape[0]/2) or \
               int(entry) >= int(self.leeddat.dat_3d.shape[1]/2):
                print("Error: Integration window larger than viewable data area.")
                print("Please choose an integer less than {0}.".format(min(int(self.leeddat.dat_3d.shape[0]/2),
                                                                           int(self.leeddat.dat_3d.shape[1]/2))))
                return
        self.leeddat.box_rad = entry
        print('New Integration Window set to {0} x {1}.'.format(2*self.leeddat.box_rad, 2*self.leeddat.box_rad))

    def get_background_from_selections(self):
        """
        :return none:
        """
        if not self.hasplotted_leed:
            return

        self.manual_background = [0]*self.leeddat.dat_3d.shape[2]  # list of correct length to be used with map()
        num_curves = len(self.current_selections)

        # Sum the currently selected I(V) curves element by element
        # Finally divide each element by the number of curves to generate average background I(V)
        for tuple in self.current_selections:
            curve = tuple[0]
            self.manual_background = list(map(add, curve, self.manual_background))  # list() for py3 compatibility

        self.manual_background = [k/(num_curves) for k in self.manual_background]
        print("Background I(V) curve stored. Curve averaged from {0} user selected I(V) curves".format(num_curves))

    def show_calculated_background(self):
        """
        :return none:
        """
        if not self.manual_background:
            return

        self.bkgnd_window = QtGui.QWidget()
        self.bkgnd_window.setMinimumHeight(0.35 * self.max_height)
        self.bkgnd_window.setMinimumWidth(0.45 * self.max_width)
        self.bfig, self.bplot_ax = plt.subplots(1, 1, figsize=(8, 6), dpi=100)
        self.bcanvas = FigureCanvas(self.bfig)
        self.bcanvas.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding
                                   )
        self.bmpl_toolbar = NavigationToolbar(self.bcanvas, self.bkgnd_window)
        nvbox = QtGui.QVBoxLayout()
        nvbox.addWidget(self.bcanvas)
        nvbox.addWidget(self.bmpl_toolbar)
        self.bkgnd_window.setLayout(nvbox)

        rect = self.bfig.patch
        if self.Style:
            rect.set_facecolor((68 / 255., 67 / 255., 67 / 255.))
            self.bplot_ax.set_title("Average Background I(V)", fontsize=18, color='w')
            self.bplot_ax.set_ylabel('Intensity [arb. units]', fontsize=18, color='white')
            self.bplot_ax.set_xlabel('Energy [eV]', fontsize=18, color='white')
            self.bplot_ax.xaxis.label.set_color('w')
            self.bplot_ax.yaxis.label.set_color('w')
        self.bplot_ax.plot(self.leeddat.elist, self.manual_background)
        plt.grid(False)
        self.bcanvas.draw()
        self.bkgnd_window.show()
        return

    def subtract_stored_background(self):
        """
        :return none
        """
        if (not self.hasdisplayed_leed) or (not self.manual_background):
            # if no current I(V) curves or no background curve simply return
            return
        self.LEED_IV_ax.clear()
        curves = []
        OFFSET = False
        for tuple in self.current_selections:
            curve = tuple[0]
            corrected_curve = list(map(sub, curve, self.manual_background))  # list() for py3 compatibility
            if np.min(corrected_curve) < 0:
                OFFSET = True
            curves.append((corrected_curve, tuple[1]))
        for curve in curves:
            if OFFSET:
                # prevent negative intensity by adding constant offset to each data point
                # list() for py3 compatibility
                self.LEED_IV_ax.plot(self.leeddat.elist, list(map(add, curve[0], [100000]*len(curve[0]))), color=curve[1])
                print("Plotting with manual offset after subtraction")
            else:
                self.LEED_IV_ax.plot(self.leeddat.elist, curve[0], color=curve[1])

        if self.Style:
            self.LEED_IV_ax.set_title("Corrected I(V)", fontsize=18,color='white')
            self.LEED_IV_ax.set_ylabel('Intensity [arb. units]', fontsize=18, color='white')
            self.LEED_IV_ax.set_xlabel('Energy [eV]', fontsize=18, color='white')
        else:
            self.LEED_IV_ax.set_title("Corrected I(V)", fontsize=18)
            self.LEED_IV_ax.set_ylabel('Intensity [arb. units]', fontsize=18)
            self.LEED_IV_ax.set_xlabel('Energy [eV]', fontsize=18)
        self.LEED_IV_canvas.draw()

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
                """
                # perimeter sum
                ps = (img[0, 0:] + img[0:, -1] + img[-1, :] + img[0:, 0]).sum()  # sum edges
                ps -= (img[0,0] + img[0, -1] + img[-1, -1] + img[-1, 0])  # subtract corners for double counting
                num_pixels = 2*(2*(2*self.leeddat.box_rad)-2)
                ps /= num_pixels
                bkgnd.append(ps)  # store average perimeter pixel value
                if self.Debug:
                    print("Average Background calculated as {}".format(ps))
                    print("Raw Sum: {}".format(img.sum()))
                img -= int(ps)  # subtract background from each pixel
                if self.Debug:
                    print("Adjusted Sum: {}".format(img[img >= 0].sum()))
                    print(img)
                # calculate new total intensity of the integration window counting only positive values
                # there should be no negatives but we discard them just incase
                adj_ilist.append(img[img >= 0].sum())
                """
                total_int = img.sum()
                per_sum = (img[0, :] + img[0:, -1] + img[-1, :] + img[:, 0]).sum()  # sum edges
                per_sum -= (img[0, 0] + img[0, -1] + img[-1, -1] + img[-1, 0])  # subtract corners for double counting
                per_sum  = (per_sum / float(8*self.leeddat.box_rad - 4))*(2*self.leeddat.box_rad)**2

                corrected_int = total_int - per_sum
                bkgnd.append(per_sum)
                adj_ilist.append(corrected_int)

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
        rawoutbut.clicked.connect(lambda: self.output_LEED_to_Text(data=self.raw_selections, smth=self.smooth_file_output))  # output button
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
        coroutputbutton.clicked.connect(lambda: self.output_LEED_to_Text(data=self.cor_data, smth=self.smooth_file_output))  # output button
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
        exbackoutbut.clicked.connect(lambda: self.output_LEED_to_Text(data=self.ex_back, smth=self.smooth_file_output))  # output button
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
        avgbackoutbut.clicked.connect(lambda: self.output_LEED_to_Text(data=self.avg_back, smth=self.smooth_file_output))  # output button
        nhbox.addStretch(1)
        nhbox.addWidget(avgbackoutbut)
        self.pop_window4.setLayout(nvbox)

        num_curves = len(self.current_selections)
        last_raw_curve_idx = int(num_curves/2) -1  # manually cast to int for py3 compliance
        if self.Debug:
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

        if not self.Style:
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

    def output_to_text(self, data=None, smth=None):
        """
        Write out data to text files in columar format
        :param data:
            str flag for LEEM or LEED data now deprecated
        :return none:
        """
        if data is None:
            # no data passed as input; do nothing
            print('No Data to Output ...')
            return

        # TODO: Now that LEED/LEEM have separate output functions
        #       the data flag is no longer needed

        if data == 'LEEM':
            # handle LEEM output
            if not self.hasplotted_leem:
                return
            if not os.path.exists(os.path.join(self.leemdat.data_dir, 'ivout')):
                os.path.mkdir(os.path.join(self.leemdat.data_dir, 'ivout'))
            leem_out_dir = os.path.join(self.leemdat.data_dir, 'ivout')
            n = len(self.leem_IV_list)  # number of threads to run
            count = 1  # thread number
            for tup in self.leem_IV_list:
                outfile = os.path.join(leem_out_dir, str(tup[2])+'-'+str(tup[3])+'.txt')
                print('Starting thread {0} of {1}'.format(count, n))

                # gather data to output and handle smoothing
                elist = tup[0]
                ilist = tup[1]
                if smth:
                    ilist = LF.smooth(ilist, window_len=self.smooth_window_len,
                                      window_type=self.smooth_window_type)

                self.thread = WorkerThread(task='OUTPUT_TO_TEXT',
                                           elist=elist, ilist=ilist,
                                           name=outfile)
                self.connect(self.thread, QtCore.SIGNAL('finished()'), self.output_complete)
                self.thread.start()
                count += 1
            return

    def output_average_LEED(self):
        """
        :return none:
        """
        # print('Call placed to output_average_LEED')
        if self.leeddat.average_ilist is None:
            pass
        else:
            self.output_LEED_to_Text(data=self.leeddat.average_ilist, smth=self.smooth_file_output)
        return

    def output_LEED_to_Text(self, data=None, smth=None):
        """
        Output LEED I(V) data to a tab delimited text file
        :param data:
            flag for outputting data from main window (data=None)
            or for outputting data from a popped out window after background subtraction
            In this second case, data points to a list of intensity data points
        :param smth:
            boolean flag for smoothing the output intensity data
        :return:
        """
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

        if data is None:
            # Output data from main window
            # for each element in rect_coords - spin up a qthread to output the data to file
            for idx, tup in enumerate(self.rect_coords):

                # generate raw data to pass to new thread to be output
                int_win = self.leeddat.dat_3d[tup[0]-self.leeddat.box_rad:tup[0]+self.leeddat.box_rad,
                                              tup[1]-self.leeddat.box_rad:tup[1]+self.leeddat.box_rad,
                                              :]
                ilist = [img.sum() for img in np.rollaxis(int_win, 2)]
                elist = self.leeddat.elist

                # check if smoothing is enabled
                if self.smooth_file_output:
                    ilist = LF.smooth(ilist)
                # full file name

                # check for single file output
                if len(self.rect_coords) == 1:
                    full_path = os.path.join(out_dir, entry+'.txt')
                    # full_path = out_dir + '/' + entry + '.txt'
                else:
                    full_path = os.path.join(out_dir, entry+'_'+str(idx+1)+'.txt')
                    # full_path = out_dir + '/' + entry + '_' + str(idx+1)  + '.txt'
                print('Starting thread {0} of {1} ...'.format(idx, len(self.rect_coords)))

                self.thread = WorkerThread(task='OUTPUT_TO_TEXT',
                                           ilist=ilist, elist=elist,
                                           name=full_path)

                self.connect(self.thread, QtCore.SIGNAL('finished()'), self.output_complete)
                self.thread.start()
            print('Done Writing Files ...')
            return
        else:
            # Output data from popped out window
            # Currently only supports background subtraction for one curve at a time
            ilist = data
            elist = self.leeddat.elist
            if smth:
                ilist = LF.smooth(ilist, window_len=self.smooth_window_len, window_type=self.smooth_window_type)
            full_path = os.path.join(out_dir, entry+'.txt')
            print('Starting thread 0 of 1 ...')
            self.thread = WorkerThread(task='OUTPUT_TO_TEXT',
                                       ilist=ilist, elist=elist,
                                       name=full_path)
            self.connect(self.thread, QtCore.SIGNAL('finished()'), self.output_complete)
            self.thread.start()
            print('Done Writing Files ...')
            return

    def get_beam_max_update_slice(self, int_win, win_coords, img):
        """
        Given a 2d integration window centered on a user selected point,
        find the beam maximum in the integration window then return a
        new slice from leeddat.dat3d centered on the beam max.
        :param int_win:
            2d data slice from leeddat.dat3d
        :param win_coords:
            tuple containing the coordinates of the center of
            int_win relative to (0,0,:) in leeddat.dat3d
        :param img:
            full 2d array of pixels. represents one slice from image stack
        :return new_slice:
            2d numpy array sliced from leeddat.dat3d
        """
        c_bm, r_bm = LF.find_local_maximum(int_win)  # find_local_max outputs (x,y) from opencv
        r_u, c_u = win_coords
        # coordinates of top left corner for new int window centered on beam max
        new_top_left_coords = (r_u + r_bm - 2*self.leeddat.box_rad,
                               c_u + c_bm - 2*self.leeddat.box_rad)
        ntl_r = new_top_left_coords[0]
        ntl_c = new_top_left_coords[1]

        return img[ntl_r:ntl_r+2*self.leeddat.box_rad,
                   ntl_c:ntl_c+2*self.leeddat.box_rad]

    def new_leed_extract(self):
        """
        extract I(V) data from currently selected areas in self.leeddat.dat3d
        :return none:
        """
        if (self.rect_count == 0) or (not self.rects) or (not self.rect_coords):
            # no data selected; do nothing
            print('No Data Selected to Plot')
            return

        if self.leeddat.dat_3d.shape[2] != len(self.leeddat.elist):
            print("! Warning Data does not match current Energy Parameters !")
            print("Can not plot data due to mismatch ...")
            return

        self.hasplotted_leed = True

        # Loop for each user selection
        for idx, tup in enumerate(self.rect_coords):

            # Loop for each image in stack to generate ilist
            ilist = []
            for img in np.rollaxis(self.leeddat.dat_3d, 2):

                # generate window based on user selection coordinates
                r_u, c_u = tup
                win = img[r_u - self.leeddat.box_rad:r_u + self.leeddat.box_rad,
                          c_u - self.leeddat.box_rad:c_u + self.leeddat.box_rad]
                new_win = self.get_beam_max_update_slice(int_win=win, win_coords=tup, img=img)
                ilist.append(new_win.sum()/((2*self.leeddat.box_rad)**2))

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

    def shift_user_selection(self):
        """
        Using opencv, find the relative beam maximum nearest to the user selection.
        Shift the user selected integration window to be centered on the
        located maxima.
        This takes out some ambiguity when comparing I(V) curves from the same
        LEED beams at extracted at different times.
        In the future, a CONFIG setting will be toggle-able such that this function can be
        always enabled or always disabled.
        :return: none
        """
        self.shifted_rects = []
        self.shifted_rect_coords = []
        for tup in self.rect_coords:
            int_win = self.leeddat.dat_3d[tup[0]-self.leeddat.box_rad:tup[0]+self.leeddat.box_rad,
                                          tup[1]-self.leeddat.box_rad:tup[1]+self.leeddat.box_rad,
                                          :]

            # TODO: Clean up this algorithm. Remind what the variables actually do

            # TODO: IN PROGRESS - implementing full beam centering algorithm for each image in stack

            maxLoc = LF.find_local_maximum(int_win[:, :, int(int_win.shape[2]/2)])  # (x,y)
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

    ###########################################################################################
    # Core Functionality:
    # LEEM Functions and Processes
    ###########################################################################################

    def load_LEEM(self):
        """
        Manually load LEEM raw data
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
            self.thread = WorkerThread(task='LOAD_LEEM',
                                       path=self.leemdat.data_dir,
                                       imht=self.leemdat.ht,
                                       imwd=self.leemdat.wd)
            # disconnect any previously connected Signals/Slots
            self.disconnect(self.thread, QtCore.SIGNAL('output(PyQt_PyObject)'), self.retrieve_LEEM_data)
            self.disconnect(self.thread, QtCore.SIGNAL('finished()'), self.update_LEEM_img)
            # connect appropriate signals for loading LEED data
            self.connect(self.thread, QtCore.SIGNAL('output(PyQt_PyObject)'), self.retrieve_LEEM_data)
            self.connect(self.thread, QtCore.SIGNAL('finished()'), self.update_LEEM_img)
            self.thread.start()

            #self.leemdat.dat_3d = LF.process_LEEM_Data(self.leemdat.data_dir,
            #                                           self.leemdat.ht,
            #                                           self.leemdat.wd)
        except ValueError:
            print('Error Loading LEEM Data: Please Recheck Image Settings')
            print('Resetting data directory to previous setting, {}'.format(prev_ddir))
            return

    def retrieve_LEEM_data(self, dat):
        """
        Catch the emitted numpy ndarray emitted from QThread when finished loading data
        :return none:
        """
        self.leemdat.dat_3d = dat
        return

    def update_LEEM_img(self):
        """
        After loading data, format necessary LEEM plots and slider which in turn updates plot
        :return none:
        """
        # Assuming that data loading was successful - self.leemdat.dat_3d is now a 3d numpy array
        # Generate energy list to correspond to the third array axis
        print('Data Loaded successfully to numpy array with shape: {}'.format(self.leemdat.dat_3d.shape))
        self.set_energy_parameters(dat='LEEM')
        self.format_slider()
        self.hasdisplayed_leem = True

        if not self.has_loaded_data:
            self.update_image_slider(self.leemdat.dat_3d.shape[2]-1)
            self.has_loaded_data = True
            return
        # self.update_image_slider(0)
        return

    def format_slider(self):
        """
        Reset the bounds on the LEEM image slider
        :return none
        """
        self.image_slider.setRange(0, self.leemdat.dat_3d.shape[2]-1)

    def update_image_slider(self, value):
        """
        Update the Slider label value to the new electron energy
        Call show_LEEM_Data() to display the correct LEEM image
        :param value:
            int value from slider representing filenumber
        :return none:
        """
        if not self.hasdisplayed_leem:
            return
        self.image_slider_value_label.setText(str(
                                    LF.filenumber_to_energy(
                                                            self.leemdat.elist,
                                                            value)) + " eV")
        # set slider to value
        self.image_slider.setValue(value)
        self.show_LEEM_Data(self.leemdat.dat_3d, value)

    def clear_LEEM_IV(self):
        """
        Clear circular patches, patch coordinates, and LEEM IV plot
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
        if not self.Style:
            self.LEEM_ax.set_title('LEEM Image: E= ' + str(LF.filenumber_to_energy(self.leemdat.elist,
                                                                                   self.leemdat.curimg)), fontsize=18)
        else:
            self.LEEM_ax.set_title('LEEM Image: E= ' + str(LF.filenumber_to_energy(self.leemdat.elist,
                                                                                   self.leemdat.curimg)), fontsize=18, color='white')
        self.LEEM_canvas.draw()

    def show_LEEM_Data(self, data, imgnum):
        """
        Display slice from self.leemdat.dat3d to self.LEEM_ax
        :param data:
            numpy ndarray corresponding to LEEM IV image stack, self.leemdat.dat3d
        :param imgnum:
            int index pointing to position along third axis of numpy ndarray self.leemdat.dat3d
        :return none:
        """
        self.leemdat.curimg = imgnum
        img = data[0:, 0:, self.leemdat.curimg]

        if self.Style:
            self.LEEM_ax.set_title('LEEM Image: E= ' + str(LF.filenumber_to_energy(self.leemdat.elist, self.leemdat.curimg)) +' eV', fontsize=18, color='white')
        else:
            self.LEEM_ax.set_title('LEEM Image: E= ' + str(LF.filenumber_to_energy(self.leemdat.elist, self.leemdat.curimg)) +' eV', fontsize=18)

        self.LEEM_ax.imshow(img, cmap=cm.Greys_r)
        self.LEEM_canvas.draw()
        return

    def leem_click(self, event):
        """
        Handle mouse click events that originate from/in the LEEM image axis
        :param event:
            matplotlib mouse_click_event
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
        :param event:
            matplotlib mouse_click_event
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

        if self.smooth_leem_plot:
            self.LEEM_IV_ax.plot(self.leemdat.elist, LF.smooth(self.leemdat.ilist,
                                                               self.smooth_window_len,
                                                               self.smooth_window_type),
                                 color=self.colors[self.click_count-1]
                                 )
        else:
            self.LEEM_IV_ax.plot(self.leemdat.elist, self.leemdat.ilist, color=self.colors[self.click_count-1])

        self.leem_IV_list.append((self.leemdat.elist, self.leemdat.ilist,
                                  self.leemdat.curX, self.leemdat.curY,
                                  self.click_count-1)) # color stored by click count index
        self.leem_IV_mask.append(0)
        self.init_Plot_Axes()
        self.LEEM_canvas.draw()

    def popout_LEEM_IV(self):
        """
        Take data displayed in main LEEM_IV_ax and plot in a separate window
        Useful for saving picture of I(V) plot without including the LEEM image plot
        :return none:
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
        if self.Style:
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

    def LEEM_rectangular_selection(self):
        """
        User selects two points and a rectangle between them is
        chosen as an area for I(V)-analysis

        The average I(V) of the entire area is calculated
        :return:
        """
        # self.LEEM_ax.figure.canvas.mpl_disconnect(self.LEEM_click_handler)

        if not self.hasdisplayed_leem:
            return

        self.x0 = None
        self.x1 = None
        self.y0 = None
        self.y1 = None

        # Create new window and setup layout
        self.new_window_leem = QtGui.QWidget()
        self.new_window_leem.setWindowTitle("Select Rectangular Area")
        self.new_window_leem.setMinimumHeight(0.35 * self.max_height)
        self.new_window_leem.setMinimumWidth(0.45 * self.max_width)
        self.nfig_leem, self.nplot_ax_leem = plt.subplots(1, 1, figsize=(8, 6), dpi=100)
        self.ncanvas_leem = FigureCanvas(self.nfig_leem)
        self.ncanvas_leem.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                      QtGui.QSizePolicy.Expanding)
        self.cancelbut = QtGui.QPushButton("Cancel")
        self.okbut = QtGui.QPushButton("Ok")

        # setup color style
        rect = self.nfig_leem.patch
        if self.Style:
            # dark
            rect.set_facecolor((68 / 255., 67 / 255., 67 / 255.))
            self.nplot_ax_leem.set_title("LEEM Image", fontsize=12, color='w')
            self.nplot_ax_leem.xaxis.label.set_color('w')
            self.nplot_ax_leem.yaxis.label.set_color('w')

        else:
            # light
            rect.set_facecolor((189 / 255., 195 / 255., 199 / 255.))

        plt.axis('off')
        plt.grid(False)

        # set button layout
        button_hbox = QtGui.QHBoxLayout()
        button_hbox.addStretch(1)
        button_hbox.addWidget(self.cancelbut)
        button_hbox.addStretch(1)
        button_hbox.addWidget(self.okbut)
        button_hbox.addStretch(1)

        # set layout for canvas and buttons
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.ncanvas_leem)
        vbox.addLayout(button_hbox)
        self.new_window_leem.setLayout(vbox)

        # setup event connections
        # buttons
        """
        self.cancelbut.clicked.connect(lambda: close(w=self.new_window_leem,
                                                     hdl=self.LEEM_click_handler,
                                                     ax=self.LEEM_ax,
                                                     action=self.leem_click))
        """
        self.cancelbut.clicked.connect(self.new_window_leem.close)
        self.okbut.clicked.connect(self.parse_selection)
        # image axis
        self.nplot_ax_leem.figure.canvas.mpl_connect('button_press_event', self.rect_on_press)
        self.nplot_ax_leem.figure.canvas.mpl_connect('button_release_event', self.rect_on_release)



        img = self.leemdat.dat_3d[0:, 0:, self.leemdat.curimg]
        self.nplot_ax_leem.imshow(img, cmap=cm.Greys_r)
        self.ncanvas_leem.draw()
        self.new_window_leem.show()

    def rect_on_press(self, e):
        """

        :param e: mpl on_press event
        :return:
        """
        if e.inaxes == self.nplot_ax_leem:
            if self._DEBUG:
                print("Button Press Event caught by LEEM_rectangular_selection.")
            self.x0 = e.xdata
            self.y0 = e.ydata

            self.leem_circ = patches.Circle(xy=(self.x0, self.y0), radius=3, fill=True, facecolor='red')
            self.nplot_ax_leem.add_patch(self.leem_circ)
            self.ncanvas_leem.draw()

    def rect_on_release(self, e):
        """

        :param e: mpl on_release event
        :return:
        """
        if self.leem_rect_count < len(self.colors):
            self.leem_rect_count += 1
        else:
            # TODO: handle this situation better
            self.leem_rect_count = 1

        if self._DEBUG:
            print("Button Release Event caught by LEEM_rectangular_selection.")
        self.x1 = e.xdata
        self.y1 = e.ydata

        if (self.x0 is not None and
            self.x1 is not None and
            self.y0 is not None and
            self.y1 is not None):

            w = self.x1 - self.x0
            h = self.y1 - self.y0
            xy = (self.x0, self.y0)
            self.leem_rect = patches.Rectangle(xy=xy, width=w, height=h,
                                               fill=False, linewidth=2,
                                               edgecolor=self.colors[self.leem_rect_count])
            self.nplot_ax_leem.add_patch(self.leem_rect)
            self.leem_rects.append(self.leem_rect)
            self.leem_circ.remove()
            self.ncanvas_leem.draw()

    def parse_selection(self):
        """

        :param w: window
        :return:
        """
        print("Parsing LEEM user selection(s) ...")
        # do something with self.leem_rect ...

        if self.leem_rects:
            # there are rectangular selections to parse

            # New window for plotted data

            self.leem_rect_plot_window = QtGui.QWidget()
            self.leem_rect_plot_window.setWindowTitle("User Selection(s): Average I(V) ")
            self.leem_rect_fig, self.leem_rect_iv_ax = plt.subplots(1, 1, figsize=(8, 6), dpi=100)
            self.leem_rect_canvas = FigureCanvas(self.leem_rect_fig)
            self.leem_rect_canvas.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)

            self.smooth_leem_rect_but = QtGui.QPushButton("Smooth I(V)")
            self.smooth_leem_rect_but.clicked.connect(self.smooth_leem_rect)

            vbox = QtGui.QVBoxLayout()
            vbox.addWidget(self.leem_rect_canvas)
            vbox.addWidget(self.smooth_leem_rect_but)
            self.leem_rect_plot_window.setLayout(vbox)
            rect = self.leem_rect_fig.patch
            if self.Style:
                # dark
                rect.set_facecolor((68 / 255., 67 / 255., 67 / 255.))


            # parse selections
            for idx, rect in enumerate(self.leem_rects):
                w = int(rect.get_width())
                h = int(rect.get_height())
                origin_x = int(rect.get_xy()[0])
                origin_y = int(rect.get_xy()[1])
                data_slice = self.leemdat.dat_3d[origin_y:origin_y + h + 1,
                                                 origin_x:origin_x + w + 1, :]
                ilist = [img.sum() for img in np.rollaxis(data_slice, 2)]
                self.leem_rect_iv_ax.plot(self.leemdat.elist, ilist, color=self.colors[idx+1])
                if self._DEBUG:
                    print(data_slice.shape)

            plt.grid(False)
            if self._Style:
                self.leem_rect_iv_ax.set_title("LEEM-I(V) Selection Average", fontsize=18, color='w')
                self.leem_rect_iv_ax.set_xlabel("Energy (eV)", fontsize=18, color='w')
                self.leem_rect_iv_ax.set_ylabel("Intensity (arb. units)", fontsize=18, color='w')
                self.leem_rect_iv_ax.tick_params(labelcolor='w', top='off', right='off')
            else:
                self.leem_rect_iv_ax.set_title("LEEM-I(V) Selection Average", fontsize=18)
                self.leem_rect_iv_ax.set_xlabel("Energy (eV)", fontsize=18)
                self.leem_rect_iv_ax.set_ylabel("Intensity (arb. units)", fontsize=18)
                self.leem_rect_iv_ax.tick_params(labelcolor='b', top='off', right='off')
            self.leem_rect_plot_window.show()
            self.leem_rect_canvas.draw()

        else:
            pass
        self.leem_rect_count = 0

    def smooth_leem_rect(self):
        """

        :return:
        """
        if not self.leem_rects:
            return
        # there is data to parse, smooth, and plot
        self.leem_rect_iv_ax.clear()
        for idx, rect in enumerate(self.leem_rects):
            w = int(rect.get_width())
            h = int(rect.get_height())
            origin_x = int(rect.get_xy()[0])
            origin_y = int(rect.get_xy()[1])
            data_slice = self.leemdat.dat_3d[origin_y:origin_y + h + 1,
                         origin_x:origin_x + w + 1, :]
            ilist = [img.sum() for img in np.rollaxis(data_slice, 2)]
            self.leem_rect_iv_ax.plot(self.leemdat.elist, LF.smooth(ilist), color=self.colors[idx + 1])
        if self._Style:
            self.leem_rect_iv_ax.set_title("LEEM-I(V) Selection Average", fontsize=18, color='w')
            self.leem_rect_iv_ax.set_xlabel("Energy (eV)", fontsize=18, color='w')
            self.leem_rect_iv_ax.set_ylabel("Intensity (arb. units)", fontsize=18, color='w')
            self.leem_rect_iv_ax.tick_params(labelcolor='w', top='off', right='off')
        else:
            self.leem_rect_iv_ax.set_title("LEEM-I(V) Selection Average", fontsize=18)
            self.leem_rect_iv_ax.set_xlabel("Energy (eV)", fontsize=18)
            self.leem_rect_iv_ax.set_ylabel("Intensity (arb. units)", fontsize=18)
            self.leem_rect_iv_ax.tick_params(labelcolor='b', top='off', right='off')
        self.leem_rect_canvas.draw()


    def plot_derivative(self):
        """
        Create new window and plot dI/dV for each current I(V) curve
        Note, dI/dV will, in general, amplify noise in the data.
        Thus it is recommended to smooth the data before calculating dI/dV
        :return none:
        """
        if not self.hasplotted_leem or len(self.leem_IV_list) == 0:
            return

        self.leem_didv_window = QtGui.QWidget()
        self.leem_didv_window.setMinimumHeight(0.35 * self.max_height)
        self.leem_didv_window.setMinimumWidth(0.45*self.max_width)
        self.leem_didv_fig, self.leem_didv_ax = plt.subplots(1,1, figsize=(8,6), dpi=100)
        self.leem_didv_can = FigureCanvas(self.leem_didv_fig)

        self.LEEM_IV_ax.clear()
        for tuple in self.leem_IV_list:
            data = tuple[1]
            color_idx = tuple[4]

            # Smooth data before taking derivative:
            if self.smooth_leem_plot:
                # use user settings
                data = LF.smooth(data, self.smooth_window_len, self.smooth_window_type)
            else:
                # use default settings
                data = LF.smooth(data)
            # calculate derivative; note this reduces the length by 1
            data = np.diff(data)/np.diff(self.leemdat.elist)

            if self.smooth_leem_plot:
                self.LEEM_IV_ax.plot(self.leemdat.elist[:-1], LF.smooth(data, self.smooth_window_len, self.smooth_window_type), color=self.colors[color_idx])
            else:
                self.LEEM_IV_ax.plot(self.leemdat.elist[:-1], data, color=self.colors[color_idx])
        self.LEEM_IV_ax.set_title("LEEM dI/dV")
        self.LEEM_canvas.draw()

    def smooth_current_IV(self, ax, can):
        """
        Apply data smoothing algorithm to currently plotted I(V) curves
        :param ax:
            mpl axis element which ill be plotting data
        :param can:
            canvas containing ax which needs to call draw() to update the image
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
                    self.smooth_currrent_IV(ax, can)
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
                print('Window_Length entry,{0}, was odd - Using next even integer {1}'.format((entry, entry + 1)))
                entry += 1
                self.smooth_window_len = int(entry)

            else:
                self.smooth_window_len = int(entry)

        for idx, tup in enumerate(self.leem_IV_list):
            ax.plot(tup[0], LF.smooth(tup[1], self.smooth_window_len, self.smooth_window_type), color=self.colors[tup[4]])
        if self.Style:
            ax.set_title("LEEM I(V)-Smoothed", fontsize=18, color='w')
            ax.set_ylabel("Intensity (arb. units)", fontsize=18, color='w')
            ax.set_xlabel("Energy (eV)", fontsize=18, color='w')
        else:
            ax.set_title("LEEM I(V)-Smoothed", fontsize=18)
            ax.set_ylabel("Intensity (arb. units)", fontsize=18)
            ax.set_xlabel("Energy (eV)", fontsize=18)
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
        :param xd:
            array-like set of x values
        :param yd:
            array-like set of y values
        :return:
            tuple of two elements: (boolean for curve is flat?, integer # of minima found)
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

    def check_flat(self, data, thresh=5):
        '''
        :param data:
            1d numpy array containing smoothed dI/dE data
        :param thresh:
            threshold value for
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
        Method for counting the number of minima in a LEEM-I(V) curve
        :param data:
            3d numpy array of smooth data cut to specific data range
        :param ecut:
            1d list of energy values cut to specific data range
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
        return

    def discrete_imshow(self, data, clrmp=cm.Spectral):
        '''
        :param data:
            2d numpy array to be plotted
        :param clrmp:
            mpl color map
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
