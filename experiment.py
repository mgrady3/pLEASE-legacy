"""
Generic LEEM / LEED experiment object
Used for serializing experiment data
This makes it easier to load data from a previously analyzed experiment

Author: Maxwell Grady
Date: March 2016
"""
import json
import pprint

pp = pprint.PrettyPrinter(indent=4)


class Experiment(object):
    """

    """

    def __init__(self):
        self._Test = False
        self.name = ''
        self.path = ''
        self.data_type = ''
        self.ext = ''
        self.bit = ''
        self.byte_order = ''
        self.mine = ''
        self.maxe = ''
        self.stepe = ''
        self.num_files = ''
        self.imw = ''
        self.imh = ''

        self.loaded_settings = None


    def toFile(self):
        output = {key:vars(self)[key] for key in vars(self).keys() if key != 'loaded_settings' if not key.startswith('_')}
        # pp.pprint(output)
        file_to_output = '/Users/Maxwell/Desktop/'+self.name+'_output.json'
        with open(file_to_output, 'w') as f:
            json.dump(output, f, indent=4)

    def fromFile(self, fl):
        """
        Read in parameters from a json file, fl
        :param fl: string path to json file
        :return:
        """
        with open(fl, 'r') as f:
            self.loaded_settings = json.load(f)
        try:
                self.name = self.loaded_settings['name']
                self.path = self.loaded_settings['path']
                self.data_type  = self.loaded_settings['type']
                self.ext = self.loaded_settings['ext']
                self.bit = self.loaded_settings['bits']
                self.byte_order = self.loaded_settings['byteo']
                self.mine = self.loaded_settings['mine']
                self.maxe = self.loaded_settings['maxe']
                self.stepe = self.loaded_settings['stepe']
                self.num_files = self.loaded_settings['numf']
                self.imw = self.loaded_settings['imw']
                self.imh = self.loaded_settings['imh']
        except KeyError:
            print("Error in Experiment JSON - Check for usage of Valid Keys Only")
            print("Valid Experiment Parameters are: name, path, type, ext, bits, byteo, mine, maxe, stepe, and numf")
            print("Please refer to experiment.py docstrings for explanation of valid JSON parameter files.")

        self.loaded_settings = None

    def test_load(self):
        test_file = '/Users/Maxwell/Desktop/test_exp_1.json'
        with open(test_file, 'r') as f:
            self.loaded_settings = json.load(f)
        self._Test = True

    def test_fill(self):
        if self.loaded_settings is not None and self._Test:
            try:
                self.name = self.loaded_settings['name']
                self.path = self.loaded_settings['path']
                self.data_type  = self.loaded_settings['type']
                self.ext = self.loaded_settings['ext']
                self.bit = self.loaded_settings['bits']
                self.byte_order = self.loaded_settings['byteo']
                self.mine = self.loaded_settings['mine']
                self.maxe = self.loaded_settings['maxe']
                self.stepe = self.loaded_settings['stepe']
                self.num_files = self.loaded_settings['numf']
                self.imw = self.loaded_settings['imw']
                self.imh = self.loaded_settings['imh']

            except KeyError:
                print("Error in Experiment JSON - Check for usage of Valid Keys Only")
        self.loaded_settings = None
        self._Test = False




