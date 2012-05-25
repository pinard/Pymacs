# Interface between Emacs Lisp and Python - Makefile.
# Copyright © 2001, 2002, 2003, 2012 Progiciels Bourbeau-Pinard inc.
# François Pinard <pinard@iro.umontreal.ca>, 2001.

EMACS = emacs
PYTHON = python
RST2LATEX = rst2latex

PYSETUP = $(PYTHON) setup.py
PPPP = $(PYTHON) pppp -C ppppconfig.py

all: prepare
	$(PYSETUP) --quiet build

check: clean-debug
	$(PPPP) pymacs.el.in Pymacs.py.in tests
	cd tests && \
	  EMACS="$(EMACS)" PYTHON="$(PYTHON)" \
	  PYMACS_OPTIONS="-d debug-protocol -s debug-signals" \
	  $(PYTHON) pytest -f t $(TEST)

install: prepare
	$(PYSETUP) install

prepare:
	$(PPPP) Pymacs.py.in pppp.rst.in pymacs.el.in pymacs.rst.in contrib tests

clean: clean-debug
	rm -rf build* contrib/rebox/build
	rm -f */*py.class *.pyc */*.pyc pppp.pdf pymacs.pdf
	$(PPPP) -c *.in contrib tests

clean-debug:
	rm -f tests/debug-protocol tests/debug-signals

pppp.pdf: pppp.rst.in
	$(PPPP) pppp.rst.in
	rm -rf tmp-pdf
	mkdir tmp-pdf
	$(RST2LATEX) --use-latex-toc --input-encoding=UTF-8 \
	  pppp.rst tmp-pdf/pppp.tex
	cd tmp-pdf && pdflatex pppp.tex
	cd tmp-pdf && pdflatex pppp.tex
	mv -f tmp-pdf/pppp.pdf $@
	rm -rf tmp-pdf

pymacs.pdf: pymacs.rst.in
	$(PPPP) pymacs.rst.in
	rm -rf tmp-pdf
	mkdir tmp-pdf
	$(RST2LATEX) --use-latex-toc --input-encoding=UTF-8 \
	  pymacs.rst tmp-pdf/pymacs.tex
	cd tmp-pdf && pdflatex pymacs.tex
	cd tmp-pdf && pdflatex pymacs.tex
	mv -f tmp-pdf/pymacs.pdf $@
	rm -rf tmp-pdf

# The following goals for the maintainer of the Pymacs Web site.

ARCHIVES = web/src/archives
VERSION = `grep '^version' setup.py | sed -e "s/'$$//" -e "s/.*'//"`

publish: pppp.pdf pymacs.pdf pymacs.rst
	find -name '*~' | xargs rm -fv
	version=$(VERSION) && \
	  git archive --format=tar --prefix=Pymacs-$$version/ HEAD . \
	    | gzip > $(ARCHIVES)/Pymacs-$$version.tar.gz
	rm -f $(ARCHIVES)/Pymacs.tar.gz
	version=$(VERSION) && \
	  ln -s Pymacs-$$version.tar.gz $(ARCHIVES)/Pymacs.tar.gz
	make-web -C web
	synchro push alcyon -d entretien/pymacs
	ssh alcyon 'make-web -C entretien/pymacs/web'
