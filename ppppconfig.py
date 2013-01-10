# -*- coding: utf-8 -*-
# p4 configuration for Pymacs.


# Overall Pymacs configuration
# ============================

# VERSION is the name of the Pymacs version, as declared within setup.py.

def get_version():
    for line in open('setup.cfg'):
        if '=' in line:
            key, value = line.split('=', 1)
            if key.strip() == 'version':
                return value.strip()

VERSION = get_version()
del get_version


# Configuration for the Emacs Lisp side
# =====================================

# DEFADVICE_OK is 't' when it is safe to use defadvice.  It has been reported
# that, at least under Aquamacs (a MacOS X native port of Emacs), one gets
# "Lisp nesting exceeds `max-lisp-eval-depth'" messages while requesting
# functions documentation (we do not know why).  Set this variable to 'nil'
# as a way to avoid the problem.

DEFADVICE_OK = 't'


# PYTHON gets the command name of the Python interpreter.

def get_python():
    import os
    return os.getenv('PYTHON') or 'python'

PYTHON = get_python()
del get_python


# Configuration for Python (Pymacs helper)
# ========================================

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


# PYTHON3 is True within Python 3.

def get_python3():
    import sys
    return sys.version_info[0] == 3

PYTHON3 = get_python3()
del get_python3
