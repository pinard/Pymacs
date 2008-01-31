# -*- coding: UTF-8 -*-

# Checking if pymacs-services works.

import re
import setup

def setup_module(module):
    setup.start_python()

def teardown_module(module):
    setup.stop_python()

def test_1():

    def validate(input, expected):
        output = re.sub(r'\(pymacs-(defun|python) [0-9]*\)',
                        r'(pymacs-\1 0)',
                        setup.ask_python(input))
        assert output == expected, (output, expected)

    for quotable, python, emacs in setup.each_equivalence():
        if quotable:
            yield validate, python, '(pymacs-reply \'%s)\n' % emacs
        else:
            yield validate, python, '(pymacs-reply %s)\n' % emacs

def test_2():
    value = setup.ask_python('3 + 5\n')
    assert value == '(pymacs-reply 8)\n', repr(value)

#def test_pymacs_print_for_eval():
#    yield emacs, '3 + 5', '3 + 5'
#
#def test_pymacs_eval():
#    yield emacs_eval, '3 + 5', 8
#    yield emacs_eval, '`3 + 5`', '8'

def emacs(input, output):
    value = setup.emacs(input)
    assert output == value, (output, value)

def emacs_eval(input, output):
    value = setup.emacs_eval(input)
    assert output == value, (output, value)
