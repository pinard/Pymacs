#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

try:
    from distutils.core import setup
except ImportError:
    sys.stderr.write("""\

.------------------------------------------------------------------------.
| It seems that the package Distutils is not available for this Python.  |
| You might fetch and install Distutils and retry your command, or else, |
| figure out where the Pymacs/ directory should go, and make that copy.  |
`------------------------------------------------------------------------'

""")
    sys.exit(1)

package = 'Pymacs'
version = '0.25'

setup(name=package, version=version,
      description="Interface between Emacs Lisp and Python",
      author='François Pinard', author_email='pinard@iro.umontreal.ca',
      url='http://pymacs.progiciels-bpi.ca',
      py_modules=['Pymacs'])
