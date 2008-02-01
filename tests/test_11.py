# -*- coding: UTF-8 -*-

# Checking if pymacs.py works (Emacs and pymacs-services unused).

import re
import setup

from Pymacs import lisp, pymacs

def test_print_lisp():

    def validate(input, quoted, expected):
        fragments = []
        pymacs.print_lisp(input, fragments.append, quoted)
        output = re.sub(r'\(pymacs-(defun|python) [0-9]*\)',
                        r'(pymacs-\1 0)',
                        ''.join(fragments))
        assert output == expected, (output, expected)

    for selfeval, python, emacs in setup.each_equivalence():
        python = eval(python)
        yield validate, python, False, emacs
        if selfeval:
            yield validate, python, True, emacs
        else:
            yield validate, python, True, '\'' + emacs
