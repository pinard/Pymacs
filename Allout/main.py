#!/usr/bin/env python
# -*- coding: Latin-1 -*-
# Copyright © 2001, 2002, 2003 Progiciels Bourbeau-Pinard inc.
# François Pinard <pinard@iro.umontreal.ca>, 2001.

"""\
Lit un fichier `allout', ou une partie d'un tel, et effectue divers
traitements sur ce fichier.  L'appel générique est:

Usage: allout ACTION [OPTION]... [FICHIER]...
"""

import sys

def main(*arguments):
    import allout
    if not arguments:
        sys.stdout.write(__doc__)
        import list, texi
        for module in list, texi, allout:
            sys.stdout.write('\n')
            sys.stdout.write(module.__doc__)
        sys.exit(0)
    action = arguments[0]
    arguments = arguments[1:]
    try:
        if action == 'list':
            import list
            list.main(*arguments)
        elif action == 'texi':
            import texi
            texi.main(*arguments)
        else:
            raise allout.UsageError, "Unknown ACTION."
    except allout.UsageError, message:
        sys.stderr.write("* %s\n* Try `allout' without arguments for help.\n"
                         % message)
        sys.exit(1)

if __name__ == '__main__':
    main(*sys.argv[1:])
