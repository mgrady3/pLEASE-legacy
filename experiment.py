"""
Generic LEEM / LEED experiment object
Used for serializing experiment data
This makes it easier to load data from a previously analyzed experiment

Author: Maxwell Grady
Date: March 2016
"""

class Experiment(object):
    """

    """

    def __init__(self):
        self.path = ''
        self.data_type = ''
        self.ext = ''
        self.bit = ''
        self.byte_order = ''
        self.mine = ''
        self.maxe = ''
        self.stepe = ''
        self.num_files = ''


    def toFile(self):
        pass

    def fromFile(self):
        pass
