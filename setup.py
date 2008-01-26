#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
sys.path.insert(0, '.')
from Pymacs import __package__, __version__
del sys.path[0]

from distutils.core import setup

setup(name=__package__, version=__version__,
      description="Interface between Emacs LISP and Python.",
      author='François Pinard', author_email='pinard@iro.umontreal.ca',
      url='http://pymacs.progiciels-bpi.ca',
      scripts=['pymacs-services'],
      packages=['Pymacs'])
