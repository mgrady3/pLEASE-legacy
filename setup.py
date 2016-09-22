##############################################################################
# Author: Liam Deacon                                                        #
#                                                                            #
# Contact: liam.m.deacon@gmail.com                                           #
#                                                                            #
# Copyright: Copyright (C) 2016 Liam Deacon                                  #
#                                                                            #
# License: MIT License                                                       #
#                                                                            #
# Permission is hereby granted, free of charge, to any person obtaining a    #
# copy of this software and associated documentation files (the "Software"), #
# to deal in the Software without restriction, including without limitation  #
# the rights to use, copy, modify, merge, publish, distribute, sublicense,   #
# and/or sell copies of the Software, and to permit persons to whom the      #
# Software is furnished to do so, subject to the following conditions:       #
#                                                                            #
# The above copyright notice and this permission notice shall be included in #
# all copies or substantial portions of the Software.                        #
#                                                                            #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,   #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL    #
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING    #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER        #
# DEALINGS IN THE SOFTWARE.                                                  #
#                                                                            #
##############################################################################
'''
**setup.py** - module for installing PLEASE package using either easy_install or pip
'''
# from distutils.core import setup
from setuptools import setup

setup(
    name='PLEASE',
    packages=['PLEASE'],
    package_data={'PLEASE':['*.png', './icons/*.png']},
   # requires=['numpy', 'matplotlib', 'scipy', 'pillow', 'pyqt4', 'qtconsole', 
   #           'opencv_python', 'pyyaml', 'seaborn', 'qdarkstyle', 'tifffile'],
    install_requires=['numpy', 'matplotlib', 'scipy', 'pillow', 'pyqt4', 'qtconsole',
                      'pyyaml', 'seaborn', 'qdarkstyle', 'tifffile'],
    version='0.2.2',
    description='Software for the analysis of Low Energy Electron Microscopy data',
    long_description= """
PLEASE is a software package built for analysis of Low Energy Electron Microscopy data sets with specific emphasis on analysis of IV data sets.

For more info see https://github.com/mgrady3/pLEASE or contact the authors via Email (max.grady@gmail.com) or Twitter (https://twitter.com/andisspam)
""",
    author='Maxwell Grady',
    author_email='max.grady@gmail.com',
    url='https://github.com/mgrady3/pLEASE',
    download_url='https://github.com/mgrady3/pLEASE/archive/master.zip',
    keywords=['LEEM', 'surface science', 'image analysis', 'I(V) spectra', 'electron microscopy'],
    license='GPLv3',
    platforms='any',
    classifiers=[
     'Development Status :: 2 - Pre-Alpha',
     'Environment :: X11 Applications :: Qt',
     'Intended Audience :: Science/Research',
     'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
     'Operating System :: OS Independent',
     'Programming Language :: Python :: 2.7',
     'Programming Language :: Python :: 3',
     'Topic :: Scientific/Engineering :: Chemistry',
     'Topic :: Scientific/Engineering :: Physics',
     'Topic :: Scientific/Engineering :: Visualization',
     ],
    scripts=['please.pyw'],
)

