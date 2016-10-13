import sys
import time
import numpy as np
# from genericthread import GenericThread
from PyQt4 import QtCore, QtGui
from queue import Queue


class MinimaCounterMT(QtCore.QObject):

    def __init__(self, data, num_threads):
        super(MinimaCounterMT, self).__init__()
        self.data_to_process = Queue()
        self.maxThreadCount = num_threads
        self.currentThreadCount = 0
        self.input_data = data
        self.coords = [(r, c) for r in range(self.input_data.shape[0])
                       for c in range(self.input_data.shape[1])]
        self.output_mask = np.zeros((self.input_data.shape[0],
                                    self.input_data.shape[1]))
        self.workers = []

    def start(self):
        print("Starting conditions:")
        print("Input Data Shape: {}".format(self.input_data.shape))
        print("Num Data Points to Process: {}".format(len(self.coords)))
        print("Placing input data onto Queue for processing ...")
        start = time.time()

        for coord in self.coords:
            self.data_to_process.put(coord)

        while self.currentThreadCount < self.maxThreadCount:
            self.workers.append(TaskWorker(queue=self.data_to_process,
                                           task=self.test_count_mins))
            self.currentThreadCount += 1

        # Threads have been instantiated
        # begin work
        for thread in self.workers:
            thread.start()
        working = True
        # wait for work to finish
        while working:
            for thread in self.workers:
                if thread.isFinished():
                    thread.terminate()
                    self.currentThreadCount -= 1
                    if self.currentThreadCount == 0:
                        working = False
        self.finish(start)

    def test_count_mins(self, data_point):
        r = data_point[0]
        c = data_point[1]
        self.output_mask[r, c] = -1
        time.sleep(1)  # simulate longer running calculation

    '''
    @QtCore.pyqtSlot(str)
    def decrement_thread_count(self, message):
        print("Recieved done_signal from thread ... {}".format(message))
        print("Decrementing Thread count.")
        self.currentThreadCount -= 1
    '''

    def finish(self, t):
        print("All workers have finished processing Data ...")
        print(self.output_mask)
        print("Elapsed: {}".format(time.time() - t))
        sys.exit(0)


class TaskWorker(QtCore.QThread):

    # done_signal = QtCore.pyqtSignal(str)

    def __init__(self, queue, task):
        super(TaskWorker, self).__init__(parent=None)
        self.work_queue = queue
        self.running = True
        self.task = task

    def run(self):
        while self.running:
            # check for work
            if not self.work_queue.empty():
                # execute task
                data_point = self.work_queue.get()
                self.task(data_point)
            else:
                # no work to do
                # print("Work complete - exiting Thread ...")
                self.running = False


def main():

    # max threads
    num_threads = 12

    app = QtGui.QApplication(sys.argv)
    data = np.zeros((5, 5, 5))  # 25 total data points to process
    cm = MinimaCounterMT(data, num_threads)
    cm.start()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
