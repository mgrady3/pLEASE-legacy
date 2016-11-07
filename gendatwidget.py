import pprint
import sys
from PyQt4 import QtGui


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

        # self.test_button = QtGui.QPushButton("Test ...", self)
        # main_vbox.addWidget(self.test_button)

        setting_hbox = QtGui.QHBoxLayout()
        self.height_label = QtGui.QLabel("Enter Image Height (int)")
        self.height_text = QtGui.QLineEdit(self)
        setting_hbox.addWidget(self.height_label)
        setting_hbox.addWidget(self.height_text)

        self.width_label = QtGui.QLabel("Enter Image Width (int)")
        self.width_text = QtGui.QLineEdit(self)
        setting_hbox.addWidget(self.width_label)
        setting_hbox.addWidget(self.width_text)

        self.depth_label = QtGui.QLabel("Select Image Byte Depth")
        self.depth_menu = QtGui.QComboBox(self)
        self.depth_menu.addItem("8-bit")
        self.depth_menu.addItem("16-bit")
        setting_hbox.addWidget(self.depth_label)
        setting_hbox.addWidget(self.depth_menu)
        main_vbox.addLayout(setting_hbox)

        main_vbox.addWidget(self.h_line())

        button_box = QtGui.QHBoxLayout()
        button_box.addStretch()
        self.cancel_button = QtGui.QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(lambda: self.close())
        self.output_button = QtGui.QPushButton("Output Files", self)
        self.output_button.clicked.connect(self.outputFiles)
        button_box.addWidget(self.cancel_button)
        button_box.addWidget(self.output_button)

        main_vbox.addLayout(button_box)

        self.setLayout(main_vbox)

        self.indir = None
        self.outdir = None
        self.height = None
        self.width = None


        self.show()

    def h_line(self):
        f = QtGui.QFrame()
        f.setFrameShape(QtGui.QFrame.HLine)
        f.setFrameShadow(QtGui.QFrame.Sunken)
        return f

    def getInputDirectory(self):
        self.indir = str(QtGui.QFileDialog.getExistingDirectory(parent=None, caption="Select Directory Containing Input Files"))
        if self.indir:
            # not None
            self.indir_textarea.setText(self.indir)
        return

    def getOutputDirectory(self):
        self.outdir = str(QtGui.QFileDialog.getExistingDirectory(parent=None, caption="Select Directory for Output Files"))
        if self.outdir:
            # not None
            self.outdir_textarea.setText(self.outdir)
        return

    def parseSettings(self):
        if not self.outdir:
            print("Select an Output Directory.")
            return
        if not self.indir:
            print("Select an Input Directory")

        self.image_type = self.image_type_menu.currentText()

        self.height = self.height_text.text()
        if not self.height:
            print("Enter a height.")
            return

        self.width = self.width_text.text()
        if not self.width:
            print("Enter a height.")
            return

        self.bit_depth = self.depth_menu.currentText()

    def outputFiles(self):
        self.parseSettings()
        settings = {"indir":self.indir,
                    "outdir":self.outdir,
                    "image_type:":self.image_type,
                    "height:":self.height,
                    "width":self.width,
                    "depth":self.bit_depth}
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(settings)


def main():
    app = QtGui.QApplication(sys.argv)
    win = GenDatWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
