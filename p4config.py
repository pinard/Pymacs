# -*- coding: utf-8 -*-
# p4 configuration for Pymacs.

# It has been reported that intercepting all signals (and optionally writing
# a trace of them, create IO problems within the Pymacs helper itself.  So for
# now, IO_ERRORS_WITH_SIGNALS is blindly set to True, until I know better.
# When True, only the Interrupt signal gets monitored.

IO_ERRORS_WITH_SIGNALS = True

# OLD_EXCEPTIONS is True for old Python or Jython versions.

def get_old_exceptions():
    return not isinstance(Exception, type)

OLD_EXCEPTIONS = get_old_exceptions()
del get_old_exceptions

# PYTHON gets the command name of the Python interpreter.

def get_python():
    import os
    return os.getenv('PYTHON') or 'python'

PYTHON = get_python()
del get_python

# PYTHON3 is True within Python 3.

def get_python3():
    import sys
    return sys.version_info[0] == 3

PYTHON3 = get_python3()
del get_python3

# VERSION is the name of the Pymacs version, as declared within setup.py.

def get_version():
    import re
    for line in open('setup.py'):
        match = re.match('version *= *([\'"][^\'"]*[\'"])', line)
        if match:
            return eval(match.group(1))

VERSION = get_version()
del get_version
