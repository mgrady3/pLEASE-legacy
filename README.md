
#python Low-energy Electron Analysis SuitE: pLEASE

Author: Maxwell Grady

pLEASE is the spiritual successor to all of my previous LEED/LEEM Data analysis scripts and programs such as pyLEEM, pyLEEDLEEM, newLEED, etc

pLEASE provides a full GUI for analysis for LEED and LEEM data sets sdpecifically geared towards viewing and analyzing LEED/LEEM-I(V) data.

## Functionality:
* Full GUI written with the Qt Framework via the python bindings PyQt4
* View LEED and LEEM data sets from a variety of data formats (jpg, png, tiff, and raw bary data)
* Point-and-Click I(V) curve extraction from single  pixel (LEEM) and adjustable sized rectangular box regions (LEED)
* Ouput I(V) data to text files for easy plotting in other programs
* Background subtraction for LEED-I(V)
* FFT generation to analyze the real-space periodicity of a LEED pattern
* Data smoothing using convolution of pre-defined window functions (Hanning, Hamming, Blackman, Flat, etc...)
* Output plots as png files using built in MatPlotLib toolbars for plot navigation and interactivity

pyLEED_LEEM and newLEED are more or less finished projects

pLEASE is a work in progress to merge those two programs into one unified GUI

### Requirements:
* Python distribution 2.7 or 3.x (No Support for Legacy Python versions < 2.7)
* Numpy
* Scipy
* Matplotlib
* Pandas
* openCV
* seaborn
* Qt & PyQt4
* QDarkStyle (a QSS package which sets the overall look and feel of the GUI) 
