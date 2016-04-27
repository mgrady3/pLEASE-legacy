"""
New method of implementing Qthreads for executing long running operations
This is the more proper way of using QThreads instead of just subclassing
and overloading run()

"""
import LEEMFUNCTIONS as LF
from PyQt4 import QtCore


class Worker(QtCore.QObject):
    """
    Generic worker object
    Will execute long running code in a separate QThread so as to not block the main GUI thread
    Any valid task and its associated inputs are parsed in work_to_do which is pushed to
    a new QThread
    """
    finished = QtCore.pyqtSignal()

    def __init__(self, task=None, **kwargs):
        """
        :param task: String associated with various Data I/O methods
        :param kwargs: necessary parameters for reading/writing data
            valid input parameters are listed in the valid_keys instance variable
        """
        super(Worker, self).__init__()
        self.task = task
        self.params = kwargs

        self.valid_keys = ['path', 'data', 'ilist', 'elist',
                       'imht', 'imwd', 'name', 'bits', 'ext', 'byte']

    def work_to_do(self):
        """
        This method is called when the Worker object is pushed to a new QThread
        A QThread is instantiated and its 'started' signal is linked to this method
        Before executing any tasks, first check for a valid task and valid input parameters

        If parameters are ok, check task parameter and execute method based on task
        :return:
        """
        if self.task is None:
            print('Terminating - No Task assigned')
            self.finished.emit()

        # A task has been assigned. Check parameters against valid inputs
        for key in self.params.keys():
            if key not in self.valid_keys:
                print('Terminating - ERROR Invalid Task Parameter: {}'.format(key))
                print('Valid Parameters are: {}'.format(self.params.keys()))
                self.finished.emit()

        # A task has been assigned and all input parameters are valid
        # Parse the task parameter and call associated method to execute a long running piece of code
        # When the long running code has finished the appropriate signal is emitted from this method
        # Any data which needs to be output will be emitted from associated task methods
        # This method will only emit 'finished'
        if self.task == 'LOAD_LEEM':
            self.load_LEEM()
            self.finished.emit()

        elif self.task == 'LOAD_LEEM_IMAGES':
            self.load_LEEM_Images()
            self.finished.emit()

        elif self.task == 'LOAD_LEED':
            print("Task found: LOAD_LEED - calling self.load_LEED()")
            self.load_LEED()
            self.finished.emit()

        elif self.task == 'LOAD_LEED_IMAGES':
            self.load_LEED_Images()
            self.finished.emit()

        elif self.task == 'OUTPUT_TO_TEXT':
            self.output_to_Text()
            self.finished.emit()

        else:
            print('Terminating: Unknown task ...')
            self.finished.emit()
            return

    def load_LEEM(self):
        """

        :return:
        """
        import time
        print("Test ...")
        time.sleep(5)
        print("End Test ...")

    def load_LEEM_Images(self):
        """

        :return:
        """
        pass

    def load_LEED(self):
        """

        :return:
        """
        # requires params: path, imht, imwd
        if ('path' not in self.params.keys() or
                    'imht' not in self.params.keys() or
                    'imwd' not in self.params.keys()):
            print('Terminating - ERROR: incorrect parameters for LOAD task')
            print('Required Parameters: path, imht, imwd')
            self.finished.emit()

        if 'bits' not in self.params.keys():
            # if bit size is not specified, use default values in process_LEEM_Data()
            self.params['bits'] = None

        if 'byte' not in self.params.keys():
            self.params['byte'] = 'L'  # default to Little Endian

        print("Parameters are valid; Attempting to load raw LEED data from {0}".format(self.params['path']))
        print("Image Params: {0}  {1}".format(self.params['imht'], self.params['imwd']))
        dat_3d = LF.process_LEEM_Data(dirname=self.params['path'],
                                      ht=self.params['imht'],
                                      wd=self.params['imwd'],
                                      bits=self.params['bits'],
                                      byte=self.params['byte'])
        print("Done Loading raw LEED data")
        print(dat_3d.shape)

        # emit output signal with np array as generic pyobject type
        self.emit(QtCore.SIGNAL('output(PyQt_PyObject)'), dat_3d)


    def load_LEED_Images(self):
        """

        :return:
        """
        pass

    def output_to_Text(self):
        """
        Output tab delimited text file consisting of LEEM/LEED I(V) data
        :return:
        """
        pass

