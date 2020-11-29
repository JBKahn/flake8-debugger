Flake8 debugger plugin
======================

Check for pdb;idbp imports and set traces, as well as `from IPython.terminal.embed import InteractiveShellEmbed` and `InteractiveShellEmbed()()`.

This module provides a plugin for ``flake8``, the Python code checker.


Installation
------------

You can install or upgrade ``flake8-debugger`` with these commands::

    $ pip install flake8-debugger
    $ pip install --upgrade flake8-debugger


Plugin for Flake8
-----------------

When both ``flake8 2.2`` and ``flake8-debugger`` are installed, the plugin is
available in ``flake8``::

    $ flake8 --version
    2.0 (pep8: 1.4.5, flake8-debugger: 1.0, pyflakes: 0.6.1)


Changes
-------

##### 3.2.1 - 2019-10-31

* Swapped back from poetry to setup.py :(....python ecosystem issues....

##### 3.2.0 - 2019-10-15

* Forgot to add `breakpoint` support to the last changelog entry as well as fixing a bug introduced into that version that flagged `import builtins` as noteworthy.


##### 3.1.1 - 2019-10-12

* Fix reading from stdin when it is closed (requires flake8 > 2.1).
* Swapped to poetry from setup.py
* Ran black on the repository

##### 3.1.0 - 2018-02-11
* Add a framework classifier for use in pypi.org
* Fix entry_point in setup.py leaving it off by default again
* Detect __import__ debugger statements
* Add support for `pudb` detection

##### 3.0.0 - 2017-05-11
* fix the refactor of the detector in 2.0.0 that was removed from pypi.
* fix a flake8 issue that had it turned off by default.


##### 2.0.0 - 2016-09-19
* refactor detector
* drop official support for python 2.6 and 3.3


##### 1.4.0 - 2015-05-18
* refactor detector, run tests in python 2.6, 2.7 and 3.4 as well as adding a check for InteractiveShellEmbed.

##### 1.3.2 - 2014-11-04
* more tests, fix edge case and debugger identification.

##### 1.3.1 - 2014-11-04
* more tests, a little refactoring and improvements in catching.

##### 1.3 - 2014-11-04
* using ast instead of regular expressions

##### 1.2 - 2014-06-30
* Added a few simple tests

##### 1.1 - 2014-06-30
* First release

##### 1.0 - 2014-06-30
* Whoops
