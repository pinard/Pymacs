# -*- coding: UTF-8 -*-

# Checking if pymacs.py works (Emacs and pymacs-services unused).

import re
import setup

from Pymacs import lisp, pymacs

def test_print_lisp():

    def validate(quoted, input, expected):
        fragments = []
        pymacs.print_lisp(input, fragments.append, quoted)
        output = re.sub(r'\(pymacs-(defun|python) [0-9]*\)',
                        r'(pymacs-\1 0)',
                        ''.join(fragments))
        assert output == expected, (output, expected)

    for quotable, python, emacs in setup.each_equivalence():
        yield validate, False, eval(python), emacs
        if quotable:
            yield validate, True, eval(python), '\'' + emacs
        else:
            yield validate, True, eval(python), emacs
