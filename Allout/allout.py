#!/usr/bin/env python
# -*- coding: Latin-1 -*-
# Copyright © 2001, 2002, 2003 Progiciels Bourbeau-Pinard inc.
# François Pinard <pinard@iro.umontreal.ca>, 2001.

"""\
Un fichier `allout', pour lequel existe un mode Emacs, permet de représenter
une organisation hiérarchique de l'information contenue, avec la possibilité
d'un court libellé au sommet de chaque hiérarchie ou sous-hiérarchie.  Le
fichier utilise des marques spéciales pour marquer la structure, soit `*'
complètement à gauche d'une ligne pour marquer le début d'une hiérarchie
englobante, soit `.' à gauche d'une ligne, suivi d'un nombre arbitraire de
blancs et de l'un des caractères `*+-@.:,;', pour marquer le début d'une
hiérarchie plus imbriquée, l'imbrication étant d'autant plus importante que
le caractère `*+-@.:,;' est plus à droite.  La marque doit être le dernier
caractère sur sa ligne, ou encore, être suivie d'au moins un caractère blanc
puis d'un libellé associé à la hiérarchie introduite par cette marque.
Toute ligne n'introduisant pas de marque est une ligne de texte associée à
l'élément hiérarchique le plus récemment introduit.

Ce programme ajoute quelques interprétations particulières à un fichier
`allout' tel que défini dans Emacs.  Pour permettre à un fichier d'utiliser
plusieurs hiérarchies successivement introduites par une marque `*', un
texte qui précéderait la première marque `*' est considéré comme
super-englobant, et la toute première ligne non-blanche de ce texte préfixe
est alors le libellé associé à cette hiérarchie super-englobante.  Dans
toutes les hiérarchies, sont éliminées les lignes blanches préfixes ou
suffixes, les imbrications superflues (pas de libellé et un seul élément),
et une marge gauche commune à toutes les lignes de texte d'un même niveau.

Report bugs or suggestions to François Pinard <pinard@iro.umontreal.ca>.
"""

import sys

def read(input=sys.stdin):
    # Lire INPUT, qui est soit un fichier déjà ouvert, soit le nom d'un
    # fichier à lire, puis retourner un arbre représentant la structure
    # `allout' de ce fichier, ou None dans le cas d'un fichier vide.
    # L'arbre produit est une liste contenant récursivement d'autres listes.
    # Chaque liste débute par une chaîne donnant le libellé d'un noeud, et
    # contient ensuite dans l'ordre une chaîne par ligne ordinaire dans ce
    # noeud ou une sous-liste pour un sous-noeud dans ce noeud.

    # LEVEL vaut 0 pour la hiérarchie super-englobante, 1 pour la hiérarchie
    # `*', 2 pour la hiérarchie `..', etc.  STACK[LEVEL] contient la liste
    # des hiérarchies tout-à-fait complétées au niveau LEVEL.  Si
    # STACK[LEVEL+1] existe, STACK[LEVEL] devra nécessairement recevoir un
    # nouvel élément au plus tard à la rencontre de la fin de fichier.

    def collapse():
        # Rapetisser (ou allonger) la pile STACK pour lui donner exactement
        # la longueur LEVEL, tout en déclarant que les structures empilées
        # au-delà ont terminé leur croissance: on peut donc immédiatement
        # imbriquer ces structures dans l'arbre en construction.
        while len(stack) < level:
            stack.append([''])
        while len(stack) > level:
            structure = stack.pop()
            while len(structure) > 1 and structure[-1] == '':
                del structure[-1]
            if len(structure) == 2 and structure[0] == '':
                structure = structure[1]
            else:
                margin = None
                for line in structure[1:]:
                    if isinstance(line, str) and line:
                        count = re.match(' *', line).end(0)
                        if margin is None or count < margin:
                            margin = count
                if margin is not None:
                    for counter in range(1, len(structure)):
                        line = structure[counter]
                        if isinstance(line, str) and line:
                            structure[counter] = line[margin:]
            stack[-1].append(structure)

    if isinstance(input, str):
        input = file(input)
    import re
    stack = []
    for line in input:
        match = re.match(r'(\*|\. *[-*+@.:,;])', line)
        if match:
            level = match.end(0)
            collapse()
            stack.append([line[level:].strip()])
        elif stack:
            line = line.rstrip()
            if line or len(stack[-1]) > 1:
                stack[-1].append(line)
        else:
            line = line.strip()
            if line:
                stack.append([line])
    level = 1
    collapse()
    if len(stack[0]) == 2 and stack[0][0] == '':
        stack[0] = stack[0][1]
    return stack[0]
