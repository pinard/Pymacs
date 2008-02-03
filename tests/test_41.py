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
        output = setup.ask_emacs(input, 'prin1')
        assert output == expected, (output, expected)

    validate('(pymacs-eval "3 + 5")', '8')

def notest_2():
    # 2006-06-20 Sebastian Waschik <sebastian.waschik@gmx.de>

    def validate(input, expected):
        output = setup.ask_emacs(input, 'prin1')
        assert output == expected, (output, expected)

    setup.ask_emacs('(pymacs-exec "import os\nimport sys")')
#
#    % '''\
#def action(): lisp.insert('Test')
#lisp.apply(action, None)
#''')
