import os
import time
import matplotlib as mpl
mpl.use('Qt4Agg')
import matplotlib.pyplot as plt
import multiprocessing as mp
import numpy as np
from matplotlib import cm as cm
from matplotlib import colors as clrs
from matplotlib import colorbar


t_init = time.time()

def smooth(inpt, window_len=10, window_type='flat'):
    """
    inpt: 1-d 'array-like' container of data to be smoothed
    window_len: integer length of window function
    window_type: string specifying window name

    returns: 1-d numpy array of smoothed data with length equal to inpt
    """
    s = np.r_[inpt[window_len-1:0:-1], inpt, inpt[-1:-window_len:-1]]
    if window_type == 'flat':
        # Use boxcar averaging
        w = np.ones(window_len, 'd')
    else:
        # Use pre-defined window
        w = eval('np.'+window_type+'(window_len)')
    otpt = np.convolve(w/w.sum(), s, mode='valid')
    # make sure otpt is same length as inpt
    return otpt[(window_len/2 -1):-(window_len/2)]


def count_mins(data):
    num = 0
    locs = []
    sgn = np.sign(data[0])
    for point in data:
        if np.sign(point) != sgn and np.sign(point) == 1:
            num += 1
            locs.append(list(data).index(point))
        sgn = np.sign(point)
    '''if num >= 2:
        return (num, locs[0], locs[-1])
    else:
        return num'''
    return num


def new_count_mins(data):
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
        return (num,  -1,  -1)
    return (num, -1, -1)


def count_and_check_flat(data, thresh=5):
    mins = new_count_mins(data)
    if mins[0] >= 2:
        data_subset = data[mins[1]:mins[2]]
        data_var = np.var(data_subset)
        if data_var <= thresh:
            return 0
        else:
            return mins[0]
    else:
        return mins[0]


def discrete_colors_imshow(data, clrmp=cm.Spectral):
    max_val = np.max(data)
    min_val = np.min(data)
    cmap_list = [clrmp(i) for i in range(clrmp.N)]
    cmap_list[0] = (0,0,0, 1.0)  # custom 0 value color
    cmap = clrmp.from_list('Custom Colors', cmap_list, clrmp.N)

    bounds = np.linspace(min_val, max_val, (max_val - min_val)+1)
    norm = clrs.BoundaryNorm(bounds, cmap.N)

    #img = plt.imshow(data, interpolation='none', cmap=cmap)
    fig, ax = plt.subplots(1,1, figsize=(8,8))
    ax.imshow(data, interpolation='none', cmap=cmap)
    ax2 = fig.add_axes([0.95, 0.1, 0.03, 0.8])
    cb = colorbar.ColorbarBase(ax2, cmap=cmap, norm=norm,
        spacing='proportional', ticks=bounds, boundaries=bounds, format='%1i')
    plt.show()






'''def count_mins_with_flat_check(data):
    mins = count_mins(data)
    if mins[0] == 0:
        return 0
    elif mins[0] == 1:
        return 1
    else:
        data_to_check = smoo
'''


# Get Files
files = [name for name in os.listdir(os.getcwd()) if name.endswith('.dat')]

# Generate Energy Parameters
start_energy = -9.9
step_energy = 0.1
energy_list = [start_energy]
while len(energy_list) < len(files):
    energy_list.append(round(energy_list[-1] + step_energy, 1))

# Parse .dat files into 3d numpy array
image_height = 600
image_width = 592
image_header = 520  # discard the first 520 bytes of each file
arr_list = []


for fl in files:
    with open(fl, 'rb') as f:
        arr_list.append(np.fromstring(f.read()[image_header:],
                                      '<u2').reshape((image_height,
                                                     image_width)))
data_3d = np.dstack(arr_list)  # (600, 592, 250) size numpy array
del arr_list  # no longer need copy of each file in list

print('Generating and Parsing Data Set ...')
ts = time.time()
smooth_data = np.apply_along_axis(smooth, 2, data_3d)
diff_data = np.diff(smooth_data, axis=2) / np.diff(energy_list)
smooth_diff_data = np.apply_along_axis(smooth, 2, diff_data)

min_energy = 0.0
max_energy = 5.1
min_index = energy_list.index(min_energy)
max_index = energy_list.index(max_energy)
smooth_data_cut = smooth_data[:, :, min_index:max_index]
diff_data_cut = diff_data[:, :, min_index:max_index]
smooth_diff_data_cut = smooth_diff_data[:, :, min_index:max_index]
energy_cut = energy_list[min_index:max_index]

te = time.time()
print('Elapsed: {} '.format(round(te-ts,3)))

'''
ts = time.time()
mask_apply = np.apply_along_axis(count_mins, 2, smooth_diff_data)
te = time.time()
print('Apply_Along ... Elapsed: {} '.format(round(te-ts,3)))
'''
pool = mp.Pool(2*mp.cpu_count())  # num processes = 2*num cores
ts = time.time()
ins = [smooth_diff_data_cut[r,c,:] for r in range(image_height) for c in range(image_width)]
outs = pool.map(count_and_check_flat, ins)
pool.close()
pool.join()

outs = np.array(outs).reshape((600,592))
te = time.time()
print('Min Counting using 4 cores -  Elapsed: {} '.format(round(te-ts,3)))
# print(type(outs))
# print(outs.shape)
# print(type(outs[300,300]))

#plt.imshow(outs, cmap=cm.Spectral)
discrete_colors_imshow(outs)
t_final = time.time()
print('Displaying Output: Total Elapsed: {} '.format(round(t_final - t_init, 3)))
#plt.show()
