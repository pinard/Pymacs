#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '.')
from Pymacs import __package__, __version__
del sys.path[0]

from distutils.core import setup

setup(name=__package__, version=__version__,
      description="Interface between Emacs Lisp and Python.",
      author='Giovanni Giorgi', author_email='jj@objectsroot.com',
      url='http://blog.objectsroot.com/projects/pymacs',
      packages=['Pymacs'])
