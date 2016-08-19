"""
Define sub-class/sub-classes of QThread
these define a model for worker threads.
The main thread responsible for GUI work
can then start a worker thread to do a
computationally intensive task or an I/O
bound task without blocking usage of the UI.

Common tasks for the worker thread will be:
    Loading raw data files from disk to
    memory
    Outputting IV-data to text files(s)

"""

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
        # Get parameters as dictionary and validate against keys
        self.params = kwargs
        self.valid_keys = ['path', 'data', 'ilist', 'elist',
                           'imht', 'imwd', 'name', 'bits', 'ext', 'byte']
        for key in self.params.keys():
            if key not in self.valid_keys:
                print('Terminating - ERROR Invalid Task Parameter: {}'.format(key))
                print('Valid Parameters are: {}'.format(self.params.keys()))
                self.quit()
                self.exit()

    # TODO: better method to implement thread tasks instead of overloading run()
    # Work has been started in git branch dev_updateThreading
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

        elif self.task == 'LOAD_LEED_IMAGES':
            self.load_LEED_Images()
            self.quit()
            self.exit()

        elif self.task == 'LOAD_LEEM':
            self.load_LEEM()
            self.quit()
            self.exit()  # restrict action to one task

        elif self.task == 'LOAD_LEEM_IMAGES':
            self.load_LEEM_Images()
            self.quit()
            self.exit() # restrict action to one task

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

        if 'bits' not in self.params.keys():
            # if bit size is not specified, use default values in process_LEEM_Data()
            self.params['bits'] = None

        if 'byte' not in self.params.keys():
            self.params['byte'] = 'L'  # default to Little Endian

        # load raw data
        dat_3d = LF.process_LEEM_Data(dirname=self.params['path'],
                                      ht=self.params['imht'],
                                      wd=self.params['imwd'],
                                      bits=self.params['bits'],
                                      byte=self.params['byte'])

        # emit output signal with np array as generic pyobject type
        self.emit(QtCore.SIGNAL('output(PyQt_PyObject)'), dat_3d)

    def load_LEED_Images(self):
        """
        Load LEED data from image files
        Supported formats are TIFF, PNG, JPG
        emit the 3d data array as a custom SIGNAL to be retrieved in gui.py
        """
        if ('path' not in self.params.keys() or
            'ext' not in self.params.keys()):
            print('Terminating - ERROR: incorrect parameters for LOAD task')
            print('Required Parameters: path, ext')
        print('Loading LEED Data from Images via QThread ...')

        """
        if 'byte' in self.params.keys():
            if self.params['byte'] == 'L':
                swap = False
            elif self.params['byte'] == 'B':
                print("Byte order set as Big-Endian - swapping order when plotting data ...")
                swap = True
            else:
                swap = False
                print("Error reading byte order from experimental config ...")
        """
        data = LF.get_img_array(self.params['path'], ext=self.params['ext'], swap=False)
        if data is None:
            self.quit()
            self.exit()
        else:
            self.emit(QtCore.SIGNAL('output(PyQt_PyObject)'), data)

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

        if 'bits' not in self.params.keys():
            # if bit size is not specified, use default values in process_LEEM_Data()
            self.params['bits'] = None

        if 'byte' not in self.params.keys():
            self.params['byte'] = 'L'  # default to Little Endian

        # load raw data
        dat_3d = LF.process_LEEM_Data(dirname=self.params['path'],
                                      ht=self.params['imht'],
                                      wd=self.params['imwd'],
                                      bits=self.params['bits'],
                                      byte=self.params['byte'])

        # emit output signal with np array as generic pyobject type
        self.emit(QtCore.SIGNAL('output(PyQt_PyObject)'), dat_3d)

    def load_LEEM_Images(self):
        """
        """
        if ('path' not in self.params.keys() and
                    'ext' not in self.params.keys()):
            print('Terminating - ERROR: incorrect parameters for LOAD task')
            print('Required Parameters: path, ext')
        print('Loading LEEM Data from Images via QThread ...')
        try:
            data = LF.get_img_array(self.params['path'],
                                    ext=self.params['ext'])
        except IOError as e:
            print(e)
            print('Error occurred while loading LEEM data from images using a QThread')
            return
        except ValueError as e:
            print(e)
            print('Error occurred while loading LEEM data from images using a QThread')
            return

        self.emit(QtCore.SIGNAL('output(PyQt_PyObject)'), data)

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

            for index, item in enumerate(elist):
                f.write(str(item) + '\t' + str(ilist[index]) + '\n')

    def count_Minima(self):
        """

        :return:
        """
        # requires params: data, elist
        pass
