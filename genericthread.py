import sys
import time
from PyQt4 import QtCore, QtGui


class GenericThread(QtCore.QThread):
    """
    Subclass QThread to create thread for executing
    an arbitrary function
    Simplify run() by requiring all signal communication
    be handled solely within the parameter 'func'
    """
    # custom class level signals possibly implemented in future
    # may be useful to have a generic finished signal override

    def __init__(self, func, *args, **kwargs):
        super(QtCore.QThread, self).__init__()
        self.function = func
        self.args = args
        self.kwargs = kwargs

    def __del__(self):
        self.wait()

    def run(self):
        # print("self.args = " + str(self.args))
        # print("self.kwargs = " + str(self.kwargs))
        # print(self.function)
        if self.args and self.kwargs:
            self.function(*self.args, **self.kwargs)
        elif self.args and not self.kwargs:
            self.function(*self.args)
        elif self.kwargs and not self.args:
            self.function(**self.kwargs)
        else:
            self.function()
        return


# Test Purposes
class TestApp(QtGui.QWidget):
    """
    This class provides a minimal working example for usage of
    the GenericThread object.

    Signals are defined at the class level for communication between
    the QThread and the main GUI thread.

    A function, task, is defined and passed to GenericThread upon
    instantiation. This function and required parameters are executed
    in a separate QThread. Output from the function must be handled
    using Signals/Slots.

    Running this code from the main function creates a window with two
    buttons. One simply prints a test message when clicked. The second
    starts a new QThread and performs a long running execution. While
    this task executes the first button is still active. This indicated that the
    main GUI thread is not blocked by task execution in the new QThread.
    """
    # Class Level signals
    message_signal = QtCore.pyqtSignal(str, name='message')
    finished_signal = QtCore.pyqtSignal(name='finished')

    def __init__(self, parent=None):
        super(QtGui.QWidget, self).__init__(parent)
        self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle("Thread Testing")

        self.print_but = QtGui.QPushButton("Print", self)
        self.print_but.clicked.connect(self.print_test_message)

        self.task_but = QtGui.QPushButton("Task", self)
        self.task_but.clicked.connect(self.spawn_task)

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.print_but)
        hbox.addStretch()
        hbox.addWidget(self.task_but)

        self.setLayout(hbox)

        self.pool = []

    @staticmethod
    def print_test_message():
        print("Test Message ...")

    @QtCore.pyqtSlot(str)
    @staticmethod
    def retrieve_message(m):
        print('Retrieving message ...')
        print(str(m))

    @QtCore.pyqtSlot()
    @staticmethod
    def end():
        print("Execution Complete ...")

    def task(self, *args, **kwargs):
        secs, iters = 0, 0
        try:
            secs = kwargs['secs']
        except KeyError:
            print("Invalid kwarg in task() ...")
        try:
            iters = kwargs['iters']
        except KeyError:
            print("Invalid kwarg in task() ...")
        for i in range(iters):
            time.sleep(secs)
            self.message.emit("Execution iteration {} has finished.".format(i))

        # task has ended
        self.finished.emit()

    def spawn_task(self):
        print("Starting multithreaded execution ...")
        kwargs = {'secs': 5, 'iters': 10}
        self.gt = GenericThread(self.task, **kwargs)
        self.pool.append(self.gt)
        # Setup Signal/Slots
        try:
            self.message.disconnect()
        except:
            # if no slots are connected to message,
            # disconnect throws an exception
            # this situation is ok and we can continue
            # connecting message to a slot
            pass
        self.message.connect(self.retrieve_message)
        try:
            self.finished_signal.disconnect()
        except:
            # see above explanation
            pass
        self.finished_signal.connect(self.end)
        # start execution of thread
        self.pool[-1].start()


def main():
    app = QtGui.QApplication(sys.argv)
    ta = TestApp()
    ta.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
