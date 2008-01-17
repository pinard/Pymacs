# Interface between Emacs LISP and Python - Makefile.
# Copyright © 2001, 2002, 2003 Progiciels Bourbeau-Pinard inc.
# François Pinard <pinard@iro.umontreal.ca>, 2001.

# The `README' file provides a few good hints about installation.

### Start of customisation.
#
# Somewhere on your Emacs LISP load-path.
lispdir =
#
### End of customisation.

PYSETUP = python setup.py

all:
	$(PYSETUP) build

install:
	@./setup -l '$(lispdir)'
	$(PYSETUP) install

tags:
	(find bin -type f; find -name '*.py') | grep -v '~$$' | etags -
