#!/usr/bin/env python
# Copyright © 2001, 2002 Progiciels Bourbeau-Pinard inc.
# François Pinard <pinard@iro.umontreal.ca>, 2001.

"""\
Installer tool for Pymacs `pymacs.el'.

Usage: setup [OPTION]

  -H   Display this help, then exit.
  -V   Display package name and version, then exit.

  -i         Interactively check selected options with user.
  -n         Dry run: merely display selected options.
  -g GROUP   Install with write permissions for that user GROUP.
  -e         Load `.emacs' before checking Emacs `load-path'.

  -l LISPDIR   Install `pymacs.el' in LISPDIR.
  -E EMACS     Use that executable for EMACS, if not `emacs'.
"""

import os, string, sys

sys.path.insert(0, '.')
from Pymacs import package, version
del sys.path[0]

AUTOCONF = ()                           # neither a string nor None

class run:
    interactive = 0
    dry = 0
    group = None
    dot_emacs = 0
    lispdir = AUTOCONF
    emacs = 'emacs'

def main(*arguments):
    import getopt
    options, arguments = getopt.getopt(arguments, 'E:HVeg:il:n')
    for option, value in options:
        if option == '-E' and value:
            run.emacs = value
        elif option == '-H':
            sys.stdout.write(__doc__)
            sys.exit(0)
        elif option == '-V':
            sys.stdout.write('%s-%s' % (package, version))
            sys.exit(0)
        elif option == '-e':
            run.dot_emacs = 1
        elif option == '-g' and value:
            run.group = value
        elif option == '-i':
            run.interactive = 1
        elif option == '-l' and value:
            if value in ('none', 'None'):
                run.lispdir = None
            else:
                run.lispdir = [value]
    auto_configure()
    if run.interactive:
        check_with_user()
    check_choices()
    if not run.dry:
        complete_install()

def auto_configure():
    if run.lispdir is AUTOCONF:
        run.lispdir = []
        import tempfile
        script = tempfile.mktemp()
        if sys.platform == 'win32':
            # Win32 names starting with tilde and Emacs are unhappy together.
            path, file = os.path.split(script)
            script = os.path.join(path, 'a' + file)
        try:
            open(script, 'w').write('(message "%S" load-path)')
            load_config = ''
            if run.dot_emacs:
                config = os.path.join(os.environ['HOME'], '.emacs')
                for name in config, config + '.el', config + '.elc':
                    if os.path.isfile(name):
                        # Quote!  Spaces are common in Win32 file names.
                        load_config = ' -l "%s"' % name
                    break
            # Quote!  Spaces are common in Win32 file names.
            text = os.popen('%s -batch%s -l "%s" 2>&1'
                            % (run.emacs, load_config, script)).read()
        finally:
            os.remove(script)
        position = string.find(text, '("')
        if position >= 0:
            text = text[position:]
        if text[-1] == '\n':
            text = text[:-1]
        assert text[0] == '(' and text[-1] == ')', text
        for path in string.split(text[1:-1]):
            assert path[0] == '"' and path[-1] == '"', path
            path = path[1:-1]
            if os.access(path, 7):
                run.lispdir.append(path)

def check_with_user():
    sys.stderr.write("""\
Install tool for %s version %s.
"""
                     % (package, version))
    run.lispdir = user_select('lispdir', run.lispdir, """\
This is where `pymacs.el', the Emacs side code of Pymacs, should go:
somewhere on your Emacs `load-path'.
""")

def user_select(name, values, message):
    write = sys.stderr.write
    readline = sys.stdin.readline
    if values is None:
        write("""\

Enter a value for `%s', or merely type `Enter' if you do not want any.
"""
              % name)
        write(message)
        while 1:
            write('%s? ' % name)
            text = string.strip(readline())
            if not text:
                return None
            if os.access(os.path.expanduser(text), 7):
                return [text]
            write("""\

This directory does not exist, or is not writable.  Please reenter it.
""")
    if len(values) == 1:
        return values
    if values == []:
        write("""\

Pymacs is not likely to install properly, as the installer may not currently
write in any directory for `%s'.  Running as `root' might help you.
Or else, you will most probably have to revise a bit your work setup.
"""
              % name)
        write(message)
        return values
    write("""\

There are many possibilities for `%s', please select one of them by
typing its number followed by `Enter'.  A mere `Enter' selects the first.
"""
          % name)
    write(message)
    write('\n')
    for counter in range(len(values)):
        write('%d. %s\n' % (counter + 1, values[counter]))
    while 1:
        write('[1-%d]? ' % len(values))
        text = string.strip(readline())
        if not text:
            return [values[0]]
        try:
            counter = int(text)
        except ValueError:
            pass
        else:
            if 1 <= counter <= len(values):
                return [values[counter-1]]
        write("""\
This is not a valid choice.  Please retry.
""")

def check_choices():
    write = sys.stderr.write
    error = 0
    if run.lispdir is not None:
        if run.lispdir and os.access(os.path.expanduser(run.lispdir[0]), 7):
            run.lispdir = run.lispdir[0]
        else:
            write("\
Use `-l LISPDIR' to select where `pymacs.el' should go.\n")
            error = 1
    if error:
        write("ERROR: Installation aborted!\n"
              "       Try `%s -i'.\n" % sys.argv[0])
        sys.exit(1)
    write(
        '\n'
        "Directory selection for installing Pymacs:\n"
        "  lispdir   = %(lispdir)s\n"
        '\n'
        % run.__dict__)

def complete_install():
    run.substitute = {'PACKAGE': package, 'VERSION': version}
    if run.lispdir:
        goal = os.path.join(run.lispdir, 'pymacs.el')
        install('pymacs.el', goal, 0644)
        compile_lisp(goal)

def install(source, destination, permissions):
    sys.stderr.write('Installing %s\n' % destination)
    write = open(destination, 'w').write
    produce_at = 0
    #print '*', run.substitute
    for fragment in string.split(open(source).read(), '@'):
        #print '**', produce_at, `fragment`
        if produce_at:
            replacement = run.substitute.get(fragment)
            #print '***', replacement
            if replacement is None:
                write('@')
                write(fragment)
            else:
                write(replacement)
                produce_at = 0
        else:
            write(fragment)
            produce_at = 1
    write = None
    set_attributes(destination, permissions)

def compile_lisp(name):
    sys.stderr.write('Compiling %s\n' % name)
    os.system('%s -batch -f batch-byte-compile %s' % (run.emacs, name))
    set_attributes(name + 'c', 0644)

def set_attributes(name, permissions):
    if run.group:
        os.chown(name, run.group)
        permissions = permissions | 0020
    os.chmod(name, permissions)

if __name__ == '__main__':
    apply(main, sys.argv[1:])
