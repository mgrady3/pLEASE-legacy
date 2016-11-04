import os
import sys
from PyQt4 import QtGui, QtCore


class GenDatWindow(QtGui.QWidget):
    """

    """

    def __init__(self, parent=None):
        super(QtGui.QWidget, self).__init__(parent)

        self.setWindowTitle("Enter Image Settings")

        indir_hbox = QtGui.QHBoxLayout()
        self.indir_button = QtGui.QPushButton("Select Input Directory", self)
        self.indir_textarea = QtGui.QLineEdit(self)
        indir_hbox.addWidget(self.indir_button)
        indir_hbox.addWidget(self.indir_textarea)
        self.indir_button.clicked.connect(self.getInputDirectory)

        outdir_hbox = QtGui.QHBoxLayout()
        self.outdir_button = QtGui.QPushButton("Select Output Directory", self)
        self.outdir_textarea = QtGui.QLineEdit(self)
        indir_hbox.addWidget(self.outdir_button)
        indir_hbox.addWidget(self.outdir_textarea)
        self.outdir_button.clicked.connect(self.getOutputDirectory)

        self.image_type_menu = QtGui.QComboBox(self)
        self.image_type_menu.addItem("TIFF")
        self.image_type_menu.addItem("PNG")


    def getInputDirectory(self):
        pass

    def getOutputDirectory(self):
        pass

    def parseSettings(self):
        pass
