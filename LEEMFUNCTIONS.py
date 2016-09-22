import os
import numpy as np
import cv2
import multiprocessing as mp
from PIL import Image

# deprecated
DEF_IMHEIGHT = 600
DEF_IMWIDTH = 592
DEF_IMHEAD = 520


class ParseError(Exception):
    def __init__(self, message, errors):
        super(ParseError, self).__init__(message)
        # TODO: implement this later ...
        self.errors = errors
        self.message = message

def filenumber_to_energy(el, im):
    """
    Convert filenumber to energy in eV
    :argument el: list of energy values in eV in single decimal format
    :argument im: integer image file number in range 0 to self.LEEM_numfiles
    :return el[im]: energy value in single decimal format corresponding to file number im
    """
    try:
        return el[im]
    except IndexError as e:
        print("Error getting energy from file number ...")
        print(e)
        print("Returning 0 by default")
        return 0

def energy_to_filenumber(el, val):
    """
    Convert energy value in eV to image file number
    :argument el: list of energy values in eV in single decimal format
    :argument val: single decimal float representing an electron energy in eV
    :return el.index(val): integer filenumber corresponding to the energy val
    """
    return el.index(val)


def process_LEEM_Data(dirname, ht=0, wd=0, bits=None, byte='L'):
    """
    read in all .dat files in current data directory
    process each .dat file into a numpy array
    stack arrays atop each other
    return 3d-numpy array to self.data_3d

    :argument dirname: string path to current data directory
    :param ht: integer pixel height of image
    :param wd: integer pixel width of image
    :param bits: integer representing bit depth of image, default is 16 bit
    :param byte: string representing byte order, 'L' for Little-Endian (Intel), 'B' for Big-Endian (Motorola)
    :return dat_arr: 3d numpy array
    """
    print('Processing Data ...')
    # progress = pb.ProgressBar(fd=sys.stdout)
    arr_list = []
    flag = True
    # add filter on file names to exclude hidden files beginning with a leading period
    files = [name for name in os.listdir(dirname) if name.endswith('.dat') and not name.startswith(".")]
    files.sort()
    print('First file is {}.'.format(files[0]))

    for fl in files:
        with open(os.path.join(dirname, fl), 'rb') as f:
            # dynamically calculate file header length
            if ht == 0 and wd == 0:
                hdln = DEF_IMHEAD
                ht = DEF_IMHEIGHT
                wd = DEF_IMWIDTH
            else: hdln = len(f.read()) - (int(bits/8)*ht*wd)  # multiply by number of bytes per pixel

            if flag:
                print('Calculated Header Length of First File: {}'.format(hdln))
                # only print first file header length
                flag = False
            f.seek(0)

            # Generate format string given a bit size read from YAML config file
            if bits == 8 and byte == 'L':
                formatstring = '<u1'  # 1 byte (8 bits) per pixel
            elif bits == 8 and byte == 'B':
                formatstring = '>u1'

            elif bits == 16 and byte == 'L':
                formatstring = '<u2'  # 2 bytes (16 bits) per pixel
            elif bits == 16 and byte == 'B':
                formatstring = '>u2'

            elif bits is None:
                formatstring = '<u2'  # default to 16 bit images

            else:
                print("Error in process_LEEM_Data() - unknown bit size when loading raw data")
                print("Check for incorrect bitsize in YAML experiment file")

            arr_list.append(np.fromstring(f.read()[hdln:],
                                          formatstring).reshape((ht, wd)))
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
        if np.sign(point) != sgn and np.sign(point) == 1:
            # the derivative has changed signs - ie. crossed the x axis
            # thus by the intermediate value theorem it must have a zero point in between
            # the zero point in the dI/dV spectra corresponds to a local extrema in the I(V) spectrum

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


def get_img_array(path, ext=None, swap=False):
    """
    Generate a 3d numpy array of gray-scale image files
    :param path: path to image files
    :param ext: file extension, default None for raw (.dat) data (not yet implemented)
    :param swap: boolean to swap the byte order of the array; default False
    :return dat_3d: 3d numpy array (height, width, image number)
    """
    if ext is None:
        # Raw Data - implement this later
        pass
    else:
        # Handle Tiff and Png with '.tif' and '.png'
        print('Searching for {0} files in path: {1}'.format(ext, path))
        files = [name for name in os.listdir(path) if name.endswith(ext)]

        print('Number of Files found: {}'.format(len(files)))
        if not files and ext=='.tif':
            print('Error: No Files Found')
            print('Directory does not contain files with \'.tif\' extensions')
            print('Trying \'.tiff\' instead')
            files = [name for name in os.listdir(path) if name.endswith('.tiff')]
            if not files:
                print('Error: No Files Found')
                print('Aborting Loading ...')
                return None
        elif not files:
            # ext must be '.png' but no files were found
            print('Error no Files Found')
            print('Directory does not contain files with \'.png\' extensions')
            print('Aborting Loading ...')
            return None

        files.sort()
        arr_list = []
        for fl in files:
            arr_list.append(read_img(os.path.join(path, fl)))
        if swap:
            return np.dstack(arr_list).byteswap()
        else:
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

        # Use the greyscale transformation as defined in the Python Image Library
        # When converting from a colour image to black and white, the library uses the
        # ITU - R 601 - 2 luma transform:
        # L = R * 299 / 1000 + G * 587 / 1000 + B * 114 / 1000

        im = im.convert('L')

        pixels = list(im.getdata())
        w, h = im.size
        # generate list of lists of pixel values then convert to numpy array
        pixels = [pixels[i*w:(i+1)*w] for i in range(h)]

        # try to determine optimal numpy data type
        m = max(max(pixels))
        if 0 < m <= 255:
            typ = np.uint8
        elif 255 < m <= 65535:
            typ = np.uint16
        elif 65535 < m <= 4294967295:
            typ = np.uint32
        else:
            typ = np.uint64

        try:
            return np.array(pixels).astype(typ)
        except TypeError as e:
            print("Error reading image into numpy array")
            print("Max value stored exceeds that of 64 bit integer")
            raise e


def parse_tiff_header(img, w, h, byte_depth):
    """
    try to find byte order in tiff header info
    :param img: string path to file to examine
    :param w: img width
    :param h: imh height
    :param byte_depth: number of bits per pixel
    :return: string corresponding to Experiment YAML settings for byte order: 'L' or 'B' or None if error
    """
    header_data = None
    header = None
    try:
        with open(img, 'rb') as f:
            header = len(f.read()) - byte_depth*w*h
            if header < 0:
                raise ParseError(message="Incorrect value calculated for header length; \
                                          Check for correct Image Width, Height and Bit Depth.", errors=None)

            f.seek(0)
            header_data = f.read()[0:header+1]
            f.seek(0)
            data = f.read()[header:]

    except FileNotFoundError:
        print("Error: File {0} not found in current directory.".format(img))

    if not header_data:
        raise ParseError(message="No Header Information Found; Check for correct Image Width, Height and Bit Depth", errors=None)
    # TODO: the decoding of bytes using UTF-8 could be troublesome in the future ...
    # Perhaps its best here to have some sort of User configurable data encoding setting
    # For now that is beyond the scope of the current development
    if len(header_data) >= 2:
        byte_order = header_data[0:2]
        if byte_order.decode("UTF-8") == "MM":
            # in py2.7 'MM'.decode("UTF-8") returns u'MM' which compares True to 'MM'
            # in py3, byte_order will be read as b'MM' which needs to be decoded before comparison
            return 'B'
        elif byte_order.decode("UTF-8") == "II":
            # in py2.7 'II'.decode("UTF-8") returns u'MM' which compares True to 'II'
            # in py3, byte_order will be read as b'MM' which needs to be decoded before comparison
            return 'L'
        else:
            raise ParseError(message="Unknown byte order in first two bytes of TIFF file.", errors={byte_order: byte_order})

    else:
        raise ParseError(message="Header Length too short; Need at least two bytes to read correct byte order.", errors=None)


def gen_dat_files(dirname=None, outdirname=None, ext=None,
                  w=None, h=None, byte_depth=None):
    """
    Given a directory with image files, output raw binary files with no header
    :param dirname: string path to directory containing image files
    :param outdirname: string path to directory to output raw .dat files
    :param w: img width
    :param h: imh height
    :param byte_depth: number of bits per pixel
    :param ext:
    :return:
    """
    if dirname is None or outdirname is None or ext is None or w is None or h is None or byte_depth is None:
        print("Error: required parameters are input directory, output directory, and file extension including . , \
              image width, image height, and image byte_depth.")
        return
    print('Searching for files in {0} ...'.format(dirname))
    files = [name for name in os.listdir(dirname) if name.endswith(ext)]

    if not files:
        print("Error: no files found with file extension {0}".format(ext))
        return

    print('Found {0} files to process ...'.format(len(files)))

    if ext in ['.tif', '.tiff', '.TIF', '.TIFF']:
        try:
            print('Parsing file {0}'.format(os.path.join(dirname, files[0])))
            byte_order = parse_tiff_header(os.path.join(dirname, files[0]), w, h, byte_depth)
        except ParseError as e:
            print("Failed to parse tiff header; defaulting to big endian bye order")
            print(e.message)
            print(e.errors)
            byte_order = 'B'  # default to big endian
        except FileNotFoundError as ef:
            print(ef)  # TODO: figure out whats best practice here ...
            byte_order = 'B'  # default to big endian
    else:
        # PNG and JPEG always use Big Endian
        byte_order = 'B'  # default to big endian

    # swap to numpy syntax
    if byte_order == 'L':
        byte_order = '<'
    elif byte_order == 'B':
        byte_order = '>'

    for file in files:
        with open(os.path.join(dirname, file), 'rb') as f:
            header = len(f.read()) - byte_depth * w * h
            f.seek(0)
            # generate numpy friendly data format string: ex. '<u2' = little endian, unsigned integer, 2 bytes per pixel
            fmtstr = byte_order + 'u' + str(byte_depth)
            data = np.fromstring(f.read()[header:], fmtstr).reshape((h,w))  # strip header information
            with open(os.path.join(outdirname, file.split('.')[0]+'.dat'), 'wb') as o:
                data.tofile(o)  # store image data as raw binary file
    print("Done outputting dat files ...")
    return


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


def find_local_maximum(window, radius=25):
    """
    *** NOTE: This function makes use of OpenCV which adds another potentially
    ***       hard to compile (on Windows) module dependence
    Find the center of the LEED beam selected by the user in (r,c) format
    :param window: 3d numpy array consisting of a subset of the main data set. This is an integration window
     selected by the user which contains a LEED beam
    :param radius: user setting for radius of gaussian. Default to 25 if not explicitly set.
    :return maxLoc: tuple containing the location of the beam maximum
    """
    # Now radius is settable from the process calling find_local_maximum()
    radius = radius
    # radius = 25
    orig = window.copy()
    blur = cv2.GaussianBlur(window, (radius, radius), 0)

    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(blur, mask=None)
    return maxLoc


def count_layers_new(data, ecut):
        '''
        Currently set to use multiprocessing.
        Note this will not work well with the PyQt Gui
        Alternate methods need to be used to parallelize this code for use in the main GUI

        :param data: 3d numpy array of smooth data cut to specific data range
        :param ecut: 1d list of energy values cut to specific data range
        :return none:
        '''

        # calculate the derivative of input data
        diff_data = np.diff(data, axis=2) / np.diff(ecut)

        # smooth the derivative data
        smooth_diff_data = np.apply_along_axis(smooth, 2, diff_data)
        # print('Creating process pool ...')
        # process pool
        pool = mp.Pool(4)

        # create list of 1-d arrays as input to count_mins()
        ins = [smooth_diff_data[r,c, :] for r in range(data.shape[0])
                                        for c in range(data.shape[1])]
        # list of outputs from check_flat using pool.map()
        # print('Starting parallel computation')
        outs = pool.map(check_flat_and_count, ins)
        pool.close()
        pool.join()
        # print('Closing pool and joining ...')
        # convert back to np array and reshape
        outs = np.array(outs).reshape((data.shape[0], data.shape[1]))
        return outs


def check_flat_and_count(data, thresh=5):
        '''

        :param data: 1d numpy array containing smoothed dI/dE data
        :param thresh: threshold value for
        :return:
        '''

        mins = count_mins(data)
        if mins[0] >= 2:
            data_subset = data[mins[1]:mins[2]]
            data_var = np.var(data_subset)
            if data_var <= thresh:
                return 0
            else:
                return mins[0]
        else:
            return mins[0]


def count_mins(data):
    """
    Use the intermediate value theorem to find minima in I(E) by counting the number
    of times dI/dE changes sign from - to +

    :param data: 1d smoothed dI/dE signal
    :return tuple: (num minima, location of first minima, location of last minima)
    """
    num = 0
    locs = []
    sgn = np.sign(data[0])
    for point in data:
        if np.sign(point) != sgn and np.sign(point) == 1:
            num += 1
            locs.append(list(data).index(point))
        sgn = np.sign(point)
    if num >= 2:
        return (num, locs[0], locs[-1])
    else:
        # num min = 0 or 1
        # dummy indicies for location of minima
        return (num,  -1,  -1)
