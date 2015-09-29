"""
This module contains classes pertinent
to creating the main GUI for the data
analysis suite

Maxwell Grady 2015
"""

from PyQt4 import QtGui, QtCore


class PleaseMain(QtGui.QWidget):
    """

    """
    _Style = True
    _DEBUG = False
    _ERROR = True

    def __init__(self, leed=None, parent=None):
        """

        :param leed:
        :param parent:
        :return none:
        """
        super(PleaseMain, self).__init__(self, parent)


class LeedData(object):
    """

    """

    def __init__(self, path=None, enetgy_params=None,
                 box_rad=20):
        """
        :param path: string path to TIFF files
        :param energy_params: list of energy parameter in single decimal format, [start_E, step_E]
        :param box_r: half_length of rectangular integration window; default value of 25
        :return none:
        """
        self.data_dir = path

