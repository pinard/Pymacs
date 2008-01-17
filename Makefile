# Interface between Emacs LISP and Python - Makefile.
# Copyright © 2001, 2002 Progiciels Bourbeau-Pinard inc.
# François Pinard <pinard@iro.umontreal.ca>, 2001.

# The `README' file provides a few good hints about installation.

### Start of customisation.
#
# Somewhere on your Emacs LISP load-path.
lispdir =
#
### End of customisation.

SETUP = python setup.py
DISTRIBUTION := $(shell ./setup -V)

all:
	$(SETUP) build

install: all
	@./setup -l '$(lispdir)'
	$(SETUP) install

tags:
	(find bin -type f; find -name '*.py') | grep -v '~$$' | etags -

dist:
	$(SETUP) sdist
	mv dist/$(DISTRIBUTION).tar.gz .
	rmdir dist
	ls -l *.gz

publish: dist
	chmod 644 $(DISTRIBUTION).tar.gz
	scp -p $(DISTRIBUTION).tar.gz bor:w/pymacs/
	ssh bor rm -vf w/pymacs/Pymacs.tar.gz
	ssh bor ln -vs $(DISTRIBUTION).tar.gz w/pymacs/Pymacs.tar.gz
	ssh bor ls -Llt w/pymacs
