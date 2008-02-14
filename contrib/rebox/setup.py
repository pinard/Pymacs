#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '.')
from Pymacs import __package__, __version__
del sys.path[0]

from distutils.core import setup

setup(name=__package__, version=__version__,
      description="Refilling comment boxes from within Emacs.",
      author='François Pinard', author_email='pinard@iro.umontreal.ca',
      url='http://pinard.progiciels-bpi.ca',
      scripts=['rebox'],
      packages=['Pymacs.Rebox'])
