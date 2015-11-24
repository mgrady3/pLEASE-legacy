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

    task: string describing task to be completed by worker thread

    kwargs:
        path: string path to data to load or directory to output into
        data: numpy array of data to perform a calculation on or output to text
        ilist: list of intensity values to output to text
        elist: list of energy values in eV in single decimal format to be used for
                calculations or for outputting to text
        imht: integer image height dimension
        imwd: integer image width dimension
    """
    def __init__(self, task=None, **kwargs):
        super(WorkerThread, self).__init__()
        self.task = task
        # Get parameters and validate
        self.params = kwargs
        self.valid_keys = ['path', 'data', 'ilist', 'elist',
                           'imht', 'imwd']
        for key in self.params.keys():
            if key not in self.valid_keys:
                print('Terminating - ERROR Invalid Task Parameter: {}'.format(key))
                print('Valid Parameters are: {}'.format(self.params.keys()))
                self.quit()
                self.exit()

    def run(self):
        """
        # Overload the QThread run() method to do specific tasks
        :return none:
        """
        if self.task is None:
            print('Terminating - No task to execute ...')
            self.quit()
            self.exit()
        elif self.task == 'LOAD_LEED':
            # requires params: path, imht, imwd
            if ( 'path' not in self.params.keys() or
                 'imht' not in self.params.keys() or
                 'imwd' not in self.params.keys()):

                print('Terminating - ERROR: incorrect parameters for LOAD task')
                print('Required Parameters: path, imht, imwd')
                self.quit()
                self.exit()

            dat_3d = LF.process_LEEM_Data(dirname=self.params['path'],
                                          ht=self.params['imht'],
                                          wd=self.params['imwd'])

            # emit output signal with np array as generic pyobject type
            self.emit(QtCore.SIGNAL('output(PyQt_PyObject)'), dat_3d)
            self.quit()
            self.exit()  # restrict action to one task

        elif self.task == 'LOAD_LEEM':
            # requires params: path, imht, imwd
            pass

        elif self.task == 'OUTPUT_TO_TEXT':
            # requires params: path, ilist, elist
            pass

        elif self.task == 'COUNT_MINIMA':
            # requires params: data, elist
            pass

        else:
            print('Terminating: Unknown task ...')
            self.quit()
            self.exit()