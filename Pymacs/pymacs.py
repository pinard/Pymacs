#!/usr/bin/env python
# Copyright © 2001, 2002 Progiciels Bourbeau-Pinard inc.
# François Pinard <pinard@iro.umontreal.ca>, 2001.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.  */

"""\
Interface between Emacs Lisp and Python - Python part.

Emacs may launch this module as a stand-alone program, in which case it
acts as a server of Python facilities for that Emacs session, reading
requests from standard input and writing replies on standard output.

This module may also be usefully imported by those other Python modules.
See the Pymacs documentation (in `README') for more information.
"""

## Note: This code is currently compatible down to Python version 1.5.2.
## It is probably worth keeping it that way for a good while, still.

import os, string, sys, types

# Python services for Emacs applications.

def main(*arguments):
    """\
Execute Python services for Emacs, and Emacs services for Python.
This program is meant to be called from Emacs, using `pymacs.el'.

The program arguments are additional search paths for Python modules.
"""
    from Pymacs import version
    arguments = list(arguments)
    arguments.reverse()
    for argument in arguments:
        if os.path.isdir(argument):
            sys.path.insert(0, argument)
    lisp._protocol.send('(pymacs-version "%s")' % version)
    lisp._protocol.loop()

class Protocol:

    # FIXME: The following should work, but does not:
    #
    # * pymacs.py (Protocol): Declare exceptions as classes, not strings.
    #
    #class ProtocolError(Exception): pass
    #class ReplyException(Exception): pass
    #class ErrorException(Exception): pass
    #
    # I get:
    #    (pymacs-eval "lisp('\"abc\"').__class__.__name__")
    #    "ReplyException"

    ProtocolError = 'ProtocolError'
    ReplyException = 'ReplyException'
    ErrorException = 'ErrorException'

    def __init__(self):
        self.freed = []

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
            except Protocol.ReplyException, value:
                return value
            except Protocol.ErrorException, message:
                status = 'error'
                argument = message
            except Protocol.ProtocolError, message:
                sys.stderr.write("Protocol error: %s\n" % message)
                sys.exit(1)
            except KeyboardInterrupt:
                raise
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
            if self.freed:
                write('(progn (pymacs-free-lisp')
                for index in self.freed:
                    write(' %d' % index)
                write(') ')
            write('(pymacs-%s ' % status)
            print_lisp(argument, write, quoted=1)
            write(')')
            if self.freed:
                write(')')
                self.freed = []
            self.send(string.join(fragments, ''))

    def receive(self):
        # Receive a Python expression from Emacs, return its text unevaluated.
        text = sys.stdin.read(3)
        if not text or text[0] != '>':
            raise Protocol.ProtocolError, "`>' expected."
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
    raise Protocol.ReplyException, value

def error(message):
    # This function implements the `error' pseudo-function.
    raise Protocol.ErrorException, "Emacs: %s" % message

def pymacs_load_helper(file_without_extension, prefix):
    # This function imports a Python module, then returns a Lisp expression
    # which, when later evaluated, will install trampoline definitions in
    # Emacs for accessing the Python module facilities.  MODULE may be a
    # full path, yet without the `.py' or `.pyc' extension, in which case
    # the directory is temporarily added to the Python search path for
    # the sole duration of that import.  All defined symbols on the Lisp
    # side have have PREFIX prepended, and have Python underlines in Python
    # turned into dashes.  If PREFIX is None, it then defaults to the base
    # name of MODULE with underlines turned to dashes, followed by a dash.
    directory, module_name = os.path.split(file_without_extension)
    module_components = string.split(module_name, '.')
    if prefix is None:
        prefix = string.replace(module_components[-1], '_', '-') + '-'
    try:
        object = sys.modules.get(module_name)
        if object:
            reload(object)
        else:
            try:
                if directory:
                    sys.path.insert(0, directory)
                object = __import__(module_name)
            finally:
                if directory:
                    del sys.path[0]
            # Whenever MODULE_NAME is of the form [PACKAGE.]...MODULE,
            # __import__ returns the outer PACKAGE, not the module.
            for component in module_components[1:]:
                object = getattr(object, component)
    except ImportError:
        return None
    load_hook = object.__dict__.get('pymacs_load_hook')
    if load_hook:
        load_hook()
    interactions = object.__dict__.get('interactions', {})
    if type(interactions) != types.DictType:
        interactions = {}
    arguments = []
    for name, value in object.__dict__.items():
        if callable(value) and value is not lisp:
            arguments.append(allocate_python(value))
            arguments.append(lisp[prefix + string.replace(name, '_', '-')])
            try:
                interaction = value.interaction
            except AttributeError:
                interaction = interactions.get(value)
            if callable(interaction):
                arguments.append(allocate_python(interaction))
            else:
                arguments.append(interaction)
    if arguments:
        return [lisp.progn,
                [lisp.pymacs_defuns, [lisp.quote, arguments]],
                object]
    return [lisp.quote, object]

def doc_string(object):
    if hasattr(object, '__doc__'):
        return object.__doc__

# Garbage collection matters.

# Many Python types do not have direct Lisp equivalents, and may not be
# directly returned to Lisp for this reason.  They are rather allocated in
# a list of handles, below, and a handle index is used for communication
# instead of the Python value.  Whenever such a handle is freed from the
# Lisp side, its index is added of a freed list for later reuse.

python = []
freed_list = []

def allocate_python(value):
    assert type(value) != type(''), (type(value), `value`)
    # Allocate some handle to hold VALUE, return its index.
    if freed_list:
        index = freed_list[-1]
        del freed_list[-1]
        python[index] = value
    else:
        index = len(python)
        python.append(value)
    return index

def free_python(*indices):
    # Return many handles to the pool.
    for index in indices:
        python[index] = None
        freed_list.append(index)

def zombie_python(*indices):
    # Ensure that some handles are _not_ in the pool.
    for index in indices:
        while index >= len(python):
            freed_list.append(len(python))
            python.append(None)
        python[index] = zombie
        freed_list.remove(index)
    # Merely to make `*Pymacs*' a bit more readable.
    freed_list.sort()

def zombie(*arguments):
    error("Object vanished when helper was killed.")

# Emacs services for Python applications.

class Let:

    def __init__(self, **keywords):
        self.stack = []
        apply(self.push, (), keywords)

    def __del__(self):
        while self.stack:
            method = self.stack[-1][0]
            if method == 'variables':
                self.pop()
            elif method == 'excursion':
                self.pop_excursion()
            elif method == 'match_data':
                self.pop_match_data()
            elif method == 'restriction':
                self.pop_restriction()
            elif method == 'selected_window':
                self.pop_selected_window()
            elif method == 'window_excursion':
                self.pop_window_excursion()

    def __nonzero__(self):
        # So stylistic `if let:' executes faster.
        return 1

    def push(self, **keywords):
        pairs = []
        for name, value in keywords.items():
            pairs.append((name, getattr(lisp, name).value()))
            setattr(lisp, name, value)
        self.stack.append(('variables', pairs))
        return self

    def pop(self):
        method, pairs = self.stack[-1]
        assert method == 'variables', self.stack[-1]
        del self.stack[-1]
        for name, value in pairs:
            setattr(lisp, name, value)

    def push_excursion(self):
        self.stack.append(('excursion',
                           (lisp.current_buffer(),
                            lisp.point_marker(), lisp.mark_marker())))
        return self

    def pop_excursion(self):
        method, (buffer, point_marker, mark_marker) = self.stack[-1]
        assert method == 'excursion', self.stack[-1]
        del self.stack[-1]
        lisp.set_buffer(buffer)
        lisp.goto_char(point_marker)
        lisp.set_mark(mark_marker)
        lisp.set_marker(point_marker, None)
        lisp.set_marker(mark_marker, None)

    def push_match_data(self):
        self.stack.append(('match_data', lisp.match_data()))
        return self

    def pop_match_data(self):
        method, match_data = self.stack[-1]
        assert method == 'match_data', self.stack[-1]
        del self.stack[-1]
        lisp.set_match_data(match_data)

    def push_restriction(self):
        self.stack.append(('restriction',
                           (lisp.point_min_marker(), lisp.point_max_marker())))
        return self

    def pop_restriction(self):
        method, (point_min_marker, point_max_marker) = self.stack[-1]
        assert method == 'restriction', self.stack[-1]
        del self.stack[-1]
        lisp.narrow_to_region(point_min_marker, point_max_marker)
        lisp.set_marker(point_min_marker, None)
        lisp.set_marker(point_max_marker, None)

    def push_selected_window(self):
        self.stack.append(('selected_window', lisp.selected_window()))
        return self

    def pop_selected_window(self):
        method, selected_window = self.stack[-1]
        assert method == 'selected_window', self.stack[-1]
        del self.stack[-1]
        lisp.select_window(selected_window)

    def push_window_excursion(self):
        self.stack.append(('window_excursion',
                           lisp.current_window_configuration()))
        return self

    def pop_window_excursion(self):
        method, current_window_configuration = self.stack[-1]
        assert method == 'window_excursion', self.stack[-1]
        del self.stack[-1]
        lisp.set_window_configuration(current_window_configuration)

class Symbol:

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return 'lisp[%s]' % repr(self.text)

    def __str__(self):
        return '\'' + self.text

    def value(self):
        return lisp(self.text)

    def copy(self):
        return lisp('(pymacs-expand %s)' % self.text)

    def set(self, value):
        if value is None:
            lisp('(setq %s nil)' % self.text)
        else:
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

    def __init__(self, index):
        self.index = index

    def __del__(self):
        lisp._protocol.freed.append(self.index)

    def __repr__(self):
        return ('lisp(%s)' % repr(lisp('(prin1-to-string %s)' % self)))

    def __str__(self):
        return '(aref pymacs-lisp %d)' % self.index

    def value(self):
        return self

    def copy(self):
        return lisp('(pymacs-expand %s)' % self)

class Buffer(Lisp):
    pass

    #def write(text):
    #    # So you could do things like
    #    # print >>lisp.current_buffer(), "Hello World"
    #    lisp.insert(text, self)

    #def point(self):
    #    return lisp.point(self)

class List(Lisp):

    def __call__(self, *arguments):
        fragments = []
        write = fragments.append
        write('(%s' % self)
        for argument in arguments:
            write(' ')
            print_lisp(argument, write, quoted=1)
        write(')')
        return lisp(string.join(fragments, ''))

    def __len__(self):
        return lisp('(length %s)' % self)

    def __getitem__(self, key):
        value = lisp('(nth %d %s)' % (key, self))
        if value is None and key >= len(self):
            raise IndexError, key
        return value

    def __setitem__(self, key, value):
        fragments = []
        write = fragments.append
        write('(setcar (nthcdr %d %s) ' % (key, self))
        print_lisp(value, write, quoted=1)
        write(')')
        lisp(string.join(fragments, ''))

class Table(Lisp):

    def __getitem__(self, key):
        fragments = []
        write = fragments.append
        write('(gethash ')
        print_lisp(key, write, quoted=1)
        write(' %s)' % self)
        return lisp(string.join(fragments, ''))

    def __setitem__(self, key, value):
        fragments = []
        write = fragments.append
        write('(puthash ')
        print_lisp(key, write, quoted=1)
        write(' ')
        print_lisp(value, write, quoted=1)
        write(' %s)' % self)
        lisp(string.join(fragments, ''))

class Vector(Lisp):

    def __len__(self):
        return lisp('(length %s)' % self)

    def __getitem__(self, key):
        return lisp('(aref %s %d)' % (self, key))

    def __setitem__(self, key, value):
        fragments = []
        write = fragments.append
        write('(aset %s %d ' % (self, key))
        print_lisp(value, write, quoted=1)
        write(')')
        lisp(string.join(fragments, ''))

class Lisp_Interface:

    def __init__(self):
        self.__dict__['_cache'] = {'nil': None}
        self.__dict__['_protocol'] = Protocol()

    def __call__(self, text):
        self._protocol.send('(progn %s)' % text)
        return self._protocol.loop()

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

lisp = Lisp_Interface()

print_lisp_quoted_specials = {'"': '\\"', '\\': '\\\\', '\b': '\\b',
                              '\f': '\\f', '\n': '\\n', '\t': '\\t'}

def print_lisp(value, write, quoted=0):
    if value is None:
        write('nil')
    elif type(value) == types.IntType:
        write(repr(value))
    elif type(value) == types.FloatType:
        write(repr(value))
    elif type(value) == types.StringType:
        write('"')
        for character in value:
            special = print_lisp_quoted_specials.get(character)
            if special is not None:
                write(special)
            elif 32 <= ord(character) < 127:
                write(character)
            else:
                write('\\%.3o' % ord(character))
        write('"')
    elif type(value) == types.ListType:
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
    elif type(value) == types.TupleType:
        write('[')
        if len(value) > 0:
            print_lisp(value[0], write)
            for sub_value in value[1:]:
                write(' ')
                print_lisp(sub_value, write)
        write(']')
    elif isinstance(value, Lisp):
        write(str(value))
    elif isinstance(value, Symbol):
        if quoted:
            write("'")
        write(value.text)
    elif callable(value):
        write('(pymacs-defun %d)' % allocate_python(value))
    else:
        write('(pymacs-python %d)' % allocate_python(value))

if __name__ == '__main__':
    apply(main, sys.argv[1:])
