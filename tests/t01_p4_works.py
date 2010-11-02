# -*- coding: utf-8 -*-

# Checking if the Poor Python Pre Processor works.

exec(compile(open('../p4').read(), '../p4', 'exec'))

def setup_module(module):
    run.context = {'YES': True, 'YES2': True, 'YES3': True,
                   'NO': False, 'NO2': False, 'NO3': False}

def validate(input, expected):

    def validate1(input, expected):
        fragments = []
        run.transform_file('p4.py', input.splitlines(True), fragments.append)
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
    yield (validate,
            'line1\n'
            'line2\n'
            'line3\n',
            'line1\n'
            'line2\n'
            'line3\n')

def test_yes():
    yield (validate,
            'if YES:\n'
            '    line1\n'
            'line2\n'
            'line3\n',
            'line1\n'
            'line2\n'
            'line3\n')
    yield (validate,
            'if YES:\n'
            '    line1\n'
            '    line2\n'
            'line3\n',
            'line1\n'
            'line2\n'
            'line3\n')
    yield (validate,
            'if YES:\n'
            '    line1\n'
            '    line2\n'
            '    line3\n',
            'line1\n'
            'line2\n'
            'line3\n')
    yield (validate,
            'line1\n'
            'if YES:\n'
            '    line2\n'
            'line3\n',
            'line1\n'
            'line2\n'
            'line3\n')
    yield (validate,
            'line1\n'
            'if YES:\n'
            '    line2\n'
            '    line3\n',
            'line1\n'
            'line2\n'
            'line3\n')
    yield (validate,
            'line1\n'
            'line2\n'
            'if YES:\n'
            '    line3\n',
            'line1\n'
            'line2\n'
            'line3\n')
    yield (validate,
            'if YES:\n'
            '    line1\n'
            'if YES:\n'
            '    line2\n'
            'line3\n',
            'line1\n'
            'line2\n'
            'line3\n')
    yield (validate,
            'if YES:\n'
            '    line1\n'
            'line2\n'
            'if YES:\n'
            '    line3\n',
            'line1\n'
            'line2\n'
            'line3\n')
    yield (validate,
            'if YES:\n'
            '    line1\n'
            'if YES:\n'
            '    line2\n'
            'if YES:\n'
            '    line3\n',
            'line1\n'
            'line2\n'
            'line3\n')
    yield (validate,
            'line1\n'
            'if YES:\n'
            '    line2\n'
            'if YES:\n'
            '    line3\n',
            'line1\n'
            'line2\n'
            'line3\n')

def test_no():
    yield (validate,
            'if NO:\n'
            '    line1\n'
            'line2\n'
            'line3\n',
            'line2\n'
            'line3\n')
    yield (validate,
            'if NO:\n'
            '    line1\n'
            '    line2\n'
            'line3\n',
            'line3\n')
    yield (validate,
            'if NO:\n'
            '    line1\n'
            '    line2\n'
            '    line3\n',
            '')
    yield (validate,
            'line1\n'
            'if NO:\n'
            '    line2\n'
            'line3\n',
            'line1\n'
            'line3\n')
    yield (validate,
            'line1\n'
            'if NO:\n'
            '    line2\n'
            '    line3\n',
            'line1\n')
    yield (validate,
            'line1\n'
            'line2\n'
            'if NO:\n'
            '    line3\n',
            'line1\n'
            'line2\n')
    yield (validate,
            'if NO:\n'
            '    line1\n'
            'if NO:\n'
            '    line2\n'
            'line3\n',
            'line3\n')
    yield (validate,
            'if NO:\n'
            '    line1\n'
            'line2\n'
            'if NO:\n'
            '    line3\n',
            'line2\n')
    yield (validate,
            'if NO:\n'
            '    line1\n'
            'if NO:\n'
            '    line2\n'
            'if NO:\n'
            '    line3\n',
            '')
    yield (validate,
            'line1\n'
            'if NO:\n'
            '    line2\n'
            'if NO:\n'
            '    line3\n',
            'line1\n')

def test_yes_else():
    yield (validate,
            'if YES:\n'
            '    line1\n'
            'else:\n'
            '    line2\n'
            'line3\n',
            'line1\n'
            'line3\n')
    yield (validate,
            'if YES:\n'
            '    line1\n'
            '    line2\n'
            'else:\n'
            '    line3\n',
            'line1\n'
            'line2\n')
    yield (validate,
            'line1\n'
            'if YES:\n'
            '    line2\n'
            'else:\n'
            '    line3\n',
            'line1\n'
            'line2\n')
    yield (validate,
            'if YES:\n'
            '    line1\n'
            'if YES:\n'
            '    line2\n'
            'else:\n'
            '    line3\n',
            'line1\n'
            'line2\n')
    yield (validate,
            'if YES:\n'
            '    line1\n'
            'else:\n'
            '    line2\n'
            'if YES:\n'
            '    line3\n',
            'line1\n'
            'line3\n')

def test_no_else():
    yield (validate,
            'if NO:\n'
            '    line1\n'
            'else:\n'
            '    line2\n'
            'line3\n',
            'line2\n'
            'line3\n')
    yield (validate,
            'if NO:\n'
            '    line1\n'
            '    line2\n'
            'else:\n'
            '    line3\n',
            'line3\n')
    yield (validate,
            'line1\n'
            'if NO:\n'
            '    line2\n'
            'else:\n'
            '    line3\n',
            'line1\n'
            'line3\n')
    yield (validate,
            'if NO:\n'
            '    line1\n'
            'if NO:\n'
            '    line2\n'
            'else:\n'
            '    line3\n',
            'line3\n')
    yield (validate,
            'if NO:\n'
            '    line1\n'
            'else:\n'
            '    line2\n'
            'if NO:\n'
            '    line3\n',
            'line2\n')

def test_regression():
    yield (validate,
            'if YES:\n'
            '    line1\n'
            'else:\n'
            '    line2\n'
            '    if NO:\n'
            '        line3\n'
            '    else:\n'
            '        line4\n'
            '    line5\n'
            'line6\n',
            'line1\n'
            'line6\n')
