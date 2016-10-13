import os
import sys
import threading
import time
import LEEMFUNCTIONS as LF
import numpy as np
from queue import Queue


class TaskWorker(threading.Thread):
    def __init__(self, queue=None, data=None, group=None,
                 target=None, name=None, args=(), kwargs={}, Verbose=None):
        threading.Thread.__init__(self, group, target, name)
        self.queue = queue
        self.data = data
        self.results = []

    def run(self):
        first = True
        while not self.queue.empty():
            coords = self.queue.get()
            if first:
                print(coords)
                first = False
            self.results.append(self.count_minima_original(coords=coords, data=self.data))

    def join(self):
        threading.Thread.join(self)
        return self.results

    def count_minima_original(coords=None, data=None):
        num_min = 0
        data_slice = LF.smooth(data[coords[0], coords[1], :])
        sign = np.sign(data_slice[0])
        for point in data_slice:
            if np.sign(point) != sign and np.sign(point) == 1:
                num_min += 1
            sign = np.sign(point)
        return [coords, num_min]


def load_data():
    print("Loading Test Data Set ...")
    start = time.time()
    data_path = "/Users/Maxwell/Desktop/Ru_UNH_LEEM/141020/141020_03_LEEM-IV_50FOV/"

    # get list of all data files
    files = [name for name in os.listdir(data_path) if name.endswith('.dat')]

    # Generate Energy Parameters
    start_energy = -9.9
    step_energy = 0.1
    energy_list = [start_energy]
    while len(energy_list) < len(files):
        energy_list.append(round(energy_list[-1] + step_energy, 1))

    # data parameters
    image_height = 600
    image_width = 592
    image_header = 520  # discard the first 520 bytes of each file
    # NOTE: only support for 8-bit and 16-bit
    image_bit_depth = 16  # 16-bit files --> 2 bytes per pixel
    image_byte_order = 'L'  # use 'L' for little endian; use 'B' for big endian

    # setup numpy format string from data params
    if image_bit_depth == 16:
        num_bytes = '2'
    else:
        num_bytes = '1'
    if image_byte_order == 'L':
        byte_symbol = '<'
    else:
        byte_symbol = '>'
    fmt_str = byte_symbol + 'u' + num_bytes
    # 'u' indicates unsigned integer values:
    # ex. '<u2' --> data comprised of little endian
    # unsigned integers with 2 bytes per pixel

    # Parse .dat files into 3d numpy array
    arr_list = []
    for fl in files:
        with open(os.path.join(data_path, fl), 'rb') as f:
            arr_list.append(np.fromstring(f.read()[image_header:],
                                         fmt_str).reshape((image_height,
                                                         image_width)))
    data_3d = np.dstack(arr_list)  # (600, 592, 250) size numpy array

    min_index = energy_list.index(0.0)
    max_index = energy_list.index(5.1)
    print("Done Loading Data - Elapsed {}".format(time.time() - start))
    return data_3d[:, :, min_index:max_index]


def main():
    max_num_threads = 4
    data = load_data()  # 3d array cut to specific energy range
    start = time.time()
    points_to_processs = Queue()
    threads = []
    coords = [(r, c) for r in range(data.shape[0])
              for c in range(data.shape[1])]
    # Create Queue of data points to process
    for coord in coords:
        points_to_processs.put(coord)

    print("Number of points to process: {}".format(points_to_processs.qsize()))
    # Generate worker threads
    for _ in range(max_num_threads):
        threads.append(TaskWorker(queue=points_to_processs, data=data))
    # Start work
    for thread in threads:
        thread.start()

    output = []
    for thread in threads:
        output.append(thread.join())

    print("Done Processing Data. Elapsed: {}".format(time.time() - start))
    print("Output List Length: {}".format(len(output)))
    print("First thread result length: {}".format(len(output[0])))
    total = 0
    for item in output:
        total += len(item)
    print("Sum of all output: {}".format(total))


if __name__ == '__main__':
    main()
