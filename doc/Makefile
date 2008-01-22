PYTHON = python

p = build
e = $p/.estampille

all: $p/pymacs.dvi $p/pymacs.info $p/pymacs.pdf

dvi: $p/pymacs.dvi
	cp $p/pymacs.dvi .

html: $p/pymacs.html
	ln -sf $p/pymacs.html

info: $p/pymacs.info
	cp $p/pymacs.info .

pdf: $p/pymacs.pdf
	cp $p/pymacs.pdf .

ps: $p/pymacs.ps
	cp $p/pymacs.ps .

clean:
	rm -f pymacs.dvi pymacs.html pymacs.info pymacs.pdf pymacs.ps
	rm -rf $p

$p/pymacs.html: $p/pymacs.texi
	cd $p && make-manual
	ln -sf ../web/manual $@
#	cd $p && LANG= makeinfo -I.. --html --output=html pymacs.texi
#	cd $p && mv html pymacs.html

$p/pymacs.info: $p/pymacs.texi
	cd $p && makeinfo -I.. --no-split pymacs.texi

$p/pymacs.dvi: $p/pymacs.texi
	cd $p && TEXINPUTS=.. texi2dvi pymacs.texi

$p/pymacs.pdf: $p/pymacs.texi
	cd $p && TEXINPUTS=.. texi2pdf pymacs.texi

$p/pymacs.ps: $p/pymacs.dvi
	cd $p && dvips -tletter -o- pymacs.dvi > pymacs.ps

$p/pymacs.texi: pymacs.all $e
	PYTHONPATH=.. $(PYTHON) ../scripts/allout texi pymacs.all > $@-tmp
	mv $@-tmp $@
	echo '(texinfo-master-menu 1) (save-buffer)' > /tmp/emacs-script
	emacs -batch $@ -l /tmp/emacs-script -kill
	rm /tmp/emacs-script

$e:
	install -d $p
	@touch $e
