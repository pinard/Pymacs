# -*- coding: utf-8 -*-

# Python side of the testing protocol.

__metaclass__ = type
import os

try:
    import signal
except ImportError:
    # Jython misses this module.
    signal = None

try:
    import subprocess
except ImportError:
    # Jython misses this module.
    subprocess = None

# Make sure that ../Pymacs will be found within this process.
import sys
if '..' not in sys.path:
    sys.path.insert(0, '..')

from Pymacs import lisp, pymacs

class Launch:
    # Make sure that ../Pymacs will be found in external processes.

    def __init__(self):
        self.pythonpath_saved = os.environ.get('PYTHONPATH')
        os.environ['PYTHONPATH'] = '..'

    def __del__(self):
        if self.pythonpath_saved is None:
            del os.environ['PYTHONPATH']
        else:
            os.environ['PYTHONPATH'] = self.pythonpath_saved

class Emacs(Launch):
    # Requests towards Emacs are written to file "_request", while
    # replies from Emacs are read from file "_reply".  We call Emacs
    # attention by erasing "_reply", and Emacs calls our attention by
    # erasing "_request".  These rules guarantee that no file is ever
    # read by one side before it has been fully written by the other.
    # Busy waiting, with built-in delays, is used on both sides.

    popen = None

    def __init__(self):
        Launch.__init__(self)
        self.cleanup()
        import atexit
        atexit.register(self.cleanup)
        emacs = os.environ.get('PYMACS_EMACS') or 'emacs'
        self.command = emacs, '-batch', '-q', '-l', 'setup.el'
        if subprocess is None:
            self.command = self.command + ('-f', 'run-one-request')
        else:
            self.command = self.command + ('-f', 'run-all-requests')

    def cleanup(self):
        if self.popen is not None:
            self.popen.poll()
            if self.popen.returncode is None:
                if signal is not None:
                    os.kill(self.popen.pid, signal.SIGINT)
                    os.waitpid(self.popen.pid, 0)
            self.popen = None
        if os.path.exists('_request'):
            os.remove('_request')
        if os.path.exists('_reply'):
            os.remove('_reply')

    def receive(self):
        if subprocess is None:
            handle = file('_reply')
            buffer = handle.read()
            handle.close()
        else:
            import time
            while os.path.exists('_request'):
                self.popen.poll()
                assert self.popen.returncode is None, self.popen.returncode
                time.sleep(0.01)
            self.popen.poll()
            assert self.popen.returncode is None, self.popen.returncode
            handle = file('_reply')
            buffer = handle.read()
            handle.close()
        return buffer

    def send(self, text):
        handle = file('_request', 'w')
        handle.write(text)
        handle.close()
        if subprocess is None:
            status = os.system(' '.join(self.command))
            assert status == 0, status
        else:
            if os.path.exists('_reply'):
                os.remove('_reply')
            if self.popen is None:
                self.popen = subprocess.Popen(self.command)
            self.popen.poll()
            assert self.popen.returncode is None, self.popen.returncode

def start_emacs():
    Emacs.services = Emacs()

def stop_emacs():
    Emacs.services.cleanup()

def ask_emacs(text, printer=None):
    if printer is not None:
        text = '(%s %s)' % (printer, text)
    Emacs.services.send(text)
    return Emacs.services.receive()

class Python(Launch):

    def __init__(self):
        Launch.__init__(self)
        # Start a Pymacs helper subprocess for executing Python code.
        python = os.environ.get('PYMACS_PYTHON') or 'python'
        command = python + ' -c "from Pymacs.pymacs import main; main(\'..\')"'
        import popen2
        self.output, self.input = popen2.popen4(command)
        text = self.receive()
        from Pymacs import __version__
        assert text == '(version "%s")\n' % __version__, repr(text)

    def receive(self):
        # Receive a Lisp expression from the Pymacs helper.
        text = self.output.read(3)
        if not text or text[0] != '<':
            if text == 'Tra':
                # Likely a traceback, and the Pymacs helper terminated.
                diagnostic = 'got:\n' + text + self.output.read()
            else:
                diagnostic = 'got ' + repr(text)
            raise pymacs.ProtocolError("'<' expected, %s\n" % diagnostic)
        while text[-1] != '\t':
            text = text + self.output.read(1)
        return self.output.read(int(text[1:-1]))

    def send(self, text):
        # Send TEXT, a Python expression, to the Pymacs helper.
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
