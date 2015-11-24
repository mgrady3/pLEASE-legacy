"""
Define sub-class/sub-classes of QThread
These define a model for worker threads
The main thread responsible for GUI work
can then start a worker thread to do a
computationally intensive task or an I/O
bound task

Common tasks for the worker thread will be:
    Loading raw data files from disk to
    memory
    Outputting IV-data to text files(s)

"""

import os
import LEEMFUNCTIONS as LF
import numpy as np
from PyQt4 import QtGui, QtCore

# TODO: Consider splitting to multiple classes for separate tasks
class WorkerThread(QtCore.QThread):
    """
    Worker Thread to execute specific tasks which
    may otherwise block the main UI
    """
    def __init__(self, task=None, **kwargs):
        super(WorkerThread, self).__init__()
        self.task = task
        self.params = kwargs
        print('Thread created: inside init')
        print('TESTING: # params = {}'.format(len(self.params)))

    def run(self):
        """
        # Overload the QThread run() method to do specific tasks
        :return none:
        """
        if self.task is None:
            print('Terminating - No task to execute ...')
            self.terminate()
        elif self.task == 'LOAD_LEED':
            pass

        elif self.task == 'LOAD_LEEM':
            pass

        elif self.task == 'OUTPUT_TO_TEXT':
            pass

        elif self.task == 'COUNT_MINIMA':
            pass

        else:
            print('Terminating: Unknown task ...')
            self.terminate()