# -*- coding: UTF-8 -*-

# Checking if the whole Pymacs works together.

import setup
from Pymacs import lisp, pymacs

def setup_module(module):
    setup.start_emacs()

def teardown_module(module):
    setup.stop_emacs()

def test_1():

    def validate(input, expected):
        output = setup.ask_emacs('(pymacs-eval %s)' % input, 'prin1')
        assert output == expected, (output, expected)

    for quotable, input, output in (
            (False, None, 'nil'),
            (False, False, 'nil'),
            (False, True, 't'),
            (False, 3, '3'),
            (False, 0, '0'),
            (False, -3, '-3'),
            (False, 3., '3.0'),
            (False, 0., '0.0'),
            (False, -3., '-3.0'),
            (False, '', '""'),
            (False, 'a', '"a"'),
            (False, 'byz', '"byz"'),
            (False, 'c\'bz', '"c\'bz"'),
            (False, 'd"z', r'"d\"z"'),
            (False, 'e\\bz', r'"e\\bz"'),
            (False, 'f\bz', '"f\bz"'),
            (False, 'g\fz', '"g\fz"'),
            (False, 'h\nz', '"h\nz"'),
            (False, 'i\tz', '"i\tz"'),
            (False, 'j\x1bz', '"j\x1bz"'),
            (False, (), '[]'),
            (False, (0,), '[0]'),
            (False, (0.0,), '[0.0]'),
            (False, ('a',), '["a"]'),
            (False, (0, 0.0, "a"), '[0 0.0 "a"]'),
            (True, [], 'nil'),
            (True, [0], '(0)'),
            (True, [0.0], '(0.0)'),
            (True, ['a'], '("a")'),
            (True, [0, 0.0, "a"], '(0 0.0 "a")'),
            (False, lisp['nil'], 'nil'),
            (True, lisp['t'], 't'),
            (True, lisp['ab_cd'], 'ab_cd'),
            (True, lisp['ab-cd'], 'ab-cd'),
            (True, lisp['lambda'], 'lambda'),
            (False, lisp.nil, 'nil'),
            (True, lisp.t, 't'),
            (True, lisp.ab_cd, 'ab-cd'),
            # TODO: Lisp and derivatives
            ):
        fragments = []
        pymacs.print_lisp(repr(input), fragments.append, quotable)
        yield validate, ''.join(fragments), output
    #for input, output in (
    #        (ord, '(pymacs-defun 0)'),
    #        (object(), '(pymacs-python 0)'),
    #        ):
    #    fragments = []
    #    pymacs.print_lisp(input, fragments.append, True)
    #    yield validate, '\'' + ''.join(fragments), output

def test_2():

    def validate(input, expected):
        output = setup.ask_emacs(input, 'prin1')
        assert output == expected, (output, expected)

    yield validate, '(pymacs-eval "3 + 5")', '8'

def notest_3():
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
