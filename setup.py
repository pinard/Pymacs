#!/usr/bin/env python

from distutils.core import setup

setup(name='pymacs',
      version='0.13',
      description='Interface between Emacs LISP and Python.',
      author='François Pinard',
      author_email='pinard@iro.umontreal.ca',
      url='http://www.iro.umontreal.ca/~pinard',
      scripts=['pymacs-services', 'rebox'],
      packages=['Pymacs'])
