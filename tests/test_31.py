# -*- coding: UTF-8 -*-

# Checking if pymacs.el works (pymacs-services unused).

import setup

def setup_module(module):
    setup.start_emacs()

def teardown_module(module):
    setup.stop_emacs()

def test_1():

    def validate(input, expected):
        output = setup.ask_emacs(input)
        assert output == expected, (output, expected)

    for selfeval, python, emacs in setup.each_equivalence():
        if selfeval:
            yield validate, '(prin1 %s)' % emacs, emacs
        else:
            yield validate, '(prin1 \'%s)' % emacs, emacs

def notest_2():

    def validate(input, expected):
        import re
        output = re.sub(r'\(pymacs-(defun|python) [0-9]*\)',
                        r'(pymacs-\1 0)',
                        setup.ask_emacs(input))
        assert output == expected, (output, expected)

    for selfeval, python, emacs in setup.each_equivalence():
        yield (validate,
               '(pymacs-print-for-eval %s)' % emacs,
               #('(let ((pymacs-forget-mutability t)\n'
               # '   (pymacs-print-for-eval %s)))\n'
               # % emacs),
               python)

def notest_3():
    value = setup.ask_emacs('nil\n')
    assert value == '8', repr(value)

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
