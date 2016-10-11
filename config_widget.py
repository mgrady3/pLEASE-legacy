import sys
from PyQt4 import QtGui, QtCore

class ConfigWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(QtGui.QWidget, self).__init__(parent)

        self.do_output = False
        self.data_dir = ''

        self.setWindowTitle("Enter settings for Experiment YAML File")
        self.title_label = QtGui.QLabel("Enter Settings to Save as YAML File")
        self.main_vbox = QtGui.QVBoxLayout()
        self.title_hbox = QtGui.QHBoxLayout()
        self.title_hbox.addStretch()
        self.title_hbox.addWidget(self.title_label)
        self.title_hbox.addStretch()
        self.main_vbox.addLayout(self.title_hbox)
        # self.main_vbox.addStretch()

        # file name
        # self.file_name_hbox = QtGui.QHBoxLayout()
        self.file_name_field = QtGui.QLineEdit()
        # regexp = QtCore.QRegExp('(.+?)(\.[^.]*$|$')
        # validator = QtGui.QRegExpValidator(regexp)
        # self.file_name_field.setValidator(validator)
        self.file_name_label = QtGui.QLabel("Enter filename without extension")
        # self.file_name_hbox.addWidget(self.file_name_field)
        # self.file_name_hbox.addWidget(self.file_name_label)
        # self.main_vbox.addLayout(self.file_name_hbox)

        # data directory
        # self.data_dir_hbox = QtGui.QHBoxLayout()
        self.data_button = QtGui.QPushButton("Select Data Dir", self)
        self.data_button.clicked.connect(self.select_data)
        self.data_label = QtGui.QLabel("Click to select a valid data directory")
        # self.data_dir_hbox.addWidget(self.data_button)
        # self.data_dir_hbox.addWidget(self.data_label)
        # self.main_vbox.addLayout(self.data_dir_hbox)

        # output directory
        self.output_dir_button = QtGui.QPushButton("Select Output Location", self)
        self.output_dir_button.clicked.connect(self.select_output_location)
        self.output_label = QtGui.QLabel("Click to select directory to store Experiment YAML file")

        # Exp type
        # self.exp_type_hbox = QtGui.QHBoxLayout()
        self.exp_type_menu = QtGui.QComboBox(self)
        self.exp_type_menu.addItem("LEED")
        self.exp_type_menu.addItem("LEEM")
        self.exp_type_label = QtGui.QLabel("Select Experiment Type")
        # self.exp_type_hbox.addWidget(self.exp_type_menu)
        # self.exp_type_hbox.addWidget(self.exp_type_label)
        # self.main_vbox.addLayout(self.exp_type_hbox)

        # Data type
        # self.data_type_hbox = QtGui.QHBoxLayout()
        self.data_type_menu = QtGui.QComboBox(self)
        self.data_type_menu.addItem("Image")
        self.data_type_menu.addItem("Raw")
        self.data_type_label = QtGui.QLabel("Select Data Type")
        # self.data_type_hbox.addWidget(self.data_type_menu)
        # self.data_type_hbox.addWidget(self.data_type_label)
        # self.main_vbox.addLayout(self.data_type_hbox)
        self.data_type_menu.currentIndexChanged.connect(self.toggle_image_type_active)

        # Image type
        # self.image_type_hbox = QtGui.QHBoxLayout()
        self.image_type_menu = QtGui.QComboBox(self)
        self.image_type_menu.addItem("TIFF")
        self.image_type_menu.addItem("PNG")
        self.image_type_label = QtGui.QLabel("Select Image Type")
        # self.image_type_hbox.addWidget(self.image_type_menu)
        # self.image_type_hbox.addWidget(self.image_type_label)
        # self.main_vbox.addLayout(self.image_type_hbox)

        grid = QtGui.QGridLayout()
        grid.addWidget(self.file_name_field, 1, 0)
        grid.addWidget(self.file_name_label, 1, 1)
        grid.addWidget(self.data_button, 2, 0)
        grid.addWidget(self.data_label, 2, 1)
        grid.addWidget(self.output_dir_button, 3, 0)
        grid.addWidget(self.output_label, 3, 1)
        grid.addWidget(self.exp_type_menu, 4, 0)
        grid.addWidget(self.exp_type_label, 4, 1)
        grid.addWidget(self.data_type_menu, 5, 0)
        grid.addWidget(self.data_type_label, 5, 1)
        grid.addWidget(self.image_type_menu, 6, 0)
        grid.addWidget(self.image_type_label, 6, 1)
        grid.setHorizontalSpacing(100)
        grid.setVerticalSpacing(15)

        self.main_vbox.addLayout(grid)

        # Data Params
        self.data_params_hbox = QtGui.QHBoxLayout()
        self.data_params_hbox.addStretch()
        self.data_params_label = QtGui.QLabel("--Data Parameters--")
        self.data_params_hbox.addWidget(self.data_params_label)
        self.data_params_hbox.addStretch()
        self.main_vbox.addStretch()
        self.main_vbox.addLayout(self.data_params_hbox)

        self.im_hbox = QtGui.QHBoxLayout()
        self.im_width_field = QtGui.QLineEdit()
        self.im_width_field.setValidator(QtGui.QIntValidator(bottom=0))
        self.im_width_label = QtGui.QLabel("Enter Image Width > 0")
        self.im_hbox.addWidget(self.im_width_field)
        self.im_hbox.addWidget(self.im_width_label)

        self.im_height_field = QtGui.QLineEdit()
        self.im_height_field.setValidator(QtGui.QIntValidator(bottom=0))
        self.im_height_label = QtGui.QLabel("Enter Image Height > 0")
        self.im_hbox.addWidget(self.im_height_field)
        self.im_hbox.addWidget(self.im_height_label)

        self.im_bits_menu = QtGui.QComboBox()
        self.im_bits_menu.addItem("8")
        self.im_bits_menu.addItem("16")
        self.im_bits_label = QtGui.QLabel("Select Image Bit Depth\n(only for Raw Data)")
        self.im_hbox.addWidget(self.im_bits_menu)
        self.im_hbox.addWidget(self.im_bits_label)

        self.im_byte_order_menu = QtGui.QComboBox()
        self.im_byte_order_menu.addItem("Little-Endian (Intel)")
        self.im_byte_order_menu.addItem("Big-Endian (Motorola)")
        self.im_byte_order_label = QtGui.QLabel("Select Byte-Order for raw data")
        self.im_hbox.addWidget(self.im_byte_order_menu)
        self.im_hbox.addWidget(self.im_byte_order_label)

        self.main_vbox.addLayout(self.im_hbox)

        # Energy Params
        self.energy_params_label_hbox = QtGui.QHBoxLayout()
        self.energy_params_label_hbox.addStretch()
        self.energy_params_label = QtGui.QLabel("--Energy Parameters--")
        self.energy_params_label_hbox.addWidget(self.energy_params_label)
        self.energy_params_label_hbox.addStretch()
        self.main_vbox.addStretch()
        self.main_vbox.addLayout(self.energy_params_label_hbox)

        self.energy_params_hbox = QtGui.QHBoxLayout()
        self.min_energy_field = QtGui.QLineEdit()
        self.min_energy_field.setValidator(QtGui.QDoubleValidator())
        self.min_energy_label = QtGui.QLabel("Enter Starting Energy in eV")
        self.max_energy_field = QtGui.QLineEdit()
        self.max_energy_field.setValidator(QtGui.QDoubleValidator())
        self.max_energy_label = QtGui.QLabel("Enter Final Energy in eV")
        self.step_energy_field = QtGui.QLineEdit()
        self.step_energy_field.setValidator(QtGui.QDoubleValidator())
        self.step_energy_label = QtGui.QLabel("Enter Step Energy in eV")

        self.energy_params_hbox.addWidget(self.min_energy_field)
        self.energy_params_hbox.addWidget(self.min_energy_label)
        self.energy_params_hbox.addStretch()
        self.energy_params_hbox.addWidget(self.max_energy_field)
        self.energy_params_hbox.addWidget(self.max_energy_label)
        self.energy_params_hbox.addStretch()
        self.energy_params_hbox.addWidget(self.step_energy_field)
        self.energy_params_hbox.addWidget(self.step_energy_label)
        self.main_vbox.addLayout(self.energy_params_hbox)

        self.main_vbox.addStretch()
        self.end_button_hbox = QtGui.QHBoxLayout()
        self.cancel_button = QtGui.QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(lambda: self.close())
        self.ok_button = QtGui.QPushButton("Ok", self)
        self.ok_button.clicked.connect(self.validate)
        self.end_button_hbox.addStretch()
        self.end_button_hbox.addWidget(self.cancel_button)
        self.end_button_hbox.addWidget(self.ok_button)
        self.main_vbox.addLayout(self.end_button_hbox)

        self.setLayout(self.main_vbox)

        # Center on Screen
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))
        self.show()

    def select_data(self):
        self.data_dir = QtGui.QFileDialog.getExistingDirectory(caption="Select Data Directory")
        return

    def select_output_location(self):
        self.output_dir = QtGui.QFileDialog.getExistingDirectory(caption="Select location to output .yaml file")
        return

    def toggle_image_type_active(self):
        if str(self.data_type_menu.currentText()) == 'Image':
            self.image_type_menu.setEnabled(True)
            self.im_bits_menu.setEnabled(False)
            self.im_byte_order_menu.setEnabled(False)
        else:
            self.image_type_menu.setEnabled(False)
            self.im_bits_menu.setEnabled(True)
            self.im_byte_order_menu.setEnabled(True)

    def validate(self):
        """
        User Input must be validated so that the output .yaml file
        is able to correctly be read in to load a data set in the future


        """
        print("Validating input ...")

        # file name validation:
        output_name = str(self.file_name_field.text())
        if output_name == '' or output_name is None:
            print("Error: No file name provided.")
            return
        else:
            # add file extension
            output_name += '.yaml'

        output_dir = str(self.output_dir)
        if output_dir == '':
            print("Error: Invalid Output Dir selected ...")
            return

        # Exp type validation:
        exp_type = str(self.exp_type_menu.currentText())
        if exp_type not in ["LEED", "LEEM"]:
            # note: this shouldn't be possible
            print("Error: Invalid Experiment type")
            return

        # Data type validation:
        data_type = str(self.data_type_menu.currentText())
        if data_type not in ["Image", "Raw"]:
            # note: this shouldn't be possible
            print("Error: Invalid Experiment type")
            return

        if data_type == 'Image':
            # Image Type Validation
            image_type = str(self.image_type_menu.currentText())
            if image_type not in ["TIFF", "PNG"]:
                # shouldn't be possible
                print("Error: Invalid Image Type")
        else:
            image_type = None

        # Data param validation:
        im_width = str(self.im_width_field.text())
        try:
            im_width = int(im_width)
        except ValueError:
            print("Error: Image Width must be an integer.")
            return
        if im_width <= 0:
            print("Error: Image Width must be >= 0.")
            return

        im_height = str(self.im_height_field.text())
        try:
            im_height = int(im_height)
        except ValueError:
            print("Error: Image Height must be an integer.")
            return
        if im_height <= 0:
            print("Error: Image Height must be >= 0.")
            return

        if data_type == 'Raw':
            # Bit Depth validation:
            im_bits = str(self.im_bits_menu.currentText())
            try:
                im_bits = int(im_bits)
            except ValueError:
                # shouldn't be possible
                print("Error: Invalid image bit depth. Non-integer")
                return
            if im_bits not in [8, 16]:
                print("Error: Invalid image bit depth. Only 8-bit and 16-bit images supported")
                return

            im_byte_order = str(self.im_byte_order_menu.currentText())
            if im_byte_order not in ["Little-Endian (Intel)", "Big-Endian (Motorola)"]:
                # shouldn't be possible
                print("Error: Invalid Byte Order Specified")
                return
        else:
            im_bits = None
            im_byte_order = None

        # Energy Param validation:
        start_e = str(self.min_energy_field.text())
        try:
            start_e = float(start_e)
        except ValueError:
            print("Error: Invalid value for starting energy.")
            return

        end_e = str(self.max_energy_field.text())
        try:
            end_e = float(end_e)
        except ValueError:
            print("Error: Invalid value for final energy.")
            return

        if start_e >= end_e:
            print("Error: Final energy must be greater than Starting energy.")
            return

        step_e = str(self.step_energy_field.text())
        try:
            step_e = float(step_e)
        except ValueError:
            print("Error: Invalid step energy.")
            return

        if step_e <= 0:
            print("Error: Step energy must be greater than 0.")
            return

        # Data Dir validation:
        data_dir = str(self.data_dir)
        if data_dir == '':
            print("Error: Invalid Data Directory.")
            return

        output_params = {"Output File Name": output_name,
                         "Output Dir": output_dir,
                         "Data Dir": data_dir,
                         "Exp Type": exp_type,
                         "Data Type": data_type,
                         "Image Type": image_type,
                         "Width": im_width,
                         "Height": im_height,
                         "Bits": im_bits,
                         "Byte Order": im_byte_order,
                         "Min Energy": start_e,
                         "Max Energy": end_e,
                         "Step Energy": step_e}
        # print("emitting Output Params as SIGNAL ...")
        self.emit(QtCore.SIGNAL('output(PyQt_PyObject)'), output_params)
        self.do_output = True
        self.close_widget()

    def close_widget(self):
        if self.do_output:
            self.emit(QtCore.SIGNAL('close'))
        self.close()


def main():
    app = QtGui.QApplication(sys.argv)
    cw = ConfigWidget()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
