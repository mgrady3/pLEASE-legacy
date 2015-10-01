"""
This module contains classes pertinent
to creating the main GUI for the data
analysis suite

Maxwell Grady 2015
"""
import data
import terminal
import sys
import LEEMFUNCTIONS as LF
import matplotlib.cm as cm
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
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
        self.border_color = (58/255., 83/255., 155/255.)

        self.rect_count = 0
        self.max_leed_click = 10
        self.rects = []
        self.rect_coords = []
        self.shifted_rects = []
        self.shifted_rect_coords = []
        self.current_selections = []

        self.colors = sns.color_palette("Set2", 10)
        self.smooth_colors = sns.color_palette("Set2", 10)

        self.smth_leed_plot = False


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
            self.IV_ax.set_title("LEEM I(V)", fontsize=20)
            self.IV_ax.set_ylabel("Intensity (arb. units)", fontsize=16)
            self.IV_ax.set_xlabel("Energy (eV)", fontsize=16)
            self.IV_ax.tick_params(labelcolor='b', top='off', right='off')
        else:
            self.IV_ax.set_title("LEEM I(V)", fontsize=20, color='white')
            self.IV_ax.set_ylabel("Intensity (arb. units)", fontsize=16, color='white')
            self.IV_ax.set_xlabel("Energy (eV)", fontsize=16, color='white')
            self.IV_ax.tick_params(labelcolor='w', top='off', right='off')

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

        extractAction = QtGui.QAction('Extract I(V)', self)
        extractAction.setShortcut('Ctrl+E')
        extractAction.setStatusTip('Extract I(V) from current selections')
        extractAction.triggered.connect(self.plot_leed_IV)
        LEEDMenu.addAction(extractAction)

        setEnergyAction = QtGui.QAction('Set Energy Parameters', self)
        setEnergyAction.triggered.connect(lambda: self.set_energy_parameters(dat='LEED'))
        LEEDMenu.addAction(setEnergyAction)

        # LEEM Menu
        LEEMMenu = self.menubar.addMenu('LEEM Actions')
        setEnergyAction = QtGui.QAction('Set Energy Parameters', self)
        setEnergyAction.triggered.connect(lambda: self.set_energy_parameters(dat='LEEM'))
        LEEMMenu.addAction(setEnergyAction)

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
                                                 "Enter a decimal for Starting Energy >0.0",
                                                 value=20.5, min=0.0, max=5000)
        if not ok:
            print('New Energy settings canceled ...')
            return
        start_e = float(entry)

        # Get Final Energy in eV
        entry, ok = QtGui.QInputDialog.getDouble(self, "Enter Final Energy in eV (must be larger than Start Energy)",
                                                 "Enter a decimal for Final Energy > Start Energy",
                                                 value=150, min=start_e, max=5000)
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
        self.LEED_IV_canvas.draw()

    def plot_leed_IV(self):
        """
        Loop through currently selected integration windows
        Extract Intensities from each window
        Plot I(V) then draw to canvas
        :return none:
        """

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
            if self.smth_leed_plot:
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