"""
This module contains classes pertinent
to creating 'terminal-esque' Qt widgets
which are capable of capturing the
standard python sys.std_out to display
messages to the User rather than through
the Terminal or Python Interpreter.

Maxwell Grady 2015
"""
import sys
from PyQt4 import QtCore, QtGui


class CustomStream(QtCore.QObject):
    """
    Custom class for sending messages to an arbitrary QWidget
    Used for re-routing sys.stdout to display messages and errors in
    a separate window instead of the python console
    """
    # define custom signal to be emitted
    # and sent to a text-based QWidget like QTextEdit

    message = QtCore.pyqtSignal(str)

    def __init__(self):
        # QObject.__init__()
        super(CustomStream, self).__init__()

    def write(self, message):
        # forgo a try:except loop here as generally all necessary objects can be cast
        # to string in python: int, float, list, None, True/False, etc...
        # should not have a problem with this type-casting
        self.message.emit(str(message))  # manually cast in-case of incorrect input

    def flush(self):
        # fix to allow usage with multiprocessing
        pass


class ErrorConsole(QtGui.QWidget):
    """
    Custom QWidget to receive messages from sys.stdout
    This serves as a way to send Error messages to the User rather
    than having the user monitor the python console
    """

    _light = False  # boolean Flag for style formatting

    def __init__(self, parent=None):
        # pass None to parent in QWidget.__init__()
        # this is a top-level widget
        super(ErrorConsole, self).__init__(parent)
        # widget to receive and display messages from custom_stream ie. std_out
        self.textEdit = QtGui.QTextEdit()
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.textEdit)
        self.setLayout(vbox)

        # style formatting

        font = QtGui.QFont()
        font.setFamily('Menlo')
        font.setFixedPitch(True)
        font.setPointSize(16)
        self.textEdit.setFont(font)

        if not self._light:
            # dark style
            # use rgba for the QWidget background. This allows setting alpha channel transparency
            self.setStyleSheet('background-color: rgba(36, 35, 35, 200)')
            self.textEdit.setStyleSheet('color: rgb(238, 232, 213)')
        else:
            # light style
            self.setStyleSheet('background-color: rgba(253, 246, 227, 200)')
            self.textEdit.setStyleSheet("QTextEdit {color: black}")
        
        # connect custom signal to pre-defined slot self.set_message
        self.stream = CustomStream()
        self.stream.message.connect(self.set_message)
        
        # re-route sys.stdout and sys.stderr
        
        sys.stdout = self.stream
        sys.stderr = self.stream
        self.show()
        
    def closeEvent(self, event):
        """
        Override closeEvent to ensure sys.stdout and sys.stderr
        are properly reset when 'terminal' widget is closed
        :param event: receive a 'window close event'
        :return none:
        """
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        # Now call standard QWidget.closeEvent() to continue as normal with
        # close window mechanism
        super(ErrorConsole, self).closeEvent(event)

    @QtCore.pyqtSlot(str)
    def set_message(self, message):
        """
        PyQt Slot to receive the signal emitted by CustomStream
        :param message: string text signal emitted from CustomStream
                        This is either a message to sys.stdout or a message from
                        sys.stderr
        :return none:
        """
        # display received message in plaintext at bottom of widget
        self.textEdit.moveCursor(QtGui.QTextCursor.End)
        self.textEdit.insertPlainText(message)
