# extract-list

## Background

To be written

## Using it

To be written

## For developers

### Needed environment

#### OS

For running the script and running the test suite you need a mac or a Linux computer. Even if the resulting application can be installed and used on Windows, the scripts for building and testing is only implemented for mac and Linux.

#### Python version

The tests and the script for running the tests, coverage, mypy etc. requires Python version 3.12.6 or newer.

#### Zsh

The scripts are all zsh. zsh is available by default on modern macs. zsh can easily be installed on Linux (on Ubuntu: sudo apt install zsh).

### Internal APIs not quaranteed

The internal APIs in this package are not guaranteed to be stable. They can change without warning between versions.

### Building application

There are 3 scripts for building the application

* setup_build_environment.zsh
  Run this script first to get the environment set up for building
* doBuild.zsh
  Run this script to build an installation package (.whl) and to run the tests on it in a venv (virtual environment).
* clean.zsh
  Deletes all files that was produced by the build to start over from a clean state.

The "testing" includes pytest, pylint, flake8 and mypy.

After running doBuild.zsh you can open reports/index.htm to see all test reports.

After running doBuild.zsh you can do manual test of the built and installed application in the virtual environment ./venv
