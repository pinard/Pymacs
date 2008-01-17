#!/usr/bin/env python
# Copyright © 1991-1998, 2000, 2002 Progiciels Bourbeau-Pinard inc.
# François Pinard <pinard@iro.umontreal.ca>, April 1991.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

"""\
Handling of comment boxes in various styles.

Introduction
------------

For comments held within boxes, it is painful to fill paragraphs, while
stretching or shrinking the surrounding box "by hand", as needed.  This piece
of Python code eases my life on this.  It may be used interactively from
within Emacs through the Pymacs interface, or in batch as a script which
filters a single region to be reformatted.  I find only fair, while giving
all sources for a package using such boxed comments, to also give the
means I use for nicely modifying comments.  So here they are!

Box styles
----------

Each supported box style has a number associated with it.  This number is
arbitrary, yet by _convention_, it holds three non-zero digits such the the
hundreds digit roughly represents the programming language, the tens digit
roughly represents a box quality (or weight) and the units digit roughly
a box type (or figure).  An unboxed comment is merely one of box styles.
Language, quality and types are collectively referred to as style attributes.

When rebuilding a boxed comment, attributes are selected independently
of each other.  They may be specified by the digits of the value given
as Emacs commands argument prefix, or as the single argument to this
script when called from the shell.  If there is no such prefix, or if the
corresponding digit is zero, the attribute is taken from the value of the
default style instead.  If the corresponding digit of the default style
is also zero, than the attribute is recognised and taken from the actual
comment box, as it existed before prior to the command.  The value 1, which
is the simplest attribute, is ultimately taken if the parsing fails.

A programming language is associated with comment delimiters.  Values are
100 for none or unknown, 200 for `/*' and `*/' as in plain C, 300 for `//'
as in C++, 400 for `#' as in most scripting languages, 500 for `;' as in
LISP or assembler and 600 for `%' as in TeX or PostScript.

Box quality differs according to language. For unknown languages (100) or
for the C language (200), values are 10 for simple, 20 for rounded, and
30 or 40 for starred.  Simple quality boxes (10) use comment delimiters
to left and right of each comment line, and also for the top or bottom
line when applicable. Rounded quality boxes (20) try to suggest rounded
corners in boxes.  Starred quality boxes (40) mostly use a left margin of
asterisks or X'es, and use them also in box surroundings.  For all others
languages, box quality indicates the thickness in characters of the left
and right sides of the box: values are 10, 20, 30 or 40 for 1, 2, 3 or 4
characters wide.  With C++, quality 10 is not useful, it is not allowed.

Box type values are 1 for fully opened boxes for which boxing is done
only for the left and right but not for top or bottom, 2 for half
single lined boxes for which boxing is done on all sides except top,
3 for fully single lined boxes for which boxing is done on all sides,
4 for half double lined boxes which is like type 2 but more bold,
or 5 for fully double lined boxes which is like type 3 but more bold.

The special style 221 is for C comments between a single opening `/*'
and a single closing `*/'.  The special style 111 deletes a box.

Batch usage
-----------

When this script is called as a program, it accepts a single argument,
which is the wanted box style expressed as a decimal number.  The contents
of stdin is then transformed according that style and sent to stdout.

Usage is `rebox [OPTION]... [FILE]'.  By default, FILE is reformatted to
standard output by refilling the comment up to column 79, while preserving
existing boxed comment style.  If FILE is not given, standard input is read.
Options may be:

  -n         Do not refill the comment inside its box, and ignore -w.
  -s STYLE   Replace box style according to STYLE, as explained above.
  -t         Replace initial sequence of spaces by TABs on each line.
  -w WIDTH   Try to avoid going over WIDTH columns per line.

Emacs usage
-----------

For most Emacs language editing modes, refilling does not make sense
outside comments, one may redefine the `M-q' command and link it to this
file.  For example, I use this in my `.emacs' file:

     (add-hook 'c-mode-hook 'fp-c-mode-routine)
     (defun fp-c-mode-routine ()
       (local-set-key "\M-q" 'rebox-comment))
     (autoload 'rebox-comment "rebox" nil t)
     (autoload 'rebox-region "rebox" nil t)

with a "rebox.el" file having this single line:

     (pymacs-load "Pymacs.rebox")

Install Pymacs from `http://www.iro.umontreal.ca/~pinard/pymacs.tar.gz'.

The Emacs function `rebox-comment' automatically discovers the extent of the
boxed comments near the cursor, possibly refills the text, then adjusts the
comment box style.  When this command is executed, the cursor should be
within a comment, or else it should be between two comments, in which case
the command applies to the next comment.  The function `rebox-region' does
the same, except that it takes the current region as a boxed comment.  Both
commands obey numeric prefixes to add or remove a box, force a particular
box style, or to prevent refilling of text.  Without such prefixes, the
commands may deduce the current comment box style from the comment itself
so the style is preserved.

The default style initial value is nil or 0.  It may be preset to another
value through calling `rebox-set-default-style' from Emacs LISP, or changed
to anything else though using a negative value for a prefix, in which case
the default style is set to the absolute value of the prefix.

A `C-u' prefix avoids refilling the text, but forces using the default box
style.  `C-u -' lets the user interact to select one attribute at a time.

History
-------

I first observed rounded corners, as in style 223 boxes, in code from
Warren Tucker, a previous maintainer of the `shar' package, circa 1980.

Besides for very special files, I was carefully avoiding to use boxes
for real work, as I found them much too hard to maintain.  My friend Paul
Provost was working at Taarna, a computer graphics place, which had boxes
as part of their coding standards.  He asked that we try something to
get out of his misery, and this how `rebox.el' was originally written.
I did not plan to use it for myself, but Paul was so enthusiastic that I
timidly started to use boxes in my things, very little at first, but more
and more as time passed, yet not fully sure it was a good move.  Later, many
friends spontaneously started to use this tool for real, some being very
serious workers.  This convinced me that boxes are acceptable, after all.

I do not use boxes much with Python code.  It is so legible that one may
loose the habit of boxing comments, or using much vertical space.  I even
avoid white lines within functions.  Comments appear prominent enough when
using highlighting editors like Emacs or nice printer tools like `enscript'.

After Emacs could be extended with Python, in 2001, I translated `rebox.el'
into `rebox.py', and added the facility to use it as a batch script.
"""

## Note: a double hash comment introduces a group of functions or methods.

import re, string, sys

class Rebox:

    ## Code which depends on template numbering.  Method `ask_for_style'
    ## sits within `Emacs_Rebox'.

    def __init__(self):
        # Language number and comment character, for generic languages.
        self.language_characters = (
            (3, '/'), (4, '#'), (5, ';'), (6, '%'))
        # Regexp to match the comment start, given a LANGUAGE value as index.
        self.matcher = []
        for pattern in (r' *(/\*|//+|#+|;+|%+)',
                        r'',            # 1
                        r' */\*',       # 2
                        r' *//+',       # 3
                        r' *#+',        # 4
                        r' *;+',        # 5
                        r' *%+'):       # 6
            self.matcher.append(re.compile(pattern).match)
        # Complete data initialisation.
        self.declare_all_templates()

    def declare_all_templates(self):
        # Information about registered templates.
        self.style_data = {}
        declare = self.declare_template
        # Generic programming language templates.
        # . Adding 300 replaces `?' by `/', for C++ style comments.
        # . Adding 400 replaces `?' by `#', for scripting languages.
        # . Adding 500 replaces `?' by ';', for LISP and assembler.
        # . Adding 600 replaces `?' by `%', for TeX and PostScript.
        declare(11, 115, ('? box',))
        declare(12, 215, ('? box ?',
                          '? --- ?'))
        declare(13, 315, ('? --- ?',
                          '? box ?',
                          '? --- ?'))
        declare(14, 415, ('? box ?',
                          '???????'))
        declare(15, 515, ('???????',
                          '? box ?',
                          '???????'))
        declare(21, 125, ('?? box',))
        declare(22, 225, ('?? box ??',
                          '?? --- ??'))
        declare(23, 325, ('?? --- ??',
                          '?? box ??',
                          '?? --- ??'))
        declare(24, 425, ('?? box ??',
                          '?????????'))
        declare(25, 525, ('?????????',
                          '?? box ??',
                          '?????????'))
        declare(31, 135, ('??? box',))
        declare(32, 235, ('??? box ???',
                          '??? --- ???'))
        declare(33, 335, ('??? --- ???',
                          '??? box ???',
                          '??? --- ???'))
        declare(34, 435, ('??? box ???',
                          '???????????'))
        declare(35, 535, ('???????????',
                          '??? box ???',
                          '???????????'))
        declare(41, 145, ('???? box',))
        declare(42, 245, ('???? box ????',
                          '???? --- ????'))
        declare(43, 345, ('???? --- ????',
                          '???? box ????',
                          '???? --- ????'))
        declare(44, 445, ('???? box ????',
                          '?????????????'))
        declare(45, 545, ('?????????????',
                          '???? box ????',
                          '?????????????'))
        # Textual (non programming) templates.
        declare(111, 113, ('box',))
        declare(112, 213, ('| box |',
                           '+-----+'))
        declare(113, 313, ('+-----+',
                           '| box |',
                           '+-----+'))
        declare(114, 413, ('| box |',
                           '*=====*'))
        declare(115, 513, ('*=====*',
                           '| box |',
                           '*=====*'))
        declare(121, 123, ('| box |',))
        declare(122, 223, ('| box |',
                           '`-----\''))
        declare(123, 323, ('.-----.',
                           '| box |',
                           '`-----\''))
        declare(124, 423, ('| box |',
                           '\\=====/'))
        declare(125, 523, ('/=====\\',
                           '| box |',
                           '\\=====/'))
        declare(141, 143, ('| box ',))
        declare(142, 243, ('* box *',
                           '*******'))
        declare(143, 343, ('*******',
                           '* box *',
                           '*******'))
        declare(144, 443, ('X box X',
                           'XXXXXXX'))
        declare(145, 543, ('XXXXXXX',
                           'X box X',
                           'XXXXXXX'))
        # C language templates.
        declare(211, 118, ('/* box */',))
        declare(212, 218, ('/* box */',
                           '/* --- */'))
        declare(213, 318, ('/* --- */',
                           '/* box */',
                           '/* --- */'))
        declare(214, 418, ('/* box */',
                           '/* === */'))
        declare(215, 518, ('/* === */',
                           '/* box */',
                           '/* === */'))
        declare(221, 128, ('/* ',
                           '   box',
                           '*/'))
        declare(222, 228, ('/*    .',
                           '| box |',
                           '`----*/'))
        declare(223, 328, ('/*----.',
                           '| box |',
                           '`----*/'))
        declare(224, 428, ('/*    \\',
                           '| box |',
                           '\\====*/'))
        declare(225, 528, ('/*====\\',
                           '| box |',
                           '\\====*/'))
        declare(231, 138, ('/*    ',
                           ' | box',
                           ' */   '))
        declare(232, 238, ('/*       ',
                           ' | box | ',
                           ' *-----*/'))
        declare(233, 338, ('/*-----* ',
                           ' | box | ',
                           ' *-----*/'))
        declare(234, 438, ('/* box */',
                           '/*-----*/'))
        declare(235, 538, ('/*-----*/',
                           '/* box */',
                           '/*-----*/'))
        declare(241, 148, ('/*    ',
                           ' * box',
                           ' */   '))
        declare(242, 248, ('/*     * ',
                           ' * box * ',
                           ' *******/'))
        declare(243, 348, ('/******* ',
                           ' * box * ',
                           ' *******/'))
        declare(244, 448, ('/* box */',
                           '/*******/'))
        declare(245, 548, ('/*******/',
                           '/* box */',
                           '/*******/'))
        declare(251, 158, ('/* ',
                           ' * box',
                           ' */   '))

    def declare_template(self, style, weight, lines):
        """\
Digest and register a single template.  The template is numbered STYLE,
has a parsing WEIGHT, and is described by one to three LINES.

If STYLE is below 100, it is generic for a few programming languages and
within lines, `?' is meant to represent the language comment character.
STYLE should be used only once through all `declare_template' calls.

One of the lines should contain the substring `box' to represent the comment
to be boxed, and if three lines are given, `box' should appear in the middle
one.  Lines containing only spaces are implied as necessary before and after
the the `box' line, so we have three lines.

Normally, all three template lines should be of the same length.  If the first
line is shorter, it represents a start comment string to be bundled within the
first line of the comment text.  If the third line is shorter, it represents
an end comment string to be bundled at the end of the comment text, and
refilled with it.
"""
        if style < 100:
            for language, character in self.language_characters:
                new_style = 100*language + style
                if 310 < new_style <= 319:
                    # Disallow quality 10 with C++.
                    continue
                new_lines = []
                for line in lines:
                    new_lines.append(string.replace(line, '?', character))
                self.declare_template(new_style, weight, new_lines)
            return
        if self.style_data.has_key(style):
            self.error("Style %d defined more than once" % style)
        # Make it exactly three lines, with `box' in the middle.
        start = string.find(lines[0], 'box')
        if start >= 0:
            line1 = None
            line2 = lines[0]
            if len(lines) > 1:
                line3 = lines[1]
            else:
                line3 = None
        else:
            start = string.find(lines[1], 'box')
            if start >= 0:
                line1 = lines[0]
                line2 = lines[1]
                if len(lines) > 2:
                    line3 = lines[2]
                else:
                    line3 = None
            else:
                self.error("Erroneous template for %d style" % style)
        end = start + len('box')
        # Define a few booleans.
        merge_nw = line1 is not None and len(line1) < len(line2)
        merge_se = line3 is not None and len(line3) < len(line2)
        # Define strings at various cardinal directions.
        if line1 is None:
            nw = nn = ne = None
        elif merge_nw:
            nw = line1
            nn = ne = None
        else:
            if start > 0:
                nw = line1[:start]
            else:
                nw = None
            if line1[start] != ' ':
                nn = line1[start]
            else:
                nn = None
            if end < len(line1):
                ne = string.rstrip(line1[end:])
            else:
                ne = None
        if start > 0:
            ww = line2[:start]
        else:
            ww = None
        if end < len(line2):
            ee = line2[end:]
        else:
            ee = None
        if line3 is None:
            sw = ss = se = None
        elif merge_se:
            sw = ss = None
            se = string.rstrip(line3)
        else:
            if start > 0:
                sw = line3[:start]
            else:
                sw = None
            if line3[start] !=  ' ':
                ss = line3[start]
            else:
                ss = None
            if end < len(line3):
                se = string.rstrip(line3[end:])
            else:
                se = None
        build_data = merge_nw, merge_se, nw, nn, ne, ww, ee, sw, ss, se
        # Define parsing regexps.
        if merge_nw:
            regexp1 = re.compile(' *' + regexp_quote(nw) + '.*$')
        elif nw and not nn and not ne:
            regexp1 = re.compile(' *' + regexp_quote(nw) + '$')
        elif nw or nn or ne:
            regexp1 = re.compile(
                ' *' + regexp_quote(nw) + regexp_ruler(nn)
                + regexp_quote(ne) + '$')
        else:
            regexp1 = None
        if ww or ee:
            regexp2 = re.compile(
                ' *' + regexp_quote(ww) + '.*' + regexp_quote(ee) + '$')
        else:
            regexp2 = None
        if merge_se:
            regexp3 = re.compile('.*' + regexp_quote(se) + '$')
        elif sw and not ss and not se:
            regexp3 = re.compile(' *' + regexp_quote(sw) + '$')
        elif sw or ss or se:
            regexp3 = re.compile(
                ' *' + regexp_quote(sw) + regexp_ruler(ss)
                + regexp_quote(se) + '$')
        else:
            regexp3 = None
        guess_data = weight, regexp1, regexp2, regexp3
        # Save results.
        self.style_data[style] = guess_data, build_data

    ## Main reformatting control.

    def engine(self, text, style=None, width=79,
               refill=1, tabify=0, position=None):
        """\
Add, delete or adjust a comment box in TEXT, according to FLAG, which
values are explained at beginning of this file.  POSITION is None, or a
character position within TEXT.  Returns the reformatted text, and either
None or an approximation of the adjusted value of POSITION in the new text.
If TABIFY is set, the beginning of produced lines will get tab-ified.
"""
        last_line_complete = text and text[-1] == '\n'
        if last_line_complete:
            text = text[:-1]
        lines = string.split(string.expandtabs(text), '\n')
        # Decide about refilling and the box style to use.
        next_style = 111
        previous_style = self.guess_style(lines)
        if previous_style is not None:
            next_style = merge_styles(next_style, previous_style)
        if style is not None:
            next_style = merge_styles(next_style, style)
        if not self.style_data.has_key(next_style):
            self.error("Style %d is not known" % next_style)
        self.message("Style: %d -> %d" % (previous_style or 0, next_style))
        # Remove all previous comment marks, and left margin.
        if position is not None:
            marker = Marker(self, previous_style, next_style)
            marker.save_position(text, position)
        lines, margin = self.unbuild(lines, previous_style)
        # Ensure only one white line between paragraphs.
        counter = 1
        while counter < len(lines) - 1:
            if lines[counter] == '' and lines[counter-1] == '':
                del lines[counter]
            else:
                counter = counter + 1
        # Rebuild the boxed comment.
        lines = self.build(lines, next_style, width, refill, margin)
        # Retabify to the left only.
        if tabify:
            for counter in range(len(lines)):
                tabs = len(re.match(' *', lines[counter]).group()) / 8
                lines[counter] = '\t' * tabs + lines[counter][8*tabs:]
        # Restore the point position.
        text = string.join(lines, '\n')
        if last_line_complete:
            text = text + '\n'
        if position is not None:
            position = marker.get_position(text)
        return text, position

    ## Parsing boxes to discover box style attributes.

    def guess_language(self, line):
        """\
Guess the language in use for LINE.
"""
        for language in range(len(self.matcher) - 1, 1, -1):
            if self.matcher[language](line):
                return language
        return 1

    def guess_style(self, lines):
        """\
Guess the current box style from studying TEXT.
"""
        best_style = None
        best_weight = None
        # Let's try all styles in turn.  A style has to match exactly to be
        # eligible.  More heavy is a style, more prone it is to be retained.
        for style, (guess_data, build_data) in self.style_data.items():
            weight, regexp1, regexp2, regexp3 = guess_data
            if best_weight is not None and weight <= best_weight:
                continue
            start = 0
            end = len(lines)
            if regexp1 is not None:
                if start == end or not regexp1.match(lines[start]):
                    continue
                start = start + 1
            if regexp3 is not None:
                if end == 0 or not regexp3.match(lines[end-1]):
                    continue
                end = end - 1
            if regexp2 is not None:
                failed = 0
                for line in lines[start:end]:
                    if not regexp2.match(line):
                        failed = 1
                        break
                if failed:
                    continue
            best_style = style
            best_weight = weight
        return best_style

    ## Reconstruction of boxes.

    def unbuild(self, lines, style):
        """\
Remove all comment marks, using STYLE to hint at what these are.  Returns
the cleaned up set of lines, and the size of the left margin.
"""
        margin = left_margin_size(lines)
        # Remove box style marks.
        guess_data, build_data = self.style_data[style]
        weight, regexp1, regexp2, regexp3 = guess_data
        start = 0
        end = len(lines)
        if regexp1 is not None:
            lines[start] = self.unbuild_clean(lines[start], regexp1)
            start = start + 1
        if regexp3 is not None:
            lines[end-1] = self.unbuild_clean(lines[end-1], regexp3)
            end = end - 1
        if regexp2 is not None:
            for counter in range(start, end):
                lines[counter] = self.unbuild_clean(lines[counter], regexp2)
        # Remove the left side of the box after it turned into spaces.
        delta = left_margin_size(lines) - margin
        for counter in range(len(lines)):
            lines[counter] = lines[counter][delta:]
        # Remove leading and trailing white lines.
        start = 0
        end = len(lines)
        while start < end and lines[start] == '':
            start = start + 1
        while end > start and lines[end-1] == '':
            end = end - 1
        return lines[start:end], margin

    def unbuild_clean(self, line, regexp):
        """\
Return LINE with all parenthetical groups in REGEXP erased and replaced by an
equivalent number of spaces, except for trailing spaces, which get removed.
"""
        match = re.match(regexp, line)
        groups = match.groups()
        for counter in range(len(groups)):
            if groups[counter] is not None:
                start, end = match.span(1 + counter)
                line = line[:start] + ' ' * (end - start) + line[end:]
        return string.rstrip(line)

    def build(self, lines, style, width, refill, margin):
        """\
Put LINES back into a boxed comment according to box STYLE, after having
refilled them if REFILL.  The box should start at column MARGIN, and
the total size of each line should ideally not go over WIDTH.
"""
        guess_data, build_data = self.style_data[style]
        merge_nw, merge_se, nw, nn, ne, ww, ee, sw, ss, se = build_data
        # Merge a short end delimiter now, so it gets refilled with text.
        if merge_se:
            if lines:
                lines[-1] = lines[-1] + '  ' + se
            else:
                lines = [se]
            se = None
        # Reduce WIDTH according to left and right inserts, then refill.
        if ww:
            width = width - len(ww)
        if ee:
            width = width - len(ee)
        if refill:
            lines = refill_lines(lines, width)
        # Reduce WIDTH further according to the current right margin.
        maximum = 0
        for line in lines:
            if line:
                if line[-1] in '.!?':
                    length = len(line) + 1
                else:
                    length = len(line)
                if length > maximum:
                    maximum = length
        width = maximum
        # Construct the top line.
        if merge_nw:
            lines[0] = ' ' * margin + nw + lines[0][margin:]
            start = 1
        elif nw or nn or ne:
            if nn:
                line = nn * width
            else:
                line = ' ' * width
            if nw:
                line = nw + line
            if ne:
                line = line + ne
            lines.insert(0, string.rstrip(' ' * margin + line))
            start = 1
        else:
            start = 0
        # Construct all middle lines.
        for counter in range(start, len(lines)):
            line = lines[counter][margin:]
            line = line + ' ' * (width - len(line))
            if ww:
                line = ww + line
            if ee:
                line = line + ee
            lines[counter] = string.rstrip(' ' * margin + line)
        # Construct the bottom line.
        if sw or ss or se:
            if ss:
                line = ss * width
            else:
                line = ' ' * width
            if sw:
                line = sw + line
            if se:
                line = line + se
            lines.append(string.rstrip(' ' * margin + line))
        return lines

## Miscellaneous services to Rebox.

def left_margin_size(lines):
    """\
Return the width of the left margin for all LINES.  Ignore white lines.
"""
    margin = None
    for line in lines:
        counter = len(re.match(' *', line).group())
        if counter != len(line):
            if margin is None or counter < margin:
                margin = counter
    if margin is None:
        margin = 0
    return margin

def merge_styles(default, style):
    """\
Return style attributes as per DEFAULT, in which attributes have been
overridden by non-zero corresponding style attributes from STYLE.
"""
    result = [default / 100, default / 10 % 10, default % 10]
    merge = style / 100, style / 10 % 10, style % 10
    for counter in range(3):
        if merge[counter]:
            result[counter] = merge[counter]
    return 100*result[0] + 10*result[1] + result[2]

def refill_lines(lines, width):
    """\
Refill LINES, trying to not produce lines having more than WIDTH columns.
"""
    # Try using GNU `fmt'.
    import tempfile, os
    name = tempfile.mktemp()
    open(name, 'w').write(string.join(lines, '\n') + '\n')
    process = os.popen('fmt -cuw %d %s' % (width, name))
    text = process.read()
    os.remove(name)
    if process.close() is None:
        return map(string.expandtabs, string.split(text, '\n')[:-1])
    # If `fmt' failed, use a simple refilling, far from ideal.  (untested)
    lines.append(None)
    new_lines = []
    new_line = ''
    start = 0
    for end in range(len(lines)):
        if not lines[end]:
            margin = left_margin_size(lines[start:end])
            for line in lines[start:end]:
                counter = len(re.match(' *', line).group())
                if counter > margin:
                    if new_line:
                        new_lines.append(' ' * margin + new_line)
                        new_line = ''
                    indent = counter - margin
                else:
                    indent = 0
                for word in string.split(line):
                    if new_line:
                        if len(new_line) + 1 + len(word) > width:
                            new_lines.append(' ' * margin + new_line)
                            new_line = word
                        else:
                            new_line = new_line + ' ' + word
                    else:
                        new_line = ' ' * indent + word
                        indent = 0
            if new_line:
                new_lines.append(' ' * margin + new_line)
                new_line = ''
            if lines[end] is not None:
                new_lines.append('')
                start = end + 1
    return new_lines

def regexp_quote(text):
    """\
Return a regexp matching TEXT without its surrounding space, maybe
followed by spaces.  If STRING is nil, return the empty regexp.
Unless spaces, the text is nested within a regexp parenthetical group.
"""
    if text is None:
        return ''
    if text == ' ' * len(text):
        return ' *'
    return '(' + re.escape(string.strip(text)) + ') *'

def regexp_ruler(character):
    """\
Return a regexp matching two or more repetitions of CHARACTER, maybe
followed by spaces.  Is CHARACTER is nil, return the empty regexp.
Unless spaces, the ruler is nested within a regexp parenthetical group.
"""
    if character is None:
        return ''
    if character == ' ':
        return '  +'
    return '(' + re.escape(character + character) + '+) *'

class Batch_Rebox(Rebox):

    def message(self, message):
        if message[-1] != '\n':
            message = message + '\n'
        sys.stderr.write(message)

    def error(self, message):
        self.message(message)
        sys.exit(1)

class Emacs_Rebox(Rebox):

    def __init__(self):
        Rebox.__init__(self)
        self.default_style = None

    def set_default_style(self, style):
        """\
Set the default style to STYLE.
"""
        self.default_style = style

    def region(self, flag):
        """\
Rebox the current region.
"""
        if flag == lisp['-']:
            flag = self.ask_for_style()
        if self.check_flag(flag):
            checkpoint = lisp.buffer_undo_list
            start, end = lisp.point(), lisp.mark(lisp.t)
            self.process_emacs_region(start, end, flag)
            self.clean_undo_after(checkpoint)
    region.interaction = 'P'

    def comment(self, flag):
        """\
Rebox the surrounding comment.
"""
        if flag == lisp['-']:
            flag = self.ask_for_style()
        if self.check_flag(flag):
            checkpoint = lisp.buffer_undo_list
            start, end = self.find_comment()
            self.process_emacs_region(start, end, flag)
            self.clean_undo_after(checkpoint)
    comment.interaction = 'P'

    def ask_for_style(self):
        """\
Request the style interactively, using the minibuffer.
"""
        language = quality = type = None
        while language is None:
            lisp.message("\
Box language is 100-none, 200-/*, 300-//, 400-#, 500-;, 600-%%")
            key = lisp.read_char()
            if key >= ord('0') and key <= ord('6'):
                language = key - ord('0')
        while quality is None:
            lisp.message("\
Box quality/width is 10-simple/1, 20-rounded/2, 30-starred/3 or 40-starred/4")
            key = lisp.read_char()
            if key >= ord('0') and key <= ord('4'):
                quality = key - ord('0')
        while type is None:
            lisp.message("\
Box type is 1-opened, 2-half-single, 3-single, 4-half-double or 5-double")
            key = lisp.read_char()
            if key >= ord('0') and key <= ord('5'):
                type = key - ord('0')
        return 100*language + 10*quality + type

    def check_flag(self, flag):
        """\
If FLAG is zero or negative, change default box style and return nil.
"""
        if type(flag) is not type(0):
            return 1
        if flag > 0:
            return 1
        self.default_style = -flag
        self.message("Default style: %d" % -flag)
        return 0

    def find_comment(self):
        """\
Find and return the limits of the block of comments following or enclosing
the cursor, or return an error if the cursor is not within such a block
of comments.  Extend it as far as possible in both directions.
"""
        let = pymacs.Let()
        let.push_excursion()
        # Find the start of the current or immediately following comment.
        lisp.beginning_of_line()
        lisp.skip_chars_forward(' \t\n')
        lisp.beginning_of_line()
        if not self.matcher[0](self.remainder_of_line()):
            temp = lisp.point()
            if not lisp.re_search_forward('\\*/', None, lisp.t):
                self.error("outside any comment block")
            lisp.re_search_backward('/\\*')
            if lisp.point() > temp:
                self.error("outside any comment block")
            temp = lisp.point()
            lisp.beginning_of_line()
            lisp.skip_chars_forward(' \t')
            if lisp.point() != temp:
                self.error("text before start of comment")
            lisp.beginning_of_line()
        start = lisp.point()
        language = self.guess_language(self.remainder_of_line())
        # Find the end of this comment.
        if language == 2:
            lisp.search_forward('*/')
            if not lisp.looking_at('[ \t]*$'):
                self.error("text after end of comment")
        lisp.end_of_line()
        if lisp.eobp():
            lisp.insert('\n')
        else:
            lisp.forward_char(1)
        end = lisp.point()
        # Try to extend the comment block backwards.
        lisp.goto_char(start)
        while not lisp.bobp():
            if language == 2:
                lisp.skip_chars_backward(' \t\n')
                if not lisp.looking_at('[ \t]*\n[ \t]*/\\*'):
                    break
                if lisp.point() < 2:
                    break
                lisp.backward-char(2)
                if not lisp.looking_at('\\*/'):
                    break
                lisp.re_search_backward('/\\*')
                temp = lisp.point()
                lisp.beginning_of_line()
                lisp.skip_chars_forward(' \t')
                if lisp.point() != temp:
                    break
                lisp.beginning_of_line()
            else:
                lisp.previous_line(1)
                if not self.matcher[language](self.remainder_of_line()):
                    break
            start = lisp.point()
        # Try to extend the comment block forward.
        lisp.goto_char(end)
        while self.matcher[language](self.remainder_of_line()):
            if language == 2:
                lisp.re_search_forward('[ \t]*/\\*')
                lisp.re_search_forward('\\*/')
                if lisp.looking_at('[ \t]*$'):
                    lisp.beginning_of_line()
                    lisp.forward_line(1)
                    end = lisp.point()
            else:
                lisp.forward_line(1)
                end = lisp.point()
        return start, end

    def remainder_of_line(self):
        """\
Return all characters between point and end of line in Emacs buffer.
"""
        return lisp('''\
(buffer-substring (point) (save-excursion (skip-chars-forward "^\n") (point)))
''')

    def process_emacs_region(self, start, end, flag):
        if flag is None:
            style = self.default_style
            refill = 1
        elif type(flag) == type([]):
            style = self.default_style
            refill = 0
        elif type(flag) == type(0):
            if self.default_style is None:
                style = flag
            else:
                style = merge_styles(self.default_style, flag)
            refill = 1
        else:
            self.error("Unexpected flag value %s" % flag)
        text = lisp.buffer_substring(start, end)
        width = lisp.fill_column.value()
        tabify = lisp.indent_tabs_mode.value() is not None
        point = lisp.point()
        if start <= point < end:
            position = point - start
        else:
            position = None
        text, position = self.engine(text, style=style, width=width,
                                     refill=refill, tabify=tabify,
                                     position=position)
        lisp.delete_region(start, end)
        lisp.insert(text)
        if position is not None:
            lisp.goto_char(start + position)

    def clean_undo_after(self, checkpoint):
        """\
Remove all intermediate boundaries from the Undo list since CHECKPOINT.
"""
        # Declare some LISP functions.
        car = lisp.car
        cdr = lisp.cdr
        eq = lisp.eq
        rplacd = lisp.rplacd
        # Remove any `nil' delimiter recently added to the Undo list.
        cursor = lisp.buffer_undo_list
        if not eq(cursor, checkpoint):
            tail = cdr(cursor)
            while not eq(tail, checkpoint):
                if car(tail):
                    cursor = tail
                    tail = cdr(tail)
                else:
                    tail = cdr(cursor)
                    rplacd(cursor, tail)

    def message(self, message):
        lisp.message(message)

    def error(self, message):
        lisp.error(message)

class Marker:

    ## Heuristic to simulate a marker while reformatting boxes.

    def __init__(self, rebox, style1, style2):
        """\
Consider REBOX styles STYLE1 and STYLE2.  Take good note of all characters
used by these styles, as well as whitespace.
"""
        ignore = self.ignore = {}
        for character in ' \t\r\n':
            ignore[character] = None
        for style in style1, style2:
            guess_data, build_data = rebox.style_data[style]
            merge_nw, merge_se, nw, nn, ne, ww, ee, sw, ss, se = build_data
            for text in nw, nn, ne, ww, ee, sw, ss, se:
                if text:
                    for character in text:
                        ignore[character] = None
        self.position = None

    def save_position(self, text, position):
        """\
Given a TEXT and a POSITION in that text, save the adjusted position
by faking that all ignorable characters before POSITION were removed.
"""
        ignore = self.ignore
        counter = 0
        for character in text[:position]:
            if ignore.has_key(character):
                counter = counter + 1
        self.position = position - counter

    def get_position(self, text, latest=0):
        """\
Given a TEXT, return the smallest value that would yield the currently saved
position, if it was saved by `save_position'.  If LATEST is true, then
return the biggest value instead of the smallest.  Unless the position lies
within a series of ignored characters, LATEST has no effect in practice.
"""
        ignore = self.ignore
        counter = 0
        position = 0
        if latest:
            for character in text:
                if ignore.has_key(character):
                    counter = counter + 1
                else:
                    if position == self.position:
                        break
                    position = position + 1
        elif self.position > 0:
            for character in text:
                if ignore.has_key(character):
                    counter = counter + 1
                else:
                    position = position + 1
                    if position == self.position:
                        break
        return position + counter

## Main execution control.

usage = """\
"""

def main(*arguments):
    style = None
    width = 79
    refill = 1
    tabify = 0
    import getopt
    options, arguments = getopt.getopt(arguments, 'ns:tw:', ['help'])
    for option, value in options:
        if option == '--help':
            sys.stdout.write(__doc__)
            sys.exit(0)
        elif option == '-n':
            refill = 0
        elif option == '-s':
            style = int(value)
        elif option == '-t':
            tabify = 1
        elif option == '-w':
            width = int(value)
    if len(arguments) == 0:
        text = sys.stdin.read()
    elif len(arguments) == 1:
        text = open(arguments[0]).read()
    else:
        sys.stderr.write("Invalid usage, try `rebox --help' for help.\n")
        sys.exit(1)
    rebox = Batch_Rebox()
    text, position = rebox.engine(text, style=style, width=width,
                                  refill=refill, tabify=tabify)
    sys.stdout.write(text)

def pymacs_load_hook():
    global pymacs, lisp, region, comment
    import pymacs
    from pymacs import lisp
    # Declare entry points for Emacs to import.
    rebox = Emacs_Rebox()
    region = rebox.region
    comment = rebox.comment

if __name__ == '__main__':
    apply(main, sys.argv[1:])
