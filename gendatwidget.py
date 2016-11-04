import os
import sys
from PyQt4 import QtGui, QtCore


class GenDatWindow(QtGui.QWidget):
    """

    """

    def __init__(self, parent=None):
        super(QtGui.QWidget, self).__init__(parent)

        self.setWindowTitle("Enter Image Settings")

        main_vbox = QtGui.QVBoxLayout()

        indir_hbox = QtGui.QHBoxLayout()
        self.indir_button = QtGui.QPushButton("Select Input Directory", self)
        self.indir_textarea = QtGui.QLineEdit(self)
        indir_hbox.addWidget(self.indir_button)
        indir_hbox.addWidget(self.indir_textarea)
        self.indir_button.clicked.connect(self.getInputDirectory)
        main_vbox.addLayout(indir_hbox)

        outdir_hbox = QtGui.QHBoxLayout()
        self.outdir_button = QtGui.QPushButton("Select Output Directory", self)
        self.outdir_textarea = QtGui.QLineEdit(self)
        indir_hbox.addWidget(self.outdir_button)
        indir_hbox.addWidget(self.outdir_textarea)
        self.outdir_button.clicked.connect(self.getOutputDirectory)
        main_vbox.addLayout(outdir_hbox)

        image_type_hbox = QtGui.QHBoxLayout()
        self.image_type_menu = QtGui.QComboBox(self)
        self.image_type_menu.addItem("TIFF")
        self.image_type_menu.addItem("PNG")
        self.image_label = QtGui.QLabel("Select Input Image Type")
        image_type_hbox.addWidget(self.image_type_menu)
        image_type_hbox.addWidget(self.image_label)
        main_vbox.addLayout(image_type_hbox)

        main_vbox.addWidget(self.h_line())

        self.test_button = QtGui.QPushButton("Test ...", self)
        main_vbox.addWidget(self.test_button)

        self.setLayout(main_vbox)
        self.show()

    def h_line(self):
        f = QtGui.QFrame()
        f.setFrameShape(QtGui.QFrame.HLine)
        f.setFrameShadow(QtGui.QFrame.Sunken)
        return f

    def getInputDirectory(self):
        pass

    def getOutputDirectory(self):
        pass

    def parseSettings(self):
        pass


def main():
    app = QtGui.QApplication(sys.argv)


if __name__ == '__main__':
    main()
