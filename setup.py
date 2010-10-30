#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys

try:
    from distutils.core import setup
except ImportError:
    setup = None

package = 'Pymacs'
version = '0.24-beta1'
python = os.getenv('python') or 'python'

def adjust(input, output):
    if os.path.exists(output):
        input_time = os.path.getmtime(input)
        output_time = os.path.getmtime(output)
        setup_time = os.path.getmtime('setup.py')
        if output_time > input_time and output_time > setup_time:
            return
        try:
            os.chmod(output, 0644)
        except AttributeError:
            # Jython does not have chmod!
            pass
        os.remove(output)
    sys.stdout.write('adjusting %s -> %s\n' % (input, output))
    buffer = open(input).read()
    open(output, 'w').write(buffer
                            .replace('@PYTHON@', python)
                            .replace('@VERSION@', version))
    try:
        os.chmod(output, 0444)
    except AttributeError:
        # Jython does not have chmod!
        pass

adjust('__init__.py.in', 'Pymacs/__init__.py')
adjust('pymacs.el.in', 'pymacs.el')
adjust('pymacs.rst.in', 'pymacs.rst')

adjust('contrib/Giorgi/setup.py.in', 'contrib/Giorgi/setup.py')
adjust('__init__.py.in', 'contrib/Giorgi/Pymacs/__init__.py')

adjust('contrib/rebox/setup.py.in', 'contrib/rebox/setup.py')
adjust('__init__.py.in', 'contrib/rebox/Pymacs/__init__.py')

if setup is None:
    sys.stderr.write("""\

.------------------------------------------------------------------------.
| It seems that the package Distutils is not available for this Python.  |
| You might fetch and install Distutils and retry your command, or else, |
| figure out where the Pymacs/ directory should go, and make that copy.  |
`------------------------------------------------------------------------'

""")
    sys.exit(1)

setup(name=package, version=version,
      description="Interface between Emacs Lisp and Python",
      author='François Pinard', author_email='pinard@iro.umontreal.ca',
      url='http://pymacs.progiciels-bpi.ca',
      packages=['Pymacs'])
