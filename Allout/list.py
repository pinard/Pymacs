#!/usr/bin/env python
# -*- coding: Latin-1 -*-
# Copyright © 2001, 2002, 2003 Progiciels Bourbeau-Pinard inc.
# François Pinard <pinard@iro.umontreal.ca>, 2001.

"""\
Lorsque ACTION est `list', ce programme reformatte le fichier un peu mieux,
en vue de l'examen visuel ou de l'impression.  Nous avons alors:

Usage: allout list [OPTION]... [FICHIER]

   -a             Produire un format `allout' plutôt qu'un format `listing'
   -s SÉLECTION   Limiter le traitement au sous-arbre SÉLECTION

FICHIER contient le fichier `allout' à lire, entrée standard si non fourni.

L'option `-a' restitue un fichier `allout' sur la sortie.

L'option `-s' introduit une liste de nombres séparés par des points.  Ces
nombres décrivent un parcours de sélection d'un sous-arbre par la sélection
successive d'un embranchement à chaque niveau.  À chaque niveau, le nombre 0
représente la tête du niveau, les nombres 1 et suivants représentent les
branches comptées à partir de la première, les nombres -1 et précédents
représentent les branches comptées à partir de la dernière.  Cette sélection
s'effectue sur l'arbre après les simplifications décrites plus haut.
"""

import sys

class Main:
    def __init__(self):
        self.allout = False
        self.selection = []

    def main(self, *arguments):
        self.allout = False
        self.selection = []
        import getopt
        options, arguments = getopt.getopt(arguments, 'as:')
        for option, value in options:
            if option == '-a':
                self.allout = True
            elif option == '-s':
                self.selection = map(int, value.split('.'))
        # Lire le fichier en format `allout'.
        import allout
        if len(arguments) == 0:
            structure = allout.read()
        elif len(arguments) == 1:
            structure = allout.read(arguments[0])
        else:
            raise allout.UsageError, "Trop d'arguments."
        # Choisir la sous-branche désirée.
        for branche in self.selection:
            structure = structure[branche]
        # Imprimer la liste résultante.
        if self.allout:
            write(structure)
        else:
            write_listing(structure)

main = Main().main

def write(structure, output=sys.stdout.write):
    # Transformer l'arbre STRUCTURE en un fichier `allout'.  Le résultat est
    # écrit sur OUTPUT, qui doit être une fonction d'écriture ou encore, le
    # nom d'un fichier à créer.
    if isinstance(output, str):
        write_recursive(structure, file(output, 'w').write, 0)
    else:
        write_recursive(structure, output, 0)

def write_recursive(structure, write, level):
    if isinstance(structure, str):
        write('%*s %s\n' % (level, '', structure))
        return
    if level == 0:
        write('* %s\n' % structure[0])
    elif level == 1:
        write('.. %s\n' % structure[0])
    else:
        write('.%*s %s\n' % (level, '.:,;'[(level-1) % 4], structure[0]))
    for branch in structure[1:]:
        write_recursive(branch, write, level+1)

def write_listing(structure, output=sys.stdout.write):
    # Transformer l'arbre STRUCTURE en une liste destinée à être lue par un
    # humain, utilisant une marge blanche croissante, et des lignes
    # blanches, pour souligner l'arboresence.  Le résultat est écrit sur
    # OUTPUT, qui doit être une fonction d'écriture ou encore, le nom d'un
    # fichier à créer.
    if isinstance(output, str):
        write_listing_recursive(structure, file(output, 'w').write, 0, False)
    else:
        write_listing_recursive(structure, output, 0, False)

def write_listing_recursive(structure, write, level, spacing):
    # SPACING est True à l'entrée si la structure précédente s'imprimait sur
    # plusieurs lignes, et la valeur de cette fonction est True pour
    # indiquer que STRUCTURE a requis plus d'une ligne pour s'imprimer.
    if spacing or (isinstance(structure, list) and len(structure) > 1):
        write('\n')
    write('  ' * level)
    if isinstance(structure, str):
        write(structure)
        write('\n')
        return False
    write(structure[0])
    write('\n')
    spacing = False
    for element in structure[1:]:
        spacing = write_listing_recursive(element, write, level+1, spacing)
    return len(structure) > 1

if __name__ == '__main__':
    main(*sys.argv[1:])
