.. role:: code(strong)
.. role:: file(literal)

================================
Ephemeral mail groups under Gnus
================================

-------------------------
Yet another Gnus back end
-------------------------

.. contents::
.. sectnum::

This page documents the :file:`contrib/nn/` subdirectory of the
Pymacs distribution.

  **This is not real documentation.  As it stands, this is more a random
  collection of remarks from other sources.  And besides, it might well
  go away completely...**

.. Introduction
.. ============
..
.. This is a helper tool for handling ephemeral email groups under Gnus.
..
.. As a user tool
.. ==============

As a Pymacs example
===================

The problem
,,,,,,,,,,,

I've been reading, saving and otherwise handling electronic mail
from within Emacs for a lot of years, even before Gnus existed.  The
preferred Emacs archiving disk format for email is Babyl storage, and
the special :code:`Rmail` mode in Emacs handles Babyl files.  With
years passing, I got dozens, then hundreds, then thousands of such
Babyl files, each of which holds from as little as only one to maybe
a few hundreds individual messages.  I tried to tailor :code:`Rmail`
mode in various ways to MIME, foreign character sets, and many other
nitty-gritty habits.  One of these habits was to progressively eradicate
paragraphs in messages I was visiting many times, as users were often
using a single message to report many problems or suggestions all at
once, while I was often addressing issues one at a time.

When I took maintenance of some popular packages, like GNU :code:`tar`,
my volume of daily email raised drastically, and I choose Gnus as a way
to sustain the heavy load.  I thought about converting all my Babyl
files to :code:`nnml` format, but this would mean loosing many tools
I wrote for Babyl files, consuming a lot of i-nodes, and also much
polluting my :code:`*Group*` buffer.  I rather chose to select and
read Babyl files as ephemeral mail groups (and for doing so, developed
Emacs user machinery so selection could be done very efficiently).
Gnus surely gave me for free nice MIME and cryptographic features,
and a flurry of handsome and useful commands, compared to previous
:code:`Rmail` mode.  On the other hand, Gnus did not allow me to modify
individual messages in Babyl files, so for a good while, I had to give
up on some special handling, like eradicating paragraphs as I used to
do.

This pushed me into writing my own Gnus back end for Babyl files: making
sure I correctly implement the article editing and modification support
of the back end API.  I chose Python to do so because I already had
various Python tools for handling Babyl files, because I wanted to
connect other Python scripts to the common mechanics, and of course
because Pymacs was making this project feasible.  Nowadays, Babyl file
support does not go very far beyond Emacs itself, while many non-Emacs
tools for handling Unix mailbox folders are available.  Spam fighting
concerns brought me to revisit the idea of massively transforming all
my Babyl files to Unix mailbox format, and I discovered that it would
be a breeze to do, if I only adapted the Python back end to handle Unix
mailbox files as well as Babyl, transparently.

Python side
,,,,,,,,,,,

I started by taking the Info nodes of the Gnus manual which were
describing the back end interface, and turning them all into a long
Python comment.  I then split that comment into one dummy function per
back end interface function, meant to write some debugging information
when called, and then return failure to Gnus.  This was enough to
explore what functions were needed, and in which circumstances.  I then
implemented enough of them so ephemeral Babyl groups work, while solid
groups might require more such functions.  The unimplemented functions
are still sitting in the module, with their included comments and
debugging code.

Emacs side
,,,,,,,,,,

One difficulty is ensuring that :code:`Nn` contents
(:file:`nncourrier.py` and :file:`folder.py`) have to be on the Python
or Pymacs search path.  The :file:`__init__.py` and package nature are
not essential.
