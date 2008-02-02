# -*- coding: UTF-8 -*-

# Checking if the whole Pymacs works together.

import setup
from Pymacs import lisp

def setup_module(module):
    setup.start_emacs()

def teardown_module(module):
    setup.stop_emacs()

def test_1():

    def validate(input, expected):
        output = setup.ask_emacs(input)
        assert output == expected, (output, expected)

    validate('(princ (pymacs-eval "3 + 5"))', '8')

def notest_1():
    # 2006-06-20 Sebastian Waschik <sebastian.waschik@gmx.de>

    def action():
        lisp.insert("Test")

    return
    lisp.apply(action, None)

#pymacs_test.interaction = ''
