#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2010 Progiciels Bourbeau-Pinard inc.
# François Pinard <pinard@iro.umontreal.ca>, 2010.

"""\
Poor Python Pre Processor (p4).

Usage: p4 -m [OPTION]... FILE1 FILE2
  or:  p4 [OPTION]... [FILE]...

General options:
  -h   Print this help and do nothing else
  -m   Produce, on standard output, a merged version
  -C   Clean files which would normally have been produced
  -v   Be verbose about written (or deleted) files

Context setting options:
  -c FILE       Evaluate Python FILE for preparing context
  -Dname        Define "name" as True
  -Dname=expr   Define "name" as the value of Python "expr"

Transformation options:
  -o OUTPUT   Collect output files into the OUTPUT directory
  -i INDENT   Indentation step, default value is 4
  -s SUFFIX   Suffix to mark transformable paths, if not '.in'
  -p          Force all files to be interpreted as Python

With -m, a single -Dname option is also required.  FILE1 and FILE2 are
merged and the result written to standard output, augmented as needed
with "if name:", "if not name:" and "else:" directives, such that FILE1
is meant when "name" is False, FILE2 is meant when "name" is True.
Beware that this is all done in a crude and approximative way, some
fixup with a text editor is likely needed afterwards.  Especially check
the surroundings of any line containing "#endif (p4)".

Without -Cm, files go through an elementary pre-processing.  If no FILE
is given, standard input is transformed and written to standard output.
Otherwise, each FILE is either a file or a directory.  Directories are
recursively traversed for the contained file names.  Whatever if a file
is directly or indirectly named, it is retained for transformation only
when it's full path name (starting at FILE and down) has a component for
which there is a '.in' suffix.  The file receiving a transformed file
is derived removing all such '.in' suffixes, and prepending OUTPUT as a
directory if specified.  Output directories are created as needed.

Within each file to transform, each occurrence of @name@ gets replaced
by the string of the context value for "name", when such is defined.
Moreover, a Python source (either when -p, or a file which name ends
with .py or .py.in, or for which the first line starts with "!#" and has
some "ython" string in it) is further handled as described below

A Python source has all its "if EXPR:", "elif EXPR:" and corresponding
"else:" lines checked (each on a single line, and without comments).
If "EXPR" is a valid Python expression for which primitives are either
constants or names introduced through -D options, the "if" or "elif"
line is removed and succeeding lines are either shifted or removed.
Beware that this tool is easily fooled with multi-line strings, as it is
driven only by textual line indentation.  It does not follow whether a
line is part of multi-line string or not.
"""

__metaclass__ = type
import os, re, sys

endif_p4 = '#endif (p4)'

class Main:
    output = None
    context = {}
    merge = False
    indent = 4
    suffix = '.in'
    python = False
    verbose = False
    clean = False

    def main(self, *arguments):
        import getopt
        options, arguments = getopt.getopt(arguments, 'CD:c:hi:mo:ps:v')
        for option, value in options:
            if option == '-C':
                self.clean = True
            elif option == '-D':
                if '=' in value:
                    name, value = value.split('=', 1)
                    value = eval(value, {})
                else:
                    name = value
                    value = True
                if name in self.context and value != self.context[name]:
                    sys.exit("More than one value for %s" % name)
                self.context[name] = value
            elif option == '-c':
                exec(compile(open(value).read(), value, 'exec'), self.context)
            elif option == '-h':
                sys.stdout.write(__doc__)
                return
            elif option == '-i':
                self.indent = int(value)
            elif option == '-m':
                self.merge = True
            elif option == '-o':
                self.output = value
            elif option == '-p':
                self.python = True
            elif option == '-s':
                self.suffix = value
            elif option == '-v':
                self.verbose = True
        if self.merge:
            if len(arguments) != 2 or len(self.context) != 1:
                sys.exit("Try `%s -h' for help" % sys.argv[0])
            self.merge_files(arguments[0], arguments[1], sys.stdout.write)
        elif not arguments:
            if not self.clean:
                self.transform_file(
                        sys.stdin.name, sys.stdin, sys.stdout.write)
        else:
            for argument in arguments:
                if os.path.isdir(argument):
                    self.transform_all_files(argument)
                elif argument.endswith(self.suffix):
                    self.transform_all_files(argument)
                else:
                    sys.stderr.write(
                            "* %s does not end with %s, ignored.\n"
                            % (argument, self.suffix))

    def merge_files(self, file1, file2, write):
        left = list(open(file1))
        right = list(open(file2))
        block_margin = None

        def protect_block(margin, danger):
            if block_margin is None:
                return
            if margin is None:
                return
            if margin < block_margin:
                return
            if margin == block_margin and not danger:
                return
            write(' ' * block_margin + endif_p4 + '\n')

        def check_next(lines, lo, hi):
            for index in range(lo, hi):
                line = lines[index].rstrip()
                short = line.lstrip()
                if short:
                    return (len(line) - len(short),
                            short.startswith('elif ')
                            or short.startswith('else:'))
            return None, False

        def lines_margin(lines, lo, hi):
            margin = None
            for index in range(lo, hi):
                line = lines[index].rstrip()
                short = line.lstrip()
                if short:
                    width = len(line) - len(short)
                    if margin is None:
                        margin = width
                    else:
                        margin = min(margin, width)
            return margin or 0

        def copy_lines(lines, lo, hi, prefix):
            for index in range(lo, hi):
                line = lines[index]
                if line.lstrip(' \t') == '\n':
                    write(line)
                else:
                    write(prefix + line)

        name = list(self.context.keys()).pop()
        import difflib
        matcher = difflib.SequenceMatcher(None, left, right)
        for (tag, low_left, high_left, low_right, high_right
                ) in matcher.get_opcodes():
            if tag == 'equal':
                margin, danger = check_next(left, low_left, high_left)
                protect_block(margin, danger)
                copy_lines(left, low_left, high_left, '')
                block_margin = None
            elif tag == 'delete':
                margin = lines_margin(left, low_left, high_left)
                protect_block(margin, False)
                write(' ' * margin + 'if not ' + name + ':\n')
                copy_lines(left, low_left, high_left, ' ' * self.indent)
                block_margin = margin
            elif tag == 'insert':
                margin = lines_margin(right, low_right, high_right)
                protect_block(margin, False)
                write(' ' * margin + 'if ' + name + ':\n')
                copy_lines(right, low_right, high_right, ' ' * self.indent)
                block_margin = margin
            elif tag == 'replace':
                margin = min(lines_margin(left, low_left, high_left),
                             lines_margin(right, low_right, high_right))
                protect_block(margin, False)
                write(' ' * margin + 'if ' + name + ':\n')
                copy_lines(right, low_right, high_right, ' ' * self.indent)
                write(' ' * margin + 'else:\n')
                copy_lines(left, low_left, high_left, ' ' * self.indent)
                block_margin = margin
            else:
                assert False, tag

    def transform_all_files(self, input):

        def ensure_directory(name):
            base = os.path.dirname(name)
            if base and not os.path.isdir(base):
                ensure_directory(base)
                if self.verbose:
                    sys.stderr.write("creating %s\n" % base)
                os.mkdir(base)

        if self.output:
            output = os.path.join(self.output, input)
        else:
            output = input
        for input, output in self.each_pair(input, output):
            if self.clean:
                if os.path.exists(output):
                    if self.verbose:
                        sys.stderr.write("deleting %s\n" % output)
                    os.remove(output)
            else:
                ensure_directory(output)
                if self.verbose:
                    sys.stderr.write("writing %s\n" % output)
                self.transform_file(
                        input, open(input), open(output, 'w').write)

    def each_pair(self, input, output):
        stack = []
        output = output.replace(self.suffix + '/', '/')
        if output.endswith(self.suffix):
            output = output[:-len(self.suffix)]
        stack.append((input, output))
        while stack:
            input_path, output_path = stack.pop()
            if os.path.isdir(input_path):
                for base in os.listdir(input_path):
                    input = os.path.join(input_path, base)
                    if base.endswith(self.suffix):
                        output = os.path.join(output_path,
                                              base[:-len(self.suffix)])
                    else:
                        output = os.path.join(output_path, base)
                    stack.append((input, output))
            elif ((self.suffix + '/') in input_path
                    or input_path.endswith(self.suffix)):
                yield input_path, output_path

    def transform_file(self, name, lines, write):
        # MARGIN is the number of spaces preceding the previous "if" line.
        # A virtual "if True:" is assumed above and left of the whole module.
        margin = -1

        # STATE is True when copying the block of code following an "if"
        # with a True expression, or when copying the block of code following
        # an "else:" after an "if" with a False expression.  STATE is False
        # when skipping over the block of code following an "if" with a
        # False expression.  STATE is None when skipping over all remaining
        # branches of an "if" block, or when skipping a whole "if" altogether
        # (when an "if" is nested within a block of code already skipped).
        state = True

        # STACK saves the previous (MARGIN, STATE) whenever a nested "if"
        # is met, and restores it when the actual margin goes left enough.
        # A nested "if" is ignored unless its expression can be evaluated.
        # Whenever STATE is True, the length of STACK also happens to be
        # the number of needed de-indents.
        stack = []

        def expression_value(match):
            try:
                value = eval(match.group(1),
                             {'__builtins__': {}},
                             self.context)
            except:
                return None
            else:
                return bool(value)

        python = (self.python
                or name.endswith('.py') or name.endswith('.py' + self.suffix))
        for counter, line in enumerate(self.each_substituded_line(lines)):
            if counter == 0 and line.startswith('#!') and 'ython' in line:
                python = True
            if not python:
                write(line)
                continue
            short = line.lstrip()
            if not short:
                if state:
                    write(line)
                continue
            width = len(line) - len(short)
            while width < margin:
                margin, state = stack.pop()
            if width == margin:
                match = re.match('else: *$', short)
                if match:
                    if state is False:
                        state = True
                    else:
                        state = None
                    continue
                match = re.match('elif (.*): *$', short)
                if match:
                    if state is False:
                        value = expression_value(match)
                        if value is not None:
                            state = value
                            continue
                        line = ' ' * width + 'if ' + match.group(1) + ':\n'
                        margin, state = stack.pop()
                    else:
                        state = None
                        continue
                else:
                    margin, state = stack.pop()
            match = re.match('if (.*): *$', short)
            if match:
                value = expression_value(match)
                if value is not None:
                    stack.append((margin, state))
                    margin = width
                    if state:
                        state = value
                    else:
                        state = None
                    continue
            if state and not short.startswith(endif_p4):
                write(line[len(stack) * self.indent:])

    def each_substituded_line(self, lines):
        if self.context:
            pattern = re.compile(
                    '@('
                    + '|'.join([re.escape(key) for key in self.context])
                    + ')@')
            for line in lines:
                yield pattern.sub(self.substitute, line)
        else:
            for line in lines:
                yield line

    def substitute(self, match):
        return str(self.context[match.group(1)])

run = Main()
main = run.main

if __name__ == '__main__':
    main(*sys.argv[1:])
