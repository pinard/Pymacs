# -*- coding: UTF-8 -*-

import setup

def test_pymacs_print_for_eval():
    yield emacs, '3 + 5', '3 + 5'

def test_pymacs_eval():
    yield emacs_eval, '3 + 5', 8
    yield emacs_eval, '`3 + 5`', '8'

def emacs(input, output):
    value = setup.emacs(input)
    assert output == value, (output, value)

def emacs_eval(input, output):
    value = setup.emacs_eval(input)
    assert output == value, (output, value)
