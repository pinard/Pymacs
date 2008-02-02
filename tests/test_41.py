# -*- coding: UTF-8 -*-

# Checking if the whole Pymacs works together.

import setup
from Pymacs import lisp

def test_1():
    # 2006-06-20 Sebastian Waschik <sebastian.waschik@gmx.de>

    def action():
        lisp.insert("Test")

    lisp.apply(action, None)

#pymacs_test.interaction = ''
