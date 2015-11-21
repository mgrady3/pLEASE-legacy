
import os
import sys
import numpy as np
import cv2
import progressbar as pb
from PIL import Image

DEF_IMHEIGHT = 600
DEF_IMWIDTH = 592
DEF_IMHEAD = 520


def filenumber_to_energy(el, im):
    """
    Convert filenumber to energy in eV
    :argument el: list of energy values in eV in single decimal format
    :argument im: integer image file number in range 0 to self.LEEM_numfiles
    :return el[im]: energy value in single decimal format corresponding to file number im
    """
    return el[im]


def energy_to_filenumber(el, val):
    """
    Convert energy value in eV to image file number
    :argument el: list of energy values in eV in single decimal format
    :argument val: single decimal float representing an electron energy in eV
    :return el.index(val): integer filenumber corresponding to the energy val
    """
    return el.index(val)


def process_LEEM_Data(dirname, ht=0, wd=0):
    """
    read in all .dat files in current data directory
    process each .dat file into a numpy array
    stack arrays atop each other
    return 3d-numpy array to self.data_3d

    :argument dirname: string path to current data directory
    :param ht: integer pixel height of image
    :param wd: integer pixel width of image
    :return dat_arr: 3d numpy array
    """
    print('Processing Data ...')
    # progress = pb.ProgressBar(fd=sys.stdout)
    arr_list = []
    files = [name for name in os.listdir(dirname) if name.endswith('.dat')]
    files.sort()
    print('First file is {}.'.format(files[0]))
    flag = True
    for fl in files:
        with open(os.path.join(dirname, fl), 'rb') as f:
            # dynamically calculate file header length
            if ht == 0 and wd == 0:
                hdln = DEF_IMHEAD
                ht = DEF_IMHEIGHT
                wd = DEF_IMWIDTH
            else: hdln = len(f.read()) - (2*ht*wd)

            if flag:
                print('Calculated Header Length of First File: {}'.format(hdln))
                # only print first file header length
                flag = False
            f.seek(0)
            arr_list.append(np.fromstring(f.read()[hdln:],
                                          '<u2').reshape((ht, wd)))
    print('Creating 3D Array ...')

    dat_arr = np.dstack(arr_list)  # create 3D stack of all image files
    del arr_list[:]  # clear data from list as it ahs now been stored in numpy array
    # print('Returning New Array Shape: {}'.format(dat_arr.shape))
    return dat_arr


def gen_neighborhood(data, row, col):
    """
    Generate 3x3 neighborhood of selected pixel
    If near the edge generate the truncated neighborhood
    to avoid index out-of-bounds errors
    :param data: 2d numpy array
    :param row: integer row index
    :param col: integer col index
    :return data: sub-slice of original data array
    """
    min_row = 0
    min_col = 0
    max_row = data.shape[0] - 1
    max_col = data.shape[1] - 1

    if (min_row < row < max_row) and (min_col < col < max_col):
        # Interior pixel --> return regular 3x3 slice of input 2d array
        return data[row-1:row+2, col-1:col+2]

    else:
        # Pixel is on the border
        # first check corner cases
        if (row, col) == (min_row, min_col):
            # top left corner
            return data[row:row+2, col:col+2]

        elif (row, col) == (min_row, max_col):
            # top right corner
            return data[row:row+2, col-1:col+1]

        elif (row, col) == (max_row, max_col):
            # bot right corner
            return data[row-1:row+1, col-1:col+1]

        elif (row, col) == (max_row, min_col):
            # bot left corner
            return data[row-1:row+1, col:col+2]

        else:
            # pixel is on Border but not a corner case
            if row == min_row:
                # upper central
                return data[row:row+2, col-1:col+2]

            elif col == max_col:
                # right central
                return data[row-1:row+2, col-1:col+1]

            elif row == max_row:
                # bottom central
                return data[row-1:row+1, col-1:col+2]

            else:
                # left central
                return data[row-1:row+2, col:col+2]


def calc_var(data):
    """
    """
    cntr = data[1, 1]
    return (cntr - data.mean())**2


def count_minima_locations(e_cut, smth_iv):
    """
    This function takes a set of I(V) data and counts the number of minima in the data set.
    The return value is the number of minima as well as a list of the indices corresponding to their locations

    :argument e_cut:  array-like container of energy values cut to same length as intensity data
    :argument smth_iv:  array-like container of intensity values cut to desired energy window
    :return:  tuple with two values (# of minima, list of minima locations)
    """
    diff_iv = list(np.diff(smth_iv)/np.diff(e_cut))
    sgn = np.sign(diff_iv[0])  # get sign of first point
    count = 0
    min_locations = []

    for point in diff_iv:
        if np.sign(point) != sgn:
            # the derivative has changed signs - ie. crossed the x axis
            # thus by the intermediate value theorem it must have a zero point in between
            # the zero point in the dI/dV spectra corresponds to a local extrema in the I(V) spectrum

            if np.sign(point) == 1:
                # the current point in the derivative is positive which means the last point was negative
                # a derivative changing from - to + indicates a local minima
                min_locations.append(diff_iv.index(point))
                count += 1
        sgn = np.sign(point)  # update sgn and continue loop with next point in the derivative

    return (count, min_locations)


def smooth(inpt, window_len=10, window_type='flat'):
    """
    Smoothing function based on Scipy Cookbook recipe for data smoothing
    Uses predefined window function (selectable) to smooth a 1D data set
    Computes the convolution with a normalized window

    :param inpt: input list or 1d array
    :param window_len: even integer size of window
    :param window_type: string for type of window function
    :return otpt: 1d numpy array of smoothed data with same length as inpt
    """
    if not (window_len % 2 == 0):
        window_len += 1
        print('Window length supplied is odd - using next highest integer: {}.'.format(window_len))

    if window_len <= 3:
        print('Error in data smoothing - please select a larger window length')
        return

    # window_type = 'hanning'
    if not window_type in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        print('Error - Invalid window_type')
        return

    # Generate two arguments to pass into numpy.convolve()
    # s is the input signal doctored with reflections of the input at the beginning and end
    # this serves to remove noise in the smoothing method
    # w is the window matrix based on pre-defined window functions or unit matrix for flat window

    s = np.r_[inpt[window_len-1:0:-1], inpt, inpt[-1:-window_len:-1]]
    # w = eval('np.'+window_type+'(window_len)')
    if window_type == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    else:
        w = eval('np.'+window_type+'(window_len)')

    # create smoothed data via numpy.convolve using the normalized input window matrix
    otpt = np.convolve(w/w.sum(), s, mode='valid')

    # format otpt to be same size as inpt and return
    return otpt[(window_len/2-1):-(window_len/2)]


def crop_images(data, indices):
    """
    Crop images based on the indices specified
    :param data: 3d numpy array of images
    :param indices: list of two tuples in (r,c) format 1st = top left corner 2nd = bottom right
    :return: 3d numpy slice of original array based on given inputs
    """
    return data[indices[0][0]:indices[1][0]+1,
                indices[0][1]:indices[1][1]+1]


def get_img_array(path, ext=None):
    """
    Generate a 3d numpy array of gray-scale image files
    :param path: path to image files
    :param ext: file extension, default None for raw (.dat) data (not yet implemented)
    :return dat_3d: 3d numpy array (height, width, image number)
    """
    if ext is None:
        # Raw Data - implement this later
        pass
    else:
        # Handle Tiff and Png with '.tif' and '.png'
        files = [name for name in os.listdir(path) if name.endswith(ext)]
        files.sort()
        print('Number of Files found: {}'.format(len(files)))
        arr_list = []
        for fl in files:
            arr_list.append(read_img(os.path.join(path, fl)))
        return np.dstack(arr_list)


def read_img(path):
        """
        Use PIL to open an image file, convert to greyscale and output a 2D numpy array.
        In principle should work for .tif, .png, .jpg,
        and possibly anything else supported by Image.open().
        :param path: path to image to be opened
        :return:
        """
        # print 'opening image %s' % path
        im = Image.open(path)
        im = im.convert('L')

        pixels = list(im.getdata())
        w, h = im.size
        # generate list of lists of pixel values then convert to numpy array
        pixels = [pixels[i*w:(i+1)*w] for i in range(h)]
        return np.array(pixels)


def parse_dir(dirname):
    """
    Hack to remove '/path/to/folder/untitled/' error from QTFileDialog where /untitled/ gets appended by default
    This happens when you select OK in in the getExistingDirectory dialog without manually selecting a directory
    Essentially you want to say OK to the default directory but for some reason /untitled/ gets added to the path

    :param dirname: string path to directory delimited by /
    :return: string path to directory delimited by / without .../untitled/... if it exists

    :Test Cases:
        x = '/User/Test/Desktop/'
        y = '/User/Test/untitled/Desktop/'
        z = '/untitled/User/Test/Desktop/'

        all will return the string '/User/Test/Desktop'

    :Note: If this will cause problems if the User actually has data stored in a path with a folder
           called untitled intentionally
    """

    splt = dirname.split('/')

    # error happens by appending /untitled/ to path
    # this results in the split list having second to last element equal to 'untitled'
    # check if this is true and delete the element if so then rejoin the list and return

    if 'untitled' in splt:
        index = splt.index('untitled')
        del splt[index]
        print('Warning: detected .../untitled/... somewhere in path')
        print('This is often caused by an error in the QFileDialog implementation.')
        print('Attempting to fix path automatically ...')
    return '/'.join(splt)


def find_local_maximum(window):
    """
    *** NOTE: This function makes use of OpenCV which adds another potentially
    ***       hard to compile (on Windows) module dependence
    Find the center of the LEED beam selected by the user in (r,c) format
    :param window: 3d numpy array consisting of a subset of the main data set. This is an integration window
     selected by the user which contains a LEED beam
    :return maxLoc: tuple containing the location of the beam maximum
    """
    radius = 25  # TODO: User Defined Setting
    orig = window.copy()
    blur = cv2.GaussianBlur(window, (radius, radius), 0)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(blur)
    return maxLoc