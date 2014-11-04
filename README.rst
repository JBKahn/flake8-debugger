Flake8 debugger plugin
==================

Check for pdb;idbp imports and set traces.

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

1.3.1 - 2014-11-04
````````````````
* more tests, a little refactoring and improvements in catching.

1.3 - 2014-11-04
````````````````
* using ast instead of regular expressions

1.2 - 2014-06-30
````````````````
* Added a few simple tests

1.1 - 2014-06-30
````````````````
* First release

1.0 - 2014-06-30
````````````````
* Whoops
