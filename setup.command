#!/usr/bin/env bash

# function definitions #
function check_conda {
  if hash conda 2>/dev/null; then
    echo "Found working conda executable!"
    echo
    has_conda=1
  else
    echo
    echo "No working conda executable found. PLEASE Automated Setup can not continue."
    echo "The Anaconda python distibution is freely available from https://www.continuum.io/downloads"
    echo "You will need to install this first if you want to use PLEASE Automated Setup. Otherwise you can install PLEASE manually. Exiting ..."
    sleep 5
    echo "Goodbye!"
    exit
  fi
}

function check_pip {
  if hash pip 2>/dev/null; then
    echo "Found working pip executable!"
    has_pip=1
  else
    echo
    echo "No working pip executable found. PLEASE Automated Setup can not continue."
    echo "Instructions for installing pip can be found here: https://pip.pypa.io/en/stable/installing/"
    echo "You will need to install this first if you want to use PLEASE Automated Setup. Otherwise you can install PLEASE manually. Exiting ..."
    sleep 5
    echo "Goodbye!"
    exit
  fi
}

function check_env {
  if [ -d ~/Anaconda/envs/please/ ];
  then
      env_exists=1
      conda_path_prefix="~/Anaconda/"
      echo "conda env 'please' exists"
  elif [ -d ~/anaconda/envs/please/ ];
  then
    env_exists=1
    conda_path_prefix="~/anaconda/"
    echo "conda env 'please' exists"
  else
      env_exists=0
      sleep 2
      echo "conda env 'please' does not exist."
      echo "There must have been an error creating the environemnt or the user opted to cancel. Exiting ..."
      echo
      sleep 5
      echo "Goodbye!"
      exit
  fi
}

# Main Script #
echo "#########################################"
echo "Welcome to PLEASE Automated Setup!"
echo "#########################################"
sleep 2
echo
echo "PLEASE Automated Setup requires the Anaconda Python Distribution"
echo "Checking for valid conda command utility..."
echo
sleep 5

check_conda

echo "PLEASE Automated requires the pip for installation of the following python packages:"
echo "qdarkstyle and tifffile"
echo
echo "Checking for valid pip command utility..."
sleep 2
echo
check_pip
echo

# we made it this far - thus conda exists and pip exists
# lets create a new virtual environement
echo "Required command utilities are present."
echo
echo "########################################################"
echo "Creating a new conda environment for PLEASE..."
echo "########################################################"
sleep 5
echo
echo "The following packages will be installed with the new environment via conda:"
echo "numpy, scipy, pyqt4, matplotlib, seaborn, pillow, pyyaml, jupyter"
echo
sleep 2
conda create -n please python=3.5 numpy scipy pyqt matplotlib seaborn pillow pyyaml jupyter
echo
echo "Checking valid environement created ..."
check_env
echo
sleep 2
echo "The following packages need to be installed from an alternate conda channel via binstar:"
echo "opencv3"
echo "Activating environment for please installation ..."

source activate please

conda install -c https://conda.binstar.org/menpo opencv3
sleep 2
echo
echo "Environemnt created successfully and conda packages installed."
echo "Attempting to install final packlages from pip ..."
echo
pip install qdarkstyle
pip install tifffile

echo "All packages installed"
echo
echo "Please is ready to be run from the conda environment please"
echo "Goodbye!"
sleep 5
exit
