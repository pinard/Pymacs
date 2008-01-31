# -*- coding: UTF-8 -*-

# Checking if pymacs-services loads.

import setup

def test_1():
    setup.start_python()
    setup.stop_python()
