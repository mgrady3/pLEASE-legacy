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
                           'imht', 'imwd', 'name']
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
            self.load_LEED()
            self.quit()
            self.exit()  # restrict action to one task

        elif self.task == 'LOAD_LEEM':
            self.load_LEEM()
            self.quit()
            self.exit()  # restrict action to one task

        elif self.task == 'OUTPUT_TO_TEXT':
            self.output_to_Text()
            self.quit()
            self.exit()  # restrict action to one task

        elif self.task == 'COUNT_MINIMA':
            self.count_Minima()
            self.quit()
            self.exit()  # restrict action to one task

        else:
            print('Terminating: Unknown task ...')
            self.quit()
            self.exit()

    def load_LEED(self):
        """
        Load raw binary LEED-IV data to a 3d numpy array
        emit the numpy array as a custom SIGNAL to be retrieved in gui.py
        :return:
        """
        # requires params: path, imht, imwd
        if ( 'path' not in self.params.keys() or
             'imht' not in self.params.keys() or
             'imwd' not in self.params.keys()):

            print('Terminating - ERROR: incorrect parameters for LOAD task')
            print('Required Parameters: path, imht, imwd')
            self.quit()
            self.exit()

        # load raw data
        dat_3d = LF.process_LEEM_Data(dirname=self.params['path'],
                                      ht=self.params['imht'],
                                      wd=self.params['imwd'])

        # emit output signal with np array as generic pyobject type
        self.emit(QtCore.SIGNAL('output(PyQt_PyObject)'), dat_3d)

    def load_LEEM(self):
        """
        Load raw binary LEEM-IV data to a 3d numpy array
        emit the numpy array as a custom SIGNAL to be retrieved in gui.py
        :return:
        """
        # requires params: path, imht, imwd
        if ( 'path' not in self.params.keys() or
             'imht' not in self.params.keys() or
             'imwd' not in self.params.keys()):

            print('Terminating - ERROR: incorrect parameters for LOAD task')
            print('Required Parameters: path, imht, imwd')
            self.quit()
            self.exit()

        # load raw data
        dat_3d = LF.process_LEEM_Data(dirname=self.params['path'],
                                      ht=self.params['imht'],
                                      wd=self.params['imwd'])

        # emit output signal with np array as generic pyobject type
        self.emit(QtCore.SIGNAL('output(PyQt_PyObject)'), dat_3d)

    def output_to_Text(self):
        """

        :return:
        """
        # requires params: path, ilist, elist, name
        filename = self.params['name']
        elist = self.params['elist']
        ilist = self.params['ilist']
        print('Writing to file {} ...'.format(filename))
        with open(filename, 'w') as f:
            f.write('E' + '\t' + 'I' + '\n')

            # TODO: see if its better to do smthn like  for e, i in zip(elist, ilist)): ...
            for index, item in enumerate(elist):
                f.write(str(item) + '\t' + str(ilist[index]) + '\n')



    def count_Minima(self):
        """

        :return:
        """
        # requires params: data, elist
        pass