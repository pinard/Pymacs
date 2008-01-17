#!/usr/bin/env python
# Copyright © 2001 Progiciels Bourbeau-Pinard inc.
# François Pinard <pinard@iro.umontreal.ca>, 2001.

"""\
Interface between Emacs LISP and Python - Python part.

Emacs may launch this module as a stand-alone program, in which case it
acts as a server of Python facilities for that Emacs session, reading
requests from standard input and writing replies on standard output.

This module may also be usefully imported by those other Python modules.
See the Pymacs documentation for more information.
"""

import os, string, sys, types

# Python services for Emacs applications.

def main(*arguments):
    """\
Execute Python services for Emacs, and Emacs services for Python.
This program is meant to be called from Emacs, using `pymacs.el'.

The program arguments are additional search paths for Python modules.
"""
    arguments = list(arguments)
    arguments.reverse()
    for argument in arguments:
        if os.path.isdir(argument):
            sys.path.insert(0, argument)
    lisp._server.send('(pymacs-version "@VERSION@")')
    lisp._server.loop()

class Server:
    ProtocolError = 'Serious error, should stop'
    ReplyException = 'Reply received from Emacs'
    ErrorException = 'Error returned from Emacs'

    def loop(self):
        # The server loop repeatedly receives a request from Emacs and
        # returns a response, which is either the value of the received
        # Python expression, or the Python traceback if an error occurs
        # while evaluating the expression.

        # The server loop may also be executed, as a recursive invocation,
        # in the context of Emacs serving a Python request.  In which
        # case, we might also receive a notification from Emacs telling
        # that the reply has been transmitted, or that an error occurred.
        # A reply notification from Emacs interrupts the loop: the result
        # of this function is the value returned from Emacs.
        while 1:
            try:
                text = self.receive()
                if text[:5] == 'exec ':
                    exec eval(text[5:], {}, {})
                    status = 'reply'
                    argument = None
                else:
                    status = 'reply'
                    argument = eval(text)
            except Server.ReplyException, value:
                return value
            except Server.ErrorException, message:
                status = 'error'
                argument = message
            except Server.ProtocolError, message:
                sys.stderr.write("Protocol error: %s\n" % message)
                sys.exit(1)
            except:
                import StringIO, traceback
                message = StringIO.StringIO()
                traceback.print_exc(file=message)
                status = 'error'
                argument = message.getvalue()
            # Send an expression to EMACS applying FUNCTION over ARGUMENT,
            # where FUNCTION is `pymacs-STATUS'.
            fragments = []
            write = fragments.append
            write('(pymacs-%s ' % status)
            print_lisp(argument, write, quoted=1)
            write(')')
            self.send(string.join(fragments, ''))

    def receive(self):
        # Receive a Python expression Emacs and return its text, unevaluated.
        text = sys.stdin.read(3)
        if not text or text[0] != '>':
            raise Server.ProtocolError, "`>' expected."
        while text[-1] != '\t':
            text = text + sys.stdin.read(1)
        return sys.stdin.read(int(text[1:-1]))

    def send(self, text):
        # Send TEXT to Emacs, which is an expression to evaluate.
        if text[-1] == '\n':
            sys.stdout.write('<%d\t%s' % (len(text), text))
        else:
            sys.stdout.write('<%d\t%s\n' % (len(text) + 1, text))
        sys.stdout.flush()

def reply(value):
    # This function implements the `reply' pseudo-function.
    raise Server.ReplyException, value

def error(message):
    # This function implements the `error' pseudo-function.
    raise Server.ErrorException, "Emacs: %s" % message

def pymacs_load_helper(lisp_module, prefix):
    # This function imports a Python module, then returns a LISP string,
    # which when later LISP-read and evaluated, will install trampoline
    # definitions in Emacs for accessing the Python module facilities.
    # MODULE may be a full path, yet without the `.py' or `.pyc' extension,
    # in which case the directory is temporarily added to the Python search
    # path for the sole duration of that import.  All defined symbols on
    # the LISP side have have PREFIX prepended, and have Python underlines
    # in Python turned into dashes.  If PREFIX is None, it then defaults
    # to the base name of MODULE, followed by a dash.
    directory, module = os.path.split(lisp_module)
    python_module = string.replace(module, '-', '_')
    if prefix is None:
        prefix = module + '-'
    try:
        if directory:
            sys.path.insert(0, directory)
        try:
            object = __import__(python_module)
        except ImportError:
            return None
    finally:
        if directory:
            del sys.path[0]
    globals().update({python_module: object})  # FIXME: use a better way...
    arguments = []
    for name, value in object.__dict__.items():
        if callable(value) and value is not lisp:
            arguments.append(allocate_handle(value))
            arguments.append(lisp[prefix + string.replace(name, '_', '-')])
    return (lisp.pymacs_defuns, (lisp.quote, tuple(arguments)))

# Many Python types do not have direct LISP equivalents, and may not be
# directly returned to LISP for this reason.  They are rather allocated in
# a list of handles, below, and a handle index is used for communication
# instead of the Python value.  Whenever such a handle is freed from the
# LISP side, its index is added of a freed list for later reuse.

handles = []
freed_list = []

def allocate_handle(value):
    # Allocate some handle to hold VALUE, return its index.
    if freed_list:
        index = freed_list[-1]
        del freed_list[-1]
        handles[index] = value
    else:
        index = len(handles)
        handles.append(value)
    return index

def free_handles(indices):
    # Return many handles to the pool.
    for index in indices:
        handles[index] = None
        freed_list.append(index)

def zombie_handles(indices):
    # Ensure that some handles are _not_ in the pool.
    for index in indices:
        while index >= len(handles):
            freed_list.append(len(handles))
            handles.append(None)
        freed_list.remove(index)
    # Merely to make `*Pymacs*' a bit more readable.
    freed_list.sort()

# Emacs services for Python applications.

class Handle:

    def __init__(self, index):
        self.index = index
        self.length = None

    def __del__(self):
        lisp('(pymacs-free-handle %d)' % self.index)

    def __repr__(self):
        return 'Handle(%s)' % self.index

    def value(self):
        return self

    def copy(self):
        return lisp('(pymacs-expand (aref pymacs-handles %d))' % self.index)

    def __call__(self, *arguments):
        fragments = []
        write = fragments.append
        write('((aref pymacs-handles %d)' % self.index)
        for argument in arguments:
            write(' ')
            print_lisp(argument, write, quoted=1)
        write(')')
        return lisp(string.join(fragments, ''))

    def __len__(self):
        if self.length is None:
            self.length = lisp('(pymacs-handle-length %d)' % self.index)
        return self.length

    def __getitem__(self, key):
        if key < 0 or key >= len(self):
            raise IndexError, key
        return lisp('(pymacs-handle-ref %d %d)' % (self.index, key))

    def __setitem__(self, key, value):
        if key < 0 or key >= len(self):
            raise IndexError, key
        fragments = []
        write = fragments.append
        write('(pymacs-handle-set %d %d ' % (self.index, key))
        print_lisp(value, write, quoted=1)
        write(')')
        lisp(string.join(fragments, ''))

class Symbol:

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return 'Symbol(%s)' % `self.text`

    def value(self):
        return lisp(self.text)

    def copy(self):
        return lisp('(pymacs-expand %s)' % self.text)

    def set(self, value):
        fragments = []
        write = fragments.append
        write('(progn (setq %s ' % self.text)
        print_lisp(value, write, quoted=1)
        write(') nil)')
        lisp(string.join(fragments, ''))

    def __call__(self, *arguments):
        fragments = []
        write = fragments.append
        write('(%s' % self.text)
        for argument in arguments:
            write(' ')
            print_lisp(argument, write, quoted=1)
        write(')')
        return lisp(string.join(fragments, ''))

class Lisp:

    def __init__(self):
        self.__dict__['_cache'] = {'nil': None}
        self.__dict__['_server'] = Server()

    def __call__(self, text):
        self._server.send(text)
        return self._server.loop()

    def __getattr__(self, name):
        if name[0] == '_':
            raise AttributeError, name
        return self[string.replace(name, '_', '-')]

    def __setattr__(self, name, value):
        if name[0] == '_':
            raise AttributeError, name
        self[string.replace(name, '_', '-')] = value

    def __getitem__(self, name):
        try:
            return self._cache[name]
        except KeyError:
            symbol = self._cache[name] = Symbol(name)
            return symbol

    def __setitem__(self, name, value):
        try:
            symbol = self._cache[name]
        except KeyError:
            symbol = self._cache[name] = Symbol(name)
        symbol.set(value)

lisp = Lisp()

def print_lisp(value, write, quoted=0):
    if value is None:
        write('nil')
    elif type(value) == types.IntType:
        write(repr(value))
    elif type(value) == types.FloatType:
        write(repr(value))
    elif type(value) == types.StringType:
        write('"' + repr("'\0" + value)[6:])
    elif type(value) == types.TupleType:
        if quoted:
            write("'")
        if len(value) == 0:
            write('nil')
        elif len(value) == 2 and value[0] == lisp.quote:
            write("'")
            print_lisp(value[1], write)
        else:
            write('(')
            print_lisp(value[0], write)
            for sub_value in value[1:]:
                write(' ')
                print_lisp(sub_value, write)
            write(')')
    elif type(value) == types.ListType:
        write('[')
        if len(value) > 0:
            print_lisp(value[0], write)
            for sub_value in value[1:]:
                write(' ')
                print_lisp(sub_value, write)
        write(']')
    elif isinstance(value, Handle):
        write('(aref pymacs-handles %d)' % value.index)
    elif isinstance(value, Symbol):
        if quoted:
            write("'")
        write(value.text)
    elif callable(value):
        id = allocate_handle(value)
        write('(pymacs-register %d (lambda (&rest arguments)'
              ' (pymacs-apply "handles[%d]" arguments)))' % (id, id))
    else:
        id = allocate_handle(value)
        write("(pymacs-register %d '(pymacs-id %d))" % (id, id))

if __name__ == '__main__':
    apply(main, sys.argv[1:])
