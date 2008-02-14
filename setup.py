#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from distutils.core import setup

package = 'Pymacs'
version = '0.23-beta9'

def adjust(input, output):
    if os.path.exists(output):
        input_time = os.path.getmtime(input)
        output_time = os.path.getmtime(output)
        setup_time = os.path.getmtime('setup.py')
        if output_time > input_time and output_time > setup_time:
            return
        os.chmod(output, 0644)
        os.remove(output)
    sys.stdout.write('adjusting %s -> %s\n' % (input, output))
    buffer = file(input).read()
    file(output, 'w').write(buffer.replace('@VERSION@', version))
    os.chmod(output, 0444)

adjust('__init__.py.in', 'Pymacs/__init__.py')
adjust('pymacs.el.in', 'pymacs.el')
adjust('pymacs.rst.in', 'pymacs.rst')

setup(name=package, version=version,
      description="Interface between Emacs Lisp and Python.",
      author='François Pinard', author_email='pinard@iro.umontreal.ca',
      url='http://pymacs.progiciels-bpi.ca',
      packages=['Pymacs'])
