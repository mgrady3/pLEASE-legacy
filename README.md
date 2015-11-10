
#python Low-energy Electron Analysis SuitE: pLEASE

Author: Maxwell Grady

pLEASE is the successor to all of my previous LEED/LEEM Data analysis scripts and programs such as pyLEEM, pyLEEDLEEM, newLEED, etc...

pLEASE provides a full GUI for analysis for LEED and LEEM data sets specifically geared towards viewing and analyzing LEED/LEEM-I(V) data.

## Functionality:
* Full GUI written with the Qt Framework via the python bindings PyQt4
* View LEED and LEEM data sets from a variety of data formats (jpg, png, tiff, and raw bary data)
* Point-and-Click I(V) curve extraction from single  pixel (LEEM) and adjustable sized rectangular box regions (LEED)
* Ouput I(V) data to text files for easy plotting in other programs in a tab separated columar file
* Background subtraction for LEED-I(V) 
* FFT generation to analyze the real-space periodicity of a LEED pattern
* Data smoothing using convolution of pre-defined window functions (Hanning, Hamming, Blackman, Flat, etc...)
* Output plots as png files using built in MatPlotLib toolbars for plot navigation and interactivity
* Rudimentasry ability to count minima/maxima in an I(V) curve - useful for determination of thin film layer thickness

pyLEED_LEEM and newLEED are more or less finished projects

pLEASE is a work in progress to merge those two programs into one unified GUI
In future versions of this software further GUI enhancements may be made using alternate constructs such as Enaml or PyQtGraph

### Requirements:
* Python distribution 2.7 or 3.x (No Support for Legacy Python versions < 2.7)
* Numpy
* Scipy
* Matplotlib
* Pandas
* *Qt & PyQt4 
* Note: All the above are contained in the Anaconda Python Distribution which I HIGHLY recommend be used for running this code
* Note: The following packages need to be manually installed but are available via Pip
* openCV
* seaborn
* QDarkStyle (a QSS package which sets the overall look and feel of the GUI) 

# Usage:
Once all the required packages and frameworks are installed either manually or by starting with the Anaconda Python Distribution, the program can be started by executing the file main.py. 

From the command line this is accomplished by executing the command 'python /path/to/main.py'  It my be necessary to instead use the 'pythonw' command: 'pythonw /path/to/main.py'

Its possible to create an executable file to launch the program in a number of ways.
On OS X the easiest way is to creat a text file that begins with '#! /usr/bin/'
Then put the line 'python /path/to/file/main.py'

Save this file as pLease.command 
Give the file executbale previleges using chmod +x
Now this file should be an executable script which will run the puthon code and can be placed anywhere in your computer's directory structure.



