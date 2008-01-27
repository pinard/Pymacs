# -*- coding: UTF-8 -*-

# Make sure the ../pymacs-services script will be found.
import os
value = os.getenv('PATH')
if value is None:
    os.putenv('PATH', '..')
elif '..' not in value.split(':'):
    os.putenv('PATH', '..:' + value)

# Make sure the ../Pymacs module will be found.
import sys
if '..' not in sys.path:
    sys.path.insert(0, '..')

from Pymacs import pymacs

def emacs(text):
    fragments = []
    pymacs.print_lisp(text, fragments.append, quoted=1)
    return _execute('(emacs %s)' % ''.join(fragments))

def emacs_eval(text):
    fragments = []
    pymacs.print_lisp(text, fragments.append, quoted=1)
    return _execute('(emacs-eval %s)' % ''.join(fragments))

def _execute(text):
    command = ('emacs -batch -q --no-init -L .. -l setup.el -eval \'%s\''
               % text.replace('\'', '\\\''))
    output = os.popen(command).read()
    return eval(output, {}, {})
