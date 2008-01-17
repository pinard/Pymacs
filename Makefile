# Interface between Emacs LISP and Python - Makefile.
# Copyright © 2001, 2002 Progiciels Bourbeau-Pinard inc.
# François Pinard <pinard@iro.umontreal.ca>, 2001.

# The `README' file provides a few good hints about installation.

### Start of customisation.
#
# Somewhere on your shell PATH.
bindir =
# Somewhere on your Emacs LISP load-path.
lispdir =
# Somewhere on your Python sys.path.
pythondir =
# Directory for Python extensions.  Make it empty if you do not use one!
pymacsdir =
#
### End of customisation.

SETUP = python setup.py --quiet
DISTRIBUTION := $(shell ./setup -V)

all:
	$(SETUP) build

install: all
	@./setup \
	  -b '$(bindir)' -l '$(lispdir)' -p '$(pythondir)' -x '$(pymacsdir)'
	$(SETUP) install

dist:
	$(SETUP) sdist
	mv dist/$(DISTRIBUTION).tar.gz .
	rmdir dist
	ls -l *.gz

publish: dist
	chmod 644 $(DISTRIBUTION).tar.gz
	scp -p $(DISTRIBUTION).tar.gz bor:pymacs/
	ssh bor rm -vf pymacs/pymacs.tar.gz
	ssh bor ln -vs $(DISTRIBUTION).tar.gz pymacs/pymacs.tar.gz
	ssh bor ls -Llt pymacs
