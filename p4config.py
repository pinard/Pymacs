# -*- coding: utf-8 -*-
# p4 configuration for Pymacs.

def get_old_exceptions():
    return not isinstance(Exception, type)

OLD_EXCEPTIONS = get_old_exceptions()
del get_old_exceptions

def get_python():
    import os
    return os.getenv('PYTHON') or 'python'

PYTHON = get_python()
del get_python

def get_python3():
    import sys
    return sys.version_info[0] == 3

PYTHON3 = get_python3()
del get_python3

def get_version():
    import re
    for line in open('setup.py'):
        match = re.match('version *= *([\'"][^\'"]*[\'"])', line)
        if match:
            return eval(match.group(1))

VERSION = get_version()
del get_version
