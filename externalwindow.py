import matplotlib
matplotlib.use("Qt5agg", force=True)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5 import QtWidgets, QtCore


class ExternalWindow(QtWidgets.QWidget):
    """
    Generic Widget to contain 1 or 2 mpl plots
    """
    def __init__(self, size, num_plots=1, *args, **kwargs):
        super(QtWidgets.QWidget, self).__init__(parent=None)
        self.args = args
        self.kwargs = kwargs
        self.setMinimumSize(size[0], size[1])

        if num_plots == 1:
            self.fig, self.pltax = plt.subplots(1, num_plots, figsize=(8,6), dpi=100)
        elif num_plots == 2:
            self.fig, (self.imgax, self.pltax) = plt.subplots(1, num_plots, figsize=(8, 6), dpi=100)
        else:
            raise NotImplementedError
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                    QtWidgets.QSizePolicy.Expanding)
        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        self.setLayout(vbox)

    def closeEvent(self, QCloseEvent):
        # for line profile plots - We want to delete the line after closing window
        if 'canvas' in self.kwargs.keys() and 'line' in self.kwargs.keys():
            self.kwargs['line'].remove()
            self.kwargs['canvas'].draw()
        self.close()


