#!/usr/bin/env python
# -*- coding: Latin-1 -*-
# Copyright © 1995, 1997, 2002, 2003 Progiciels Bourbeau-Pinard inc.
# François Pinard <pinard@iro.umontreal.ca>, 1995-01.

"""\
Lorsque ACTION est `texi', ce programme produit un fichier Texinfo à partir
des indications contenues dans le fichier `allout'.  (Convert a file from
allout (outline) format back to Texinfo format.)  Nous avons alors:

Usage: allout texi [OPTION]... [INPUT]...

  -H        suppress Texinfo file header
  -T        suppress Texinfo file trailer
  -I PATH   search included Texinfo files along PATH

Les conventions d'écriture d'un fichier `allout' en vue d'une transformation
Texinfo ne sont pas encore décrites ici.  Pour l'un des ces jours pluvieux!
"""

from __future__ import generators
import os, re, sys

Default_Copyright = """\
Permission is granted to make and distribute verbatim copies of
this manual provided the copyright notice and this permission notice
are preserved on all copies.

@ignore
Permission is granted to process this file through TeX and print the
results, provided the printed document carries copying permission
notice identical to this one except for the removal of this paragraph
(this paragraph not being relevant to the printed manual).

@end ignore
Permission is granted to copy and distribute modified versions of this
manual under the conditions for verbatim copying, provided that the entire
resulting derived work is distributed under the terms of a permission
notice identical to this one.

Permission is granted to copy and distribute translations of this manual
into another language, under the above conditions for modified versions,
except that this permission notice may be stated in a translation approved
by the Foundation.
"""

directive_map = {
    ('@section', 1) : '@chapter',
    ('@section', 2) : '@section',
    ('@section', 3) : '@subsection',
    ('@section', 4) : '@subsubsection',
    ('@unnumbered', 1) : '@unnumbered',
    ('@unnumbered', 2) : '@unnumberedsec',
    ('@unnumbered', 3) : '@unnumberedsubsec',
    ('@unnumbered', 4) : '@unnumberedsubsubsec',
    ('@heading', 1) : '@majorheading',
    ('@heading', 2) : '@heading',
    ('@heading', 3) : '@subheading',
    ('@heading', 4) : '@subsubheading',
    ('@appendix', 1) : '@appendix',
    ('@appendix', 2) : '@appendixsec',
    ('@appendix', 3) : '@appendixsubsec',
    ('@appendix', 4) : '@appendixsubsubsec',
    }

class Main:
    def __init__(self):
        # Options.
        self.includes = []
        self.header = True
        self.trailer = True
        # Variables.
        self.French = False
        self.Titlepage = None
        self.Oneliner = None            # `\n' included
        self.Copyline = None
        self.Filename = None
        self.Header = None
        self.Version = None
        self.Edition = None
        self.Updated = None
        self.Entries = None
        self.Title = None
        self.Subtitle = None
        self.Subtitle2 = None
        self.Author = None
        self.Author2 = None
        self.Description = None
        self.Copyright = None            # `\n' included
        # Flattener.
        import string
        self.flattener = string.maketrans('àâçéêèëîïôûùüÀÂÇÉÊÈËÎÏÔÛÙÜ«»:`\'',
                                          'aaceeeeiiouuuAACEEEEIIOOUU     ')
        # Index processing.
        self.equivalences = {}
        self.delayed_text = ''

    def main(self, *arguments):
        arguments = self.save_options(arguments)
        if arguments:
            for argument in arguments:
                self.process_file(argument, file(argument))
        else:
            self.process_file('<stdin>', sys.stdin)

    def save_options(self, arguments):
        # Decode options.
        import getopt
        options, arguments = getopt.getopt(arguments, 'I:HT')
        for option, value in options:
            if option == '-I':
                self.includes = value.split(':')
            elif option == '-H':
                self.header = False
            elif option == '-T':
                self.trailer = False
        return arguments

    def process_file(self, name, input):
        self.input_name = name
        structure = self.extract_structure(input)
        self.ensure_values()
        write = sys.stdout.write
        if self.header:
            self.produce_header(write)
        self.process_structure(structure, write, 0)
        if self.trailer:
            self.produce_trailer(write)

    def extract_structure(self, input):
        # Process initial lines.
        line = input.readline()
        if line and line[0] not in '*.':
            line = line.rstrip()
            for ending in '-*- outline -*-', 'allout':
                if line.endswith(ending):
                    line = line[:-len(ending)].rstrip()
            self.Oneliner = line + '\n'
            line = input.readline()
        if line and line[0] not in '*.':
            match = re.match('Copyright (\(C\)|©) (.*)', line)
            if not match:
                sys.stderr.write(
                    "%(input_name)s might not be in proper format.\n"
                    % self.__dict__)
                sys.exit(1)
            self.Copyline = match.group(2) + '\n'
            line = input.readline()
        variable = None
        spacing = 0
        while line and line[0] not in '*.':
            line = line.rstrip()
            match = re.match('(\S+):\s+(.*)', line)
            if match:
                if variable:
                    self.set_variable(variable, ''.join(fragments))
                variable = match.group(1)
                fragments = [match.group(2)]
                spacing = 0
            elif line:
                assert variable
                if fragments:
                    spacing += 1
                if spacing:
                    fragments.append('\n' * spacing)
                    spacing = 0
                if variable == 'Entries' and line[0] == '-':
                    line = '*' + line[1:]
                fragments.append(line)
            else:
                spacing += 1
            line = input.readline()
        if variable:
            self.set_variable(variable, ''.join(fragments))
        # Return the allout part as a structure.
        def generator(line, input):
            yield line
            for line in input:
                yield line
        import allout
        return allout.read(generator(line, input))

    def ensure_values(self):
        # Ensure values to some variables.
        if not self.Filename:
            self.Filename = os.path.splitext(self.input_name)[0] + '.info'
        if not self.Header:
            if self.Title:
                self.Header = self.Title
            else:
                self.Header = self.input_name
        if not self.Title:
            self.Title = self.Header
        if self.header and not self.Copyright:
            if os.path.exists('copyrall'):
                self.Copyright = file('copyrall').read()
            elif os.path.exists('../copyrall'):
                self.Copyright = file('../copyrall').read()
            else:
                self.Copyright = Default_Copyright

    def set_variable(self, variable, value):
        if variable[0].isupper() and hasattr(self, variable):
            setattr(self, variable, value)
        else:
            sys.stderr.write("%s: Unknown variable `%s'\n"
                             % (self.input_name, variable))

    def produce_header(self, write):
        # Produce the long document header.
        if self.French and self.French.lower() not in ('0', 'false',
                                                       'no', 'non'):
            write('\\def\\putwordTableofContents{Table des mati\\`eres}\n'
                  '\\input texinfoec @c -*- texinfo -*-\n')
        else:
            write('\\input texinfo\n')
        write('@c %%**start of header\n'
              '@setfilename %(Filename)s\n'
              '@settitle %(Header)s\n'
              '@finalout\n'
              '@c %%**end of header\n'
              % self.__dict__)
        if self.Version or self.Edition or self.Updated:
            write('\n')
            if self.Version:
                write('@set VERSION %(Version)s\n' % self.__dict__)
            if self.Edition:
                write('@set EDITION %(Edition)s\n' % self.__dict__)
            if self.Updated:
                write('@set UPDATED %(Updated)s\n' % self.__dict__)
        elif os.path.exists('version.texi'):
            write('\n')
            if self.includes:
                self.include('version.texi')
            else:
                write('@include version.texi\n')
        write('\n'
              '@ifinfo\n'
              '@set Francois Franc,ois\n'
              '@end ifinfo\n'
              '@tex\n'
              '@set Francois Fran\\noexpand\\ptexc cois\n'
              '@end tex\n')
        if self.Entries:
            write('\n'
                  '@ifinfo\n'
                  '@format\n'
                  'START-INFO-DIR-ENTRY\n'
                  '%(Entries)s'
                  'END-INFO-DIR-ENTRY\n'
                  '@end format\n'
                  '@end ifinfo\n'
                  % self.__dict__)
        write('\n'
              '@ifinfo\n'
              '%(Oneliner)s'
              '\n'
              'Copyright © %(Copyline)s\n'
              '\n'
              '%(Copyright)s'
              '@end ifinfo\n'
              '\n'
              '@titlepage\n'
              % self.__dict__)
        if self.Titlepage:
            write('%(Titlepage)s' % self.__dict__)
        else:
            write('@title %(Title)s\n' % self.__dict__)
            if self.Subtitle:
                write('@subtitle %(Subtitle)s\n' % self.__dict__)
            if self.Subtitle2:
                write('@subtitle %(Subtitle2)s\n' % self.__dict__)
            if self.Author:
                write('@author %(Author)s\n' % self.__dict__)
            if self.Author2:
                write('@author %(Author2)s\n' % self.__dict__)
        write('\n'
              '@page\n'
              '@vskip 0pt plus 1filll\n'
              #'@insertcopying\n'
              'Copyright @copyright{} %(Copyline)s\n'
              '\n'
              '%(Copyright)s\n'
              '@end titlepage\n'
              '\n'
              '@ifinfo\n'
              '@node Top\n'
              '@top %(Header)s\n'
              % self.__dict__)
        if self.Description:
            write('\n%(Description)s\n' % self.__dict__)
        write('\n'
              '@menu\n'
              '@end menu\n'
              '\n'
              '@end ifinfo\n')

    def produce_trailer(self, write):
        write('\n'
              '@contents\n'
              '@bye\n'
              '\n'
              # Split the following line so Emacs will not recognize it,
              # while editing this script.
              '@c Local ' 'variables:\n'
              '@c texinfo-column-for-description: 32\n'
              '@c End:\n')

    def process_structure(self, structure, write, level):
        # Transform the allout structure.
        if isinstance(structure, str):
            self.output_text(structure, write)
            return
        if ' ' in structure[0]:
            first, rest = structure[0].split(None, 1)
        else:
            first = structure[0]
            if first.endswith('.all'):
                texi_name = first[:-4] + '.texi'
                if self.includes:
                    self.include(texi_name)
                    return
                write('@include %s\n' % texi_name)
                return
            rest = ''
        if first.startswith('@'):
            if first in ('@section', '@unnumbered', '@heading', '@appendix'):
                try:
                    directive = directive_map[first, level+1]
                except KeyError:
                    directive = '@c %s-%d' % (first[1:], level+1)
                if ',' in rest:
                    second, third = rest.split(',', 1)
                else:
                    second = third = rest
                if second != '-':
                    second = second.replace('@@', ' ')
                    second = re.sub(r'@[^{]+{([^}]*)}', r'\1', second)
                    second = second.translate(self.flattener)
                    second = re.sub('  +', ' ', second)
                    write('@node %s\n' % second)
                self.output_text('%s %s' % (directive, third), write)
                for sub in structure[1:]:
                    self.process_structure(sub, write, level+1)
                return
            if first in ('@display', '@example', '@format', '@lisp', '@menu',
                         '@quotation', '@smalldisplay', '@smallexample',
                         '@smallformat', '@smalllisp'):
                assert not rest, rest
                write('%s\n' % first)
                for sub in structure[1:]:
                    self.process_structure(sub, write, level)
                write('@end %s\n' % first[1:])
                return
            if first in ('@enumerate', '@itemize', '@table'):
                if rest:
                    write('%s %s\n' % (first, rest))
                else:
                    write('%s\n' % first)
                for sub in structure[1:]:
                    self.process_structure_item(sub, write, level)
                write('@end %s\n' % first[1:])
                return
        if structure[0]:
            self.output_text(structure[0], write)
        for sub in structure[1:]:
            self.process_structure(sub, write, level)

    def process_structure_item(self, structure, write, level):
        # Transform an allout structure while introducing an @item.
        if structure[0]:
            self.output_text('@item %s' % structure[0], write)
        else:
            write('@item\n')
        for sub in structure[1:]:
            self.process_structure(sub, write, level)

    def include(self, name, write):
        for directory in self.includes:
            if os.path.exists('%s/%s' % (directory, name)):
                name = '%s/%s' % (directory, name)
                break
        sys.stderr.write("Including %s..." % name)
        inside = False
        for line in file(name):
            if inside:
                if line in ('@contents\n', '@bye\n'):
                    break
                write(line)
            elif line.startswith('@node '):
                if line != '@node Top\n' and not line.startswith('@node top,'):
                    inside = True
                    write(line)
        sys.stderr.write(" done\n")

    def output_text(self, text, write,
                    searcher = re.compile('@<([^>]*)>([^ ]*)').search):

        def output_protecting_colons(text):
            # Force a space before textual colons.
            text = re.sub(r'([^ ]):$', r'\1@w{ :}', text)
            text = re.sub(r'([^ ]): ', r'\1@w{ :} ', text)
            write('%s\n' % text)

        # Merge text after anything delayed.
        if self.delayed_text:
            text = self.delayed_text + ' ' + text
            self.delayed_text = ''
        # If line fully empty, only then produce an empty line.
        if not text:
            write('\n')
            return
        # Recognise index entries and produce them.
        match = searcher(text)
        while match:
            fragment = text[:match.start()].rstrip() + match.group(2)
            if fragment:
                output_protecting_colons(fragment)
            fragments = [fragment.strip()
                         for fragment in match.group(1).split('::')]
            if len(fragments) > 1:
                # Declare an equivalence between index entries.
                entries = []
                for fragment in fragments:
                    fragment = fragment.strip()
                    if ':' in fragment:
                        index, entry = fragment.split(':', 1)
                    else:
                        index, entry = 'c', fragment
                    assert (index, entry) not in self.equivalences, (
                        self.equivalences[index, entry])
                    entries.append((index, entry))
                for index, entry in entries:
                    self.equivalences[index, entry] = entries
            else:
                # Process an actual index entry.
                for fragment in match.group(1).split(';'):
                    fragment = fragment.strip()
                    if ':' in fragment:
                        index, entry = fragment.split(':', 1)
                    else:
                        index, entry = 'c', fragment
                    try:
                        entries = self.equivalences[index, entry]
                    except KeyError:
                        entries = [(index, entry)]
                    for index, entry in entries:
                        write('@%sindex %s\n' % (index, entry))
            text = text[match.end():].lstrip()
            match = searcher(text)
        if text:
            match = re.search('@<', text)
            if match:
                # Incomplete index entry, delay it until next line.
                self.delayed_text = text[match.start():]
                text = text[:match.start()]
            output_protecting_colons(text)

main = Main().main

if __name__ == '__main__':
    main(*sys.argv[1:])
