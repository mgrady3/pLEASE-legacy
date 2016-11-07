import LEEMFUNCTIONS as LF
from qthreads import WorkerThread

import os
import pprint
import sys

import numpy as np
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

        print("Use Window to Enter file settings then click OutputFiles ...")

        self.show()

    def h_line(self):
        f = QtGui.QFrame()
        f.setFrameShape(QtGui.QFrame.HLine)
        f.setFrameShadow(QtGui.QFrame.Sunken)
        return f

    def getInputDirectory(self):
        self.indir = str(QtGui.QFileDialog.getExistingDirectory(parent=None,
                                                                caption="Select Directory Containing Input Files"))
        if self.indir:
            # not None
            self.indir_textarea.setText(self.indir)
        return

    def getOutputDirectory(self):
        self.outdir = str(QtGui.QFileDialog.getExistingDirectory(parent=None,
                                                                 caption="Select Directory for Output Files"))
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

        self.height = int(self.height_text.text())
        if not self.height:
            print("Enter a height.")
            return

        self.width = int(self.width_text.text())
        if not self.width:
            print("Enter a height.")
            return

        self.bit_depth = self.depth_menu.currentText()

    def processInputFiles(self):
        if self.image_type == "TIFF":
            exts = [".tiff", ".TIFF", ".tif", ".TIF"]
        elif self.image_type == "PNG":
            exts = [".png", ".PNG"]
        else:
            print("Error: Unknown Image Type {}".format(self.image_type))
            return False
        self.files = []
        for ext in exts:
            for name in os.listdir(self.indir):
                if name.endswith(ext):
                    self.files.append(name)
        if not self.files:
            print("Error: No Files found in directory {} with extensions {}".format(self.indir, exts))
            return False

        if self.image_type in ['.tif', '.tiff', '.TIF', '.TIFF']:
            try:
                print('Parsing file {0}'.format(os.path.join(self.indir, self.files[0])))
                self.byte_order = LF.parse_tiff_header(os.path.join(self.indir, self.files[0]), self.widthw, self.heighth, self.bit_depth)
            except LF.ParseError as e:
                print("Failed to parse tiff header; defaulting to big endian bye order")
                print(e.message)
                print(e.errors)
                byte_order = 'B'  # default to big endian
        else:
            # PNG and JPEG always use Big Endian
            self.byte_order = 'B'  # default to big endian

        # swap to numpy syntax
        if self.byte_order == 'L':
            self.byte_order = '<'
        elif self.byte_order == 'B':
            self.byte_order = '>'

        if self.bit_depth == '16-bit':
            self.bytes_per_pixel = 2
        elif self.bit_depth == '8-bit':
            self.bytes_per_pixel = 1
        else:
            print("Error: Unknown image bit_depth. Only 8bit and 16-bit images can be processed.")
            return False

        # All settings are ready to output files
        return True

    def outputFiles(self):
        self.parseSettings()
        output_settings = self.processInputFiles()
        print('Found {0} files to process with the following settings:'.format(len(self.files)))
        settings = {"indir": self.indir,
                    "outdir": self.outdir,
                    "image_type:": self.image_type,
                    "height:": self.height,
                    "width": self.width,
                    "depth": self.bit_depth}
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(settings)

        # The following needs to happen in a separate thread from the main GUI thread.
        # The task will be I/O bound and will freeze the main GUI unless
        # execution happens in a separate QThread.
        if output_settings:
            self.thread = WorkerThread(task='GEN_DAT_FILES',
                                       path=self.indir,
                                       outpath=self.outdir,
                                       files=self.files,
                                       imht=self.height,
                                       imwd=self.width,
                                       bits=self.bytes_per_pixel,
                                       byte=self.byte_order
                                       )
            self.thread.done.connect(self.outputFinished)
            print("Beginning File Output ...")
            self.thread.start()
        else:
            print("Error Parsing Input Files ...")
            return
        """
        if output_settings:
            for file in self.files:
                # get input data from file
                with open(os.path.join(self.indir, file), 'rb') as infile:
                    header = len(infile.read()) - self.bytes_per_pixel * self.width * self.height
                    infile.seek(0)
                    fmtstr = self.byte_order + 'u' + str(self.bytes_per_pixel)
                    # strip header information
                    data = np.fromstring(infile.read()[header:], fmtstr).reshape((self.height, self.width))
                    with open(os.path.join(self.outdir, file.split('.')[0]+'.dat'), 'wb') as outfile:
                        data.tofile(outfile)
            print("Done outputting dat files ...")
            self.close()
        else:
            print("Error Parsing Input Files ...")
            return
        """

    @QtCore.pyqtSlot()
    def outputFinished(self):
        print("Done Outputting .dat Files")
        self.close()

def main():
    app = QtGui.QApplication(sys.argv)
    win = GenDatWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
