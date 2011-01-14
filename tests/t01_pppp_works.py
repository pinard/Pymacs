# -*- coding: utf-8 -*-

# Checking if the Poor's Python Pre-Processor works.

exec(compile(open('../pppp').read(), '../pppp', 'exec'))

def setup_module(module):
    run.synclines = False
    run.context = {'TRUE': True, 'FALSE': False}

def validate(input, expected):

    def validate1(input, expected):
        fragments = []
        run.transform_file('pppp.py', input.splitlines(True), fragments.append)
        output = ''.join(fragments)
        assert output == expected, (output, expected)

    validate1(input, expected)
    prefix = ' ' * run.indent
    validate1(
            ''.join([prefix + line for line in input.splitlines(True)]),
            ''.join([prefix + line for line in expected.splitlines(True)]))

def test_none():

    yield (validate,
            '',

            '')

    yield (validate,
            'line1\n',

            'line1\n')

    yield (validate,
            'line1\n'
            'line2\n',

            'line1\n'
            'line2\n')

def test_yes():

    yield (validate,
            'if TRUE:\n'
            '    line1\n'
            'line2\n'
            'line3\n',

            'line1\n'
            'line2\n'
            'line3\n')

    yield (validate,
            'if TRUE:\n'
            '    line1\n'
            '    line2\n'
            'line3\n',

            'line1\n'
            'line2\n'
            'line3\n')

    yield (validate,
            'if TRUE:\n'
            '    line1\n'
            '    line2\n'
            '    line3\n',

            'line1\n'
            'line2\n'
            'line3\n')

    yield (validate,
            'line1\n'
            'if TRUE:\n'
            '    line2\n'
            'line3\n',

            'line1\n'
            'line2\n'
            'line3\n')

    yield (validate,
            'line1\n'
            'if TRUE:\n'
            '    line2\n'
            '    line3\n',

            'line1\n'
            'line2\n'
            'line3\n')

    yield (validate,
            'line1\n'
            'line2\n'
            'if TRUE:\n'
            '    line3\n',

            'line1\n'
            'line2\n'
            'line3\n')

    yield (validate,
            'if TRUE:\n'
            '    line1\n'
            'if TRUE:\n'
            '    line2\n'
            'line3\n',

            'line1\n'
            'line2\n'
            'line3\n')

    yield (validate,
            'if TRUE:\n'
            '    line1\n'
            'line2\n'
            'if TRUE:\n'
            '    line3\n',

            'line1\n'
            'line2\n'
            'line3\n')

    yield (validate,
            'if TRUE:\n'
            '    line1\n'
            'if TRUE:\n'
            '    line2\n'
            'if TRUE:\n'
            '    line3\n',

            'line1\n'
            'line2\n'
            'line3\n')

    yield (validate,
            'line1\n'
            'if TRUE:\n'
            '    line2\n'
            'if TRUE:\n'
            '    line3\n',

            'line1\n'
            'line2\n'
            'line3\n')

def test_no():

    yield (validate,
            'if FALSE:\n'
            '    line1\n'
            'line2\n'
            'line3\n',

            'line2\n'
            'line3\n')

    yield (validate,
            'if FALSE:\n'
            '    line1\n'
            '    line2\n'
            'line3\n',

            'line3\n')

    yield (validate,
            'if FALSE:\n'
            '    line1\n'
            '    line2\n'
            '    line3\n',

            '')

    yield (validate,
            'line1\n'
            'if FALSE:\n'
            '    line2\n'
            'line3\n',

            'line1\n'
            'line3\n')

    yield (validate,
            'line1\n'
            'if FALSE:\n'
            '    line2\n'
            '    line3\n',

            'line1\n')

    yield (validate,
            'line1\n'
            'line2\n'
            'if FALSE:\n'
            '    line3\n',

            'line1\n'
            'line2\n')

    yield (validate,
            'if FALSE:\n'
            '    line1\n'
            'if FALSE:\n'
            '    line2\n'
            'line3\n',

            'line3\n')

    yield (validate,
            'if FALSE:\n'
            '    line1\n'
            'line2\n'
            'if FALSE:\n'
            '    line3\n',

            'line2\n')

    yield (validate,
            'if FALSE:\n'
            '    line1\n'
            'if FALSE:\n'
            '    line2\n'
            'if FALSE:\n'
            '    line3\n',

            '')

    yield (validate,
            'line1\n'
            'if FALSE:\n'
            '    line2\n'
            'if FALSE:\n'
            '    line3\n',

            'line1\n')

def test_unknown():

    yield (validate,
            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'line3\n',

            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'line3\n')

    yield (validate,
            'if UNKNOWN:\n'
            '    line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'if UNKNOWN:\n'
            '    line3\n',

            'if UNKNOWN:\n'
            '    line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'if UNKNOWN:\n'
            '    line3\n')

def test_yes_else():

    yield (validate,
            'if TRUE:\n'
            '    line1\n'
            'else:\n'
            '    line2\n'
            'line3\n',

            'line1\n'
            'line3\n')

    yield (validate,
            'if TRUE:\n'
            '    line1\n'
            '    line2\n'
            'else:\n'
            '    line3\n',

            'line1\n'
            'line2\n')

    yield (validate,
            'line1\n'
            'if TRUE:\n'
            '    line2\n'
            'else:\n'
            '    line3\n',

            'line1\n'
            'line2\n')

    yield (validate,
            'if TRUE:\n'
            '    line1\n'
            'if TRUE:\n'
            '    line2\n'
            'else:\n'
            '    line3\n',

            'line1\n'
            'line2\n')

    yield (validate,
            'if TRUE:\n'
            '    line1\n'
            'else:\n'
            '    line2\n'
            'if TRUE:\n'
            '    line3\n',

            'line1\n'
            'line3\n')

def test_no_else():

    yield (validate,
            'if FALSE:\n'
            '    line1\n'
            'else:\n'
            '    line2\n'
            'line3\n',

            'line2\n'
            'line3\n')

    yield (validate,
            'if FALSE:\n'
            '    line1\n'
            '    line2\n'
            'else:\n'
            '    line3\n',

            'line3\n')

    yield (validate,
            'line1\n'
            'if FALSE:\n'
            '    line2\n'
            'else:\n'
            '    line3\n',

            'line1\n'
            'line3\n')

    yield (validate,
            'if FALSE:\n'
            '    line1\n'
            'if FALSE:\n'
            '    line2\n'
            'else:\n'
            '    line3\n',

            'line3\n')

    yield (validate,
            'if FALSE:\n'
            '    line1\n'
            'else:\n'
            '    line2\n'
            'if FALSE:\n'
            '    line3\n',

            'line2\n')

def test_unknown_else():

    yield (validate,
            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'else:\n'
            '    line3\n'
            'line4\n',

            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'else:\n'
            '    line3\n'
            'line4\n')

def test_elif():

    yield (validate,
            'line1\n'
            'if TRUE:\n'
            '    line2\n'
            'elif TRUE:\n'
            '    line3\n'
            'elif TRUE:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'line2\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if TRUE:\n'
            '    line2\n'
            'elif TRUE:\n'
            '    line3\n'
            'elif FALSE:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'line2\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if TRUE:\n'
            '    line2\n'
            'elif TRUE:\n'
            '    line3\n'
            'elif UNKNOWN:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'line2\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if TRUE:\n'
            '    line2\n'
            'elif FALSE:\n'
            '    line3\n'
            'elif TRUE:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'line2\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if TRUE:\n'
            '    line2\n'
            'elif FALSE:\n'
            '    line3\n'
            'elif FALSE:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'line2\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if TRUE:\n'
            '    line2\n'
            'elif FALSE:\n'
            '    line3\n'
            'elif UNKNOWN:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'line2\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if TRUE:\n'
            '    line2\n'
            'elif UNKNOWN:\n'
            '    line3\n'
            'elif TRUE:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'line2\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if TRUE:\n'
            '    line2\n'
            'elif UNKNOWN:\n'
            '    line3\n'
            'elif FALSE:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'line2\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if TRUE:\n'
            '    line2\n'
            'elif UNKNOWN:\n'
            '    line3\n'
            'elif UNKNOWN:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'line2\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if FALSE:\n'
            '    line2\n'
            'elif TRUE:\n'
            '    line3\n'
            'elif TRUE:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'line3\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if FALSE:\n'
            '    line2\n'
            'elif TRUE:\n'
            '    line3\n'
            'elif FALSE:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'line3\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if FALSE:\n'
            '    line2\n'
            'elif TRUE:\n'
            '    line3\n'
            'elif UNKNOWN:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'line3\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if FALSE:\n'
            '    line2\n'
            'elif FALSE:\n'
            '    line3\n'
            'elif TRUE:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'line4\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if FALSE:\n'
            '    line2\n'
            'elif FALSE:\n'
            '    line3\n'
            'elif FALSE:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'line5\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if FALSE:\n'
            '    line2\n'
            'elif FALSE:\n'
            '    line3\n'
            'elif UNKNOWN:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'if UNKNOWN:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if FALSE:\n'
            '    line2\n'
            'elif UNKNOWN:\n'
            '    line3\n'
            'elif TRUE:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'if UNKNOWN:\n'
            '    line3\n'
            'else:\n'
            '    line4\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if FALSE:\n'
            '    line2\n'
            'elif UNKNOWN:\n'
            '    line3\n'
            'elif FALSE:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'if UNKNOWN:\n'
            '    line3\n'
            'else:\n'
            '    line5\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if FALSE:\n'
            '    line2\n'
            'elif UNKNOWN:\n'
            '    line3\n'
            'elif UNKNOWN:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'if UNKNOWN:\n'
            '    line3\n'
            'elif UNKNOWN:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'elif TRUE:\n'
            '    line3\n'
            'elif TRUE:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'else:\n'
            '    line3\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'elif TRUE:\n'
            '    line3\n'
            'elif FALSE:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'else:\n'
            '    line3\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'elif TRUE:\n'
            '    line3\n'
            'elif UNKNOWN:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'else:\n'
            '    line3\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'elif FALSE:\n'
            '    line3\n'
            'elif TRUE:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'else:\n'
            '    line4\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'elif FALSE:\n'
            '    line3\n'
            'elif FALSE:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'else:\n'
            '    line5\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'elif FALSE:\n'
            '    line3\n'
            'elif UNKNOWN:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'elif UNKNOWN:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'elif UNKNOWN:\n'
            '    line3\n'
            'elif TRUE:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'elif UNKNOWN:\n'
            '    line3\n'
            'else:\n'
            '    line4\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'elif UNKNOWN:\n'
            '    line3\n'
            'elif FALSE:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'elif UNKNOWN:\n'
            '    line3\n'
            'else:\n'
            '    line5\n'
            'line6\n')

    yield (validate,
            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'elif UNKNOWN:\n'
            '    line3\n'
            'elif UNKNOWN:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            'elif UNKNOWN:\n'
            '    line3\n'
            'elif UNKNOWN:\n'
            '    line4\n'
            'else:\n'
            '    line5\n'
            'line6\n')

def test_nesting():

    yield (validate,
            'line1\n'
            'if TRUE:\n'
            '    line2\n'
            '    if TRUE:\n'
            '        line3\n'
            '    else:\n'
            '        line4\n'
            '    line5\n'
            'else:\n'
            '    line6\n'
            'line7\n',

            'line1\n'
            'line2\n'
            'line3\n'
            'line5\n'
            'line7\n')

    yield (validate,
            'line1\n'
            'if TRUE:\n'
            '    line2\n'
            '    if FALSE:\n'
            '        line3\n'
            '    else:\n'
            '        line4\n'
            '    line5\n'
            'else:\n'
            '    line6\n'
            'line7\n',

            'line1\n'
            'line2\n'
            'line4\n'
            'line5\n'
            'line7\n')

    yield (validate,
            'line1\n'
            'if TRUE:\n'
            '    line2\n'
            '    if UNKNOWN:\n'
            '        line3\n'
            '    else:\n'
            '        line4\n'
            '    line5\n'
            'else:\n'
            '    line6\n'
            'line7\n',

            'line1\n'
            'line2\n'
            'if UNKNOWN:\n'
            '    line3\n'
            'else:\n'
            '    line4\n'
            'line5\n'
            'line7\n')

    yield (validate,
            'line1\n'
            'if FALSE:\n'
            '    line2\n'
            '    if TRUE:\n'
            '        line3\n'
            '    else:\n'
            '        line4\n'
            '    line5\n'
            'else:\n'
            '    line6\n'
            'line7\n',

            'line1\n'
            'line6\n'
            'line7\n')

    yield (validate,
            'line1\n'
            'if FALSE:\n'
            '    line2\n'
            '    if FALSE:\n'
            '        line3\n'
            '    else:\n'
            '        line4\n'
            '    line5\n'
            'else:\n'
            '    line6\n'
            'line7\n',

            'line1\n'
            'line6\n'
            'line7\n')

    yield (validate,
            'line1\n'
            'if FALSE:\n'
            '    line2\n'
            '    if UNKNOWN:\n'
            '        line3\n'
            '    else:\n'
            '        line4\n'
            '    line5\n'
            'else:\n'
            '    line6\n'
            'line7\n',

            'line1\n'
            'line6\n'
            'line7\n')

    yield (validate,
            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            '    if TRUE:\n'
            '        line3\n'
            '    else:\n'
            '        line4\n'
            '    line5\n'
            'else:\n'
            '    line6\n'
            'line7\n',

            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            '    line3\n'
            '    line5\n'
            'else:\n'
            '    line6\n'
            'line7\n')

    yield (validate,
            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            '    if FALSE:\n'
            '        line3\n'
            '    else:\n'
            '        line4\n'
            '    line5\n'
            'else:\n'
            '    line6\n'
            'line7\n',

            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            '    line4\n'
            '    line5\n'
            'else:\n'
            '    line6\n'
            'line7\n')

    yield (validate,
            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            '    if UNKNOWN:\n'
            '        line3\n'
            '    else:\n'
            '        line4\n'
            '    line5\n'
            'else:\n'
            '    line6\n'
            'line7\n',

            'line1\n'
            'if UNKNOWN:\n'
            '    line2\n'
            '    if UNKNOWN:\n'
            '        line3\n'
            '    else:\n'
            '        line4\n'
            '    line5\n'
            'else:\n'
            '    line6\n'
            'line7\n')

def test_regression():

    yield (validate,
            'if TRUE:\n'
            '    line1\n'
            'else:\n'
            '    line2\n'
            '    if FALSE:\n'
            '        line3\n'
            '    else:\n'
            '        line4\n'
            '    line5\n'
            'line6\n',

            'line1\n'
            'line6\n')
