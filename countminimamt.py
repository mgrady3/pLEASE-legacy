import sys
import time
import numpy as np
from genericthread import GenericThread
from PyQt4 import QtCore, QtGui


# last resort come back to a fully custom implementation
class CustomThreadPool(QtCore.QObject):
    def __init__(self):
        super(CustomThreadPool, self).__init__()
        self.threads = []

    def add_thread(self, thread):
        self.threads.append(thread)


class GenericRunnable(QtCore.QRunnable):
    """Adaptation of GenericThread to subclass QRunnable
        for use with QThreadPool
    """
    def __init__(self, func, *args, **kwargs):
        super(QtCore.QThread, self).__init__()
        self.function = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        if self.args and self.kwargs:
            self.function(*self.args, **self.kwargs)
        elif self.args and not self.kwargs:
            self.function(*self.args)
        elif self.kwargs and not self.args:
            self.function(**self.kwargs)
        else:
            self.function()
        return


class MinimaCounterMT(QtCore.QObject):
    """
    """
    output_signal = QtCore.pyqtSignal('PyQt_PyObject')
    thread_finished_signal = QtCore.pyqtSignal()

    def __init__(self, dat_3d):
        super(MinimaCounterMT, self).__init__()
        # self.pool = QtCore.QThreadPool.globalInstance()
        # self.pool.setMaxThreadCount(4)
        self.maxThreadCount = 4
        self.currentThreadCount = 0
        self.threads = []
        self.input_data = dat_3d
        self.coords = [(r, c) for r in range(self.input_data.shape[0])
                       for c in range(self.input_data.shape[1])]
        self.output_mask = np.zeros((self.input_data.shape[0],
                                    self.input_data.shape[1]))

    def start(self):
        print("Starting conditions:")
        print("Input Data Shape: {}".format(self.input_data.shape))
        print("Num Data Points to Process: {}".format(len(self.coords)))

        self.output_signal.connect(self.fill_mask)
        self.thread_finished_signal.connect(self.decrement_count)
        while self.coords:
            if self.currentThreadCount < self.maxThreadCount:
                dp = self.coords.pop()
                kwargs = {'data': self.input_data, 'coord': dp}
                gt = GenericThread(self.count_mins, **kwargs)
                self.currentThreadCount += 1
                print("Num ActiveThreads = {}".format(self.currentThreadCount))

                # self.pool.start(gt)
                self.threads.append(gt)
                gt.start()

        # last data point has been passed off for processing
        while self.currentThreadCount > 0:
            # wait for threads to finish
            pass

        # all data has been processed
        self.final_output()

    @QtCore.pyqtSlot('PyQt_PyObject')
    def fill_mask(self, package):
        print("output signal recieved")
        coord = package[0]
        num_min = package[1]
        self.output_mask[coord[0], coord[1]] = num_min

    @QtCore.pyqtSlot()
    def decrement_count(self):
        print("thread finished signal recieved")
        self.currentThreadCount -= 1
        print("Num Active Threads = {}".format(self.currentThreadCount))

    def count_mins(self, **kwargs):
        coord = None  # default value
        try:
            coord = kwargs['coord']  # value passed into thread
        except KeyError:
            print("Invalid Key in params passed to count_mins")
        time.sleep(1)  # simulate long running task
        # print("count_mins called and sleep finished ... ")
        package = [coord, -1]
        self.output_signal.emit(package)
        self.thread_finished_signal.emit()
        return

    def final_output(self):
        print(self.output_mask)


def main():
    app = QtGui.QApplication(sys.argv)
    data = np.zeros((5, 5, 5))
    cm = MinimaCounterMT(data)
    start = time.time()
    cm.start()
    finish = time.time()
    print("Elapsed: {}".format(finish - start))
    sys.exit(app.exec_)


if __name__ == '__main__':
    main()

