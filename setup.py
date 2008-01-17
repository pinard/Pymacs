#!/usr/bin/env python
# -*- coding: Latin-1 -*-

import sys
sys.path.insert(0, '.')
from Pymacs import __package__, __version__
del sys.path[0]

def update_version_texi():
    import os, stat, time
    edited = ('%.4d-%.2d-%.2d'
              % time.localtime(os.stat('doc/pymacs.all')[stat.ST_MTIME])[:3])
    version_texi = ('@set VERSION %s\n'
                    '@set EDITION %s\n'
                    '@set UPDATED %s\n'
                    % (__version__, edited, edited))
    if file('doc/version.texi').read() != version_texi:
        file('doc/version.texi', 'w').write(version_texi)

from distutils.core import setup

update_version_texi()

# If you want `Allout' installed, then add `scripts/allout' to the `scripts'
# list and `Allout' to the `packages' list.

setup(name=__package__, version=__version__,
      description="Interface between Emacs LISP and Python.",
      author='François Pinard', author_email='pinard@iro.umontreal.ca',
      url='http://www.iro.umontreal.ca/~pinard',
      scripts=['scripts/pymacs-services', 'scripts/rebox'],
      packages=['Pymacs', 'Pymacs.Nn', 'Pymacs.Rebox'])
