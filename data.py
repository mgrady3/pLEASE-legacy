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

    """

    def __init__(self):
        self.dat_3d = np.zeros((10, 10, 10))  # placeholder for main data
        self.elist = []  # list of energy values
        self.data_dir = ''  # placeholder for path to currently stored data
        # Image settings will be set to appropriate values via the User inside gui.py
        self.ht = 0  # Height of image used in loading Raw data
        self.wd = 0  # Width of image used in loading Raw data

    def load_LEED_PNG(self, dirname):
        # maybe not needed
        prev_dir = self.data_dir
        data = LF.get_img_array(dirname, ext='.png')
        print('New Data shape: {}'.format(data.shape))
        if data.shape[2] != len(self.elist):
            print('! Warning: New Data does not match current energy parameters !')
            print('Updating Energy parameters ...')
        return np.array(data)

    def load_LEED_RAW(self, dirname):
        """
        Load RAW binary files into 3d numpy array
        This is the fastest method for loading data
        This should only be called from load_LEED_Data()
        :return none:
        """
        # maybe not needed
        prev_dir = self.data_dir
        files = [name for name in os.listdir(dirname) if name.endswith('.dat')]
        print('Number of Files found: {}'.format(len(files)))
        if self.ht >= 2 and self.wd >= 2:
            # image parameters were correctly set through GUI
            return LF.process_LEEM_Data(dirname, self.ht, self.wd)
        else:
            # image parmeters were not set through GUI
            print('!Warning: Invalid Image Parameters while loading RAW data!')
            print('Returning Empty array ...')
            return np.zeros((500, 500, 100))  # placeholder array

    def load_LEED_TIFF(self, dirname):
        """
        Load LEED data from TIFF files into 3d numpy array
        This is the slowest data loading method
        There is much overhead in processing tiff image files
        This function should only be called from load_LEED_Data()
        :return data: 3d numpy array where 3rd axis corresponds to Energy via self.elist
        """
        # maybe not needed
        prev_dir = self.data_dir
        data = LF.get_img_array(dirname, ext='.tif')
        print('New Data shape: {}'.format(data.shape))
        if data.shape[2] != len(self.elist):
            print('! Warning: New Data does not match current energy parameters !')
            print('Updating Energy parameters ...')
        return np.array(data)


class LeemData(object):
    """

    """
    def __init__(self):
        self.dat_3d = np.zeros((10, 10, 10))  # placeholder for main data
        self.elist = []  # list of energy values
