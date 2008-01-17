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

PYSETUP = python setup.py
DISTRIBUTION := $(shell ./setup -V)

all:
	$(PYSETUP) build

install: all
	@./setup -l '$(lispdir)'
	$(PYSETUP) install

tags:
	(find bin -type f; find -name '*.py') | grep -v '~$$' | etags -

dist:
	$(PYSETUP) sdist
	mv dist/$(DISTRIBUTION).tar.gz .
	rmdir dist
	ls -l *.gz

publish: dist
	traiter README.html > index.html
	chmod 644 index.html $(DISTRIBUTION).tar.gz
	scp -p index.html $(DISTRIBUTION).tar.gz bor:w/pymacs/
	rm index.html $(DISTRIBUTION).tar.gz
	ssh bor rm -vf w/pymacs/Pymacs.tar.gz
	ssh bor ln -vs $(DISTRIBUTION).tar.gz w/pymacs/Pymacs.tar.gz
	ssh bor ls -Llt w/pymacs
