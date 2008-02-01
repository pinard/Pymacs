# -*- coding: UTF-8 -*-

# Python side of the testing protocol.

# Make sure the ../pymacs-services script will be found.
import os
value = os.getenv('PATH')
if value is None:
    os.putenv('PATH', '..')
elif '..' not in value.split(':'):
    os.putenv('PATH', '..:' + value)

# Make sure the ../Pymacs module will be found.
import sys
if '..' not in sys.path:
    sys.path.insert(0, '..')

from Pymacs import lisp, pymacs

class Emacs:
    # Requests towards Emacs are written to file "_request", while
    # replies from Emacs are read from file "_reply".  We call Emacs
    # attention by erasing "_reply", and Emacs calls our attention by
    # erasing "_request".  These rules guarantee that no file is ever
    # read by one side before it has been fully written by the other.
    # Busy waiting, with built-in delays, is used on both sides.

    popen = None

    def __init__(self):
        self.cleanup()
        import atexit
        atexit.register(self.cleanup)

    def cleanup(self):
        if self.popen is not None:
            self.popen.poll()
            if self.popen.returncode is None:
                import signal
                os.kill(self.popen.pid, signal.SIGINT)
                os.waitpid(self.popen.pid, 0)
            self.popen = None
        if os.path.exists('_request'):
            os.remove('_request')
        if os.path.exists('_reply'):
            os.remove('_reply')

    def receive(self):
        import time
        while os.path.exists('_request'):
            self.popen.poll()
            assert self.popen.returncode is None, self.popen.returncode
            time.sleep(0.01)
        self.popen.poll()
        assert self.popen.returncode is None, self.popen.returncode
        return file('_reply').read()

    def send(self, text):
        if self.popen is None:
            file('_reply', 'w')
            command = ('emacs', '-batch', '-q', '--no-init',
                       '-L', '..', '-l', 'setup.el')
            import subprocess
            self.popen = subprocess.Popen(command)
        self.popen.poll()
        assert self.popen.returncode is None, self.popen.returncode
        file('_request', 'w').write(text)
        os.remove('_reply')

def start_emacs():
    Emacs.services = Emacs()

def stop_emacs():
    Emacs.services.cleanup()

def ask_emacs(text):
    Emacs.services.send(text)
    return Emacs.services.receive()

class Python:

    def __init__(self):
        # Start subprocess to execute Python code.
        command = 'pymacs-services ..'
        import popen2
        self.output, self.input = popen2.popen4(command)
        text = self.receive()
        from Pymacs import __version__
        assert text == '(pymacs-version "%s")\n' % __version__, text

    def receive(self):
	# Receive a Lisp expression from pymacs-services.
	text = self.output.read(3)
	if not text or text[0] != '<':
	    raise Protocol.ProtocolError, "`>' expected."
	while text[-1] != '\t':
	    text = text + self.output.read(1)
	return self.output.read(int(text[1:-1]))

    def send(self, text):
	# Send TEXT, a Python expression, to pymacs-services.
	if text[-1] == '\n':
	    self.input.write('>%d\t%s' % (len(text), text))
	else:
	    self.input.write('>%d\t%s\n' % (len(text) + 1, text))
	self.input.flush()

def start_python():
    Python.services = Python()

def stop_python():
    Python.services.input.close()

def ask_python(text):
    Python.services.send(text)
    return Python.services.receive()

def each_equivalence():
    # Repeatedly return (SELFEVAL, PYTHON, LISP) for many objects.
    # SELFEVAL is True whenever in Lisp, (equal (eval OBJECT) OBJECT).
    # PYTHON is a Python string describing the value of repr(OBJECT).
    # LISP is a Python string describing Lisp output for prin1(OBJECT).
    yield True, 'None', 'nil'
    yield True, '3', '3'
    yield True, '0', '0'
    yield True, '-3', '-3'
    yield True, '3.0', '3.0'
    yield True, '0.0', '0.0'
    yield True, '-3.0', '-3.0'
    yield True, '""', '""'
    yield True, '"a"', '"a"'
    yield True, '"byz"', '"byz"'
    yield True, '"c\'bz"', '"c\'bz"'
    yield True, r'"d\"z"', r'"d\"z"'
    yield True, r'"e\\bz"', r'"e\\bz"'
    yield True, r'"f\x08z"', '"f\bz"'
    yield True, r'"g\x0cz"', '"g\fz"'
    yield True, r'"h\nz"', '"h\nz"'
    yield True, r'"i\tz"', '"i\tz"'
    yield True, r'"j\x1bz"', '"j\x1bz"'
    yield True, '()', '[]'
    yield True, '(0,)', '[0]'
    yield True, '(0.0,)', '[0.0]'
    yield True, '("a",)', '["a"]'
    yield True, '(0, 0.0, "a")', '[0 0.0 "a"]'
    yield False, '[]', 'nil'
    yield False, '[0]', '(0)'
    yield False, '[0.0]', '(0.0)'
    yield False, '["a"]', '("a")'
    yield False, '[0, 0.0, "a"]', '(0 0.0 "a")'
    #TODO: Lisp and derivatives
    yield True, 'lisp["nil"]', 'nil'
    yield False, 'lisp["t"]', 't'
    yield False, 'lisp["ab_cd"]', 'ab_cd'
    yield False, 'lisp["ab-cd"]', 'ab-cd'
    yield True, 'lisp.nil', 'nil'
    yield False, 'lisp.t', 't'
    yield False, 'lisp.ab_cd', 'ab-cd'
    yield False, 'ord', '(pymacs-defun 0)'
    yield False, 'object()', '(pymacs-python 0)'

def emacs(text):
    fragments = []
    pymacs.print_lisp(text, fragments.append, quoted=1)
    return _execute('(emacs %s)' % ''.join(fragments))

def emacs_eval(text):
    fragments = []
    pymacs.print_lisp(text, fragments.append, quoted=1)
    return _execute('(emacs-eval %s)' % ''.join(fragments))

def _execute(text):
    command = ('emacs -batch -q --no-init -L .. -l setup.el -eval \'%s\''
               % text.replace('\'', '\\\''))
    output = os.popen(command).read()
    return eval(output, {}, {})
