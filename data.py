"""
Module containing classes which act as containers for
LEED and LEEM data sets. Each objects has a main data
construct consisting of a 3d numpy array which is filled
by reading in a stack of data files in either an image format
or raw binary data.

Alongside the 3d numpy array there must be some type of list or
container for energy parameters which corresponds directly to the
third axis of the numpy array.
"""
import os
import numpy as np
import LEEMFUNCTIONS as LF


class LeedData(object):
    """
    Generic object to hold LEED Data and relevant variables
    Data loading methods
    """

    def __init__(self, br=20):
        self.dat_3d = np.zeros((10, 10, 10))  # placeholder for main data
        self.elist = []  # list of energy values
        self.ilist = []
        self.data_dir = ''  # placeholder for path to currently stored data
        # Image settings will be set to appropriate values via the User inside gui.py
        self.ht = 0  # Height of image used in loading Raw data
        self.wd = 0  # Width of image used in loading Raw data
        self.box_rad = br  # default value is 20 yielding a 40x40 rectangular integration window
        self.average_ilist = None

    def load_LEED_PNG(self, dirname):
        """
        Load LEED-I(V) image files into numpy array
        This function uses PIL to parse the png files
        This is slower than loading raw binary data due to the overhead in parsing
        image files, however, it is faster than loading TIFF files

        :param dirname: path to directory containing png files
        :return: 3d numpy array
        """
        # maybe not needed
        prev_dir = self.data_dir

        return np.array(LF.get_img_array(dirname, ext='.png'))

    def load_LEED_RAW(self, dirname):
        """
        Load RAW binary files into 3d numpy array
        This is the fastest method for loading data
        This should only be called from load_LEED_Data()

        :return: 3d numpy array
        """
        # maybe not needed
        prev_dir = self.data_dir
        files = [name for name in os.listdir(dirname) if name.endswith('.dat')]
        print('Number of Files found: {}'.format(len(files)))
        if self.ht >= 2 and self.wd >= 2:
            # image parameters were correctly set through GUI
            return LF.process_LEEM_Data(dirname, self.ht, self.wd)
        else:
            # image parameters were not set through GUI
            print('!Warning: Invalid Image Parameters while loading RAW data!')
            print('Returning Empty array ...')
            return np.zeros((500, 500, 100))  # placeholder array

    def load_LEED_TIFF(self, dirname):
        """
        Load LEED data from TIFF files into 3d numpy array
        This is the slowest data loading method
        There is much overhead in processing tiff image files
        This function should only be called from load_LEED_Data()

        :param dirname: path to directory containing tiff files
        :return: 3d numpy array where 3rd axis corresponds to Energy via self.elist
        """
        # maybe not needed
        prev_dir = self.data_dir

        return np.array(LF.get_img_array(dirname, ext='.tif'))


class LeemData(object):
    """
    Generic object to hold LEEM data and relevant variables
    LEEM loading functions are already contained in LEEMFUNCTIONs.py
    A this point I will not be porting them into the LeemData class
    """
    def __init__(self):
        # Image Parameters
        self.ht = 0  # image height to be set by User
        self.wd = 0  # image width to be set by User
        self.hdln = 0  # image header length to be set by User
        # Data
        self.dat_3d = np.zeros((10, 10, 10))  # placeholder for main data
        self.elist = []  # list of energy values
        self.ilist = []
        self.e_step = 0
        # Directories and Image index
        self.data_dir = ''
        self.img_mask_count_dir = ''
        self.curimg = 0  # correspondent to third axis of self.dat_3d
        # Coordinates for I(V) data
        self.curX = 0
        self.curY = 0
        # Count Minima Parameters
        self.cod_thresh = 0.45
