#!/usr/bin/env python
# -*- coding: Latin-1 -*-
# Copyright © 2003 Progiciels Bourbeau-Pinard inc.
# François Pinard <pinard@iro.umontreal.ca>, 2003-02.

"""\
Gnus back-end for editable Babyl or Mbox files, implemented in Python.
Here is how I get it all in motion from `.emacs'.

;; [...]

;; Use the following line if you prefer to save in mbox than in Babyl files.
(defconst gnus-default-article-saver 'gnus-summary-save-in-mail)

;; [...]

(defun fp-maybe-start-gnus ()
  "Have Gnus started, if not already."
  (unless (and (fboundp 'gnus-alive-p) (gnus-alive-p))
    (save-window-excursion (gnus))))

;; [...]

;;;; Lecture de courriel.

;; Lien aux fichiers Babyl.

(require 'rmail)

(defun rmail (file-name)
  (interactive)
  (fp-courriel-display-file-with-gnus file-name))

(defun rmail-mode ()
  (interactive)
  (let ((file-name buffer-file-name))
    (kill-buffer nil)
    (fp-courriel-display-file-with-gnus file-name)))

;; Lien aux fichiers mbox.

(defun fp-courriel-find-file-routine ()
  (when (and buffer-file-name
	     (or (string-match "/courriel/" buffer-file-name)
		 (string-match "/COURRIEL" buffer-file-name)))
    (let ((file-name buffer-file-name))
      (kill-buffer nil)
      (fp-courriel-display-file-with-gnus file-name))))
(add-hook 'find-file-hooks 'fp-courriel-find-file-routine)

;; Lancement de Gnus.

(defun fp-courriel-display-file-with-gnus (file-name)
  "Display a mail file with Gnus, using a special ephemeral server."
  ;; `nncourriel' is a backend I wrote, in Python, so Gnus may be used to read
  ;; and edit Babyl or mbox files.
  (fp-maybe-start-gnus)
  (unless (featurep 'nncourriel)
    (pymacs-load "Pymacs.Nn.nncourriel"))
  (if (gnus-group-read-ephemeral-group
       (concat "nncourriel:"
	       (fp-string-replace
		(fp-string-replace
		 (substring (expand-file-name file-name) 1)
		 "." "@")
		"/" "."))
       '(nncourriel "")
       t
       (cons (current-buffer) (current-window-configuration)))
      (cd-absolute (file-name-directory file-name))
    (gnus-error 3 "Mail file as group couldn't be entered")))

(defun fp-string-replace (string before after)
  (let ((new-string (make-string (length string) ? ))
	(before (aref before 0))
	(after (aref after 0))
	(index 0))
    (while (< index (length string))
      (let ((byte (aref string index)))
	(when (= byte after)
	  (error "`%s' already within `%s'" after string))
	(aset new-string index (if (= byte before) after byte)))
      (setq index (1+ index)))
    new-string))
"""                                     # '

# REVOIR:
# - Double Summary au départ.

from Pymacs import Let, lisp
OK = lisp.t

test_mode = False

try:
    from Local import commun
    Debug = commun.Debug
    NoDebug = commun.NoDebug
except ImportError:
    class Debug:
        def __init__(self, *arguments): pass
        def __call__(self, *arguments): pass
    NoDebug = Debug

try:
    from Local import folder
except ImportError:
    import folder

class Error(Exception):
    pass

### Server objects.

class Server:
    def __init__(self, server, definitions):
        self.server = server
        self.definitions = definitions
        self.status = None
        if server.endswith('-ephemeral'):
            server = server[:-10]
        self.directory = '/' + server.replace('.', '/').replace('@', '.')
        self.group_registry = {}

    def request_group(self, group, fast):
        if group not in self.group_registry:
            self.group_registry[group] = Group(self, group)
        if fast is None:
            self.group_registry[group].initial_respond()
        return OK

    def close_group(self, group):
        self.group_registry[group].close()
        del self.group_registry[group]
        return OK

    def request_scan(self, group):
        if group in self.group_registry:
            return self.group_registry[group].request_scan()

    def retrieve_headers(self, articles, group, fetch_old):
        return self.group_registry[group].retrieve_headers(articles, fetch_old)

    def request_article(self, article, group, to_buffer):
        return self.group_registry[group].request_article(article, to_buffer)

    def request_update_mark(self, group, article, mark):
        return self.group_registry[group].request_update_mark(article, mark)

    def request_replace_article(self, article, group, buffer):
        return self.group_registry[group].request_replace_article(
            article, buffer)

    def respond(self, response):
        # Replace `nntp-server-buffer' contents with RESPONSE.
        self.replace_buffer_contents(lisp.nntp_server_buffer.value(), response)

    def replace_buffer_contents(self, buffer, response):
        # Insert RESPONSE as the new contents for BUFFER.
        if test_mode:
            debug('INSERT_INTO_BUFFER', 'buffer', 'response')
        else:
            let = Let().push_excursion()
            lisp.set_buffer(buffer)
            lisp.erase_buffer()
            lisp.insert(response)

    def error(self, message):
        message = str(message)
        debug('error', 'message')
        # Report MESSAGE and raise Error.  The error should always be caught
        # in a try/except block, and then, None should get returned to Gnus.
        self.status = message
        report(message)
        # Gnus does not really report an error to the user.  So for now,
        # force a hard Lisp error, to make sure the user sees it...  Grrr!
        if not test_mode:
            lisp.error(message)
        raise Error

### Group objects.

class Group:
    def __init__(self, server, group):
        self.server = server
        self.group_name = group
        import os
        try:
            self.folder = folder.folder(
                os.path.join(server.directory,
                             group.replace('.', '/').replace('@', '.')),
                strip201=True)
        except folder.Error, message:
            self.server.error(message)
        self.marks = [' '] * len(self.folder)

    def initial_respond(self):
        self.server.respond(
            '211 %d %d %d %s\n'
            % (len(self.folder), 1, len(self.folder), self.group_name))

    def close(self):
        deleted = written = 0
        for counter in range(len(self.folder)):
            if self.marks[counter] == 'E':
                self.folder.mark_deleted(counter)
                deleted +=1
            else:
                written +=1
        if written == 0 or deleted > 0 or self.folder.modified:
            if written == 0:
                before = "Permanently delete all messages? "
                after = "Removing file %s" % self.folder.file_name
            elif deleted == 0:
                before = "Save modified messages? "
                after = "Rewriting all %d messages" % written
            else:
                before = "Permanently delete %d messages? " % deleted
                after = "Deleting %d messages, keeping %d" % (deleted, written)
            if self.folder.count201 > 0:
                before += "(%d `\\201's) " % self.folder.count201
            if lisp.y_or_n_p(before) is None:
                self.server.error("May not rewrite file")
            lisp.message(after)
            try:
                self.folder.close(
                    lisp.make_backup_file_name(self.folder.file_name))
            except folder.Error, message:
                self.server.error(message)
        else:
            lisp.message("No need to save")
        self.server = None
        return OK

    def request_scan(self):
        try:
            self.folder.rescan()
        except folder.Error, message:
            self.server.error(message)
        count = len(self.folder) - len(self.marks)
        if count > 0:
            lisp.message("%d new articles" % count)
            self.marks += [' '] * count
        return OK

    def retrieve_headers(self, articles, fetch_old):
        # FETCH_OLD is not supported, as it is meaningless here.

        def append_cleaned(header, prefix=''):
            text = headers[header]
            if text is None:
                fields.append(prefix)
            else:
                fields.append(prefix + ' '.join(text.split()))

        if not test_mode:
            articles = articles.copy()
        fragments = []
        for article in articles:
            try:
                headers = self.folder.message_headers(article-1)
            except folder.Error, message:
                self.server.error(message)
            fields = [str(article)]
            append_cleaned('subject')
            append_cleaned('from')
            append_cleaned('date')
            append_cleaned('message-id')
            append_cleaned('references')
            chars, lines = self.folder.chars_lines(article-1)
            if headers['chars'] is None:
                fields.append(str(chars))
            else:
                append_cleaned('chars')
            if headers['lines'] is None:
                fields.append(str(lines))
            else:
                append_cleaned('lines')
            if headers['xref'] is None:
                fields.append('')
            else:
                append_cleaned('xref', 'Xref: ')
            fields.append('\n')
            fragments.append('\t'.join(fields))
        self.server.respond(''.join(fragments))
        return lisp.nov

    def request_article(self, article, to_buffer):
        if to_buffer is None:
            to_buffer = lisp.nntp_server_buffer.value()
        self.server.replace_buffer_contents(to_buffer, self.folder[article-1])
        if test_mode:
            return self.group_name, article
        return lisp.cons(self.group_name, article)

    def request_update_mark(self, article, mark):
        character = chr(mark)
        if character in 'rR':
            character = 'E'
        self.marks[article-1] = character
        return ord(character)

    def request_replace_article(self, article, buffer):
        let = Let().push_excursion()
        lisp.set_buffer(buffer)
        self.folder[article-1] = lisp.buffer_string()
        self.marks[article-1] = ' '
        return OK

### Required back End Functions.

server_registry = {}

def retrieve_headers(articles, group=None, server=None, fetch_old=None):
    debug('RETRIEVE_HEADERS', 'articles', 'group', 'server', 'fetch_old')
    try:
        return server_registry[server].retrieve_headers(
            articles, group, fetch_old)
    except Error:
        pass

def open_server(server, definitions=None):
    debug('OPEN_SERVER', 'server', 'definitions')
    if server in server_registry:
        return OK
    try:
        server_registry[server] = Server(server, definitions)
        return OK
    except Error:
        pass

def close_server(server=None):
    debug('CLOSE_SERVER', 'server')
    del server_registry[server]
    return OK

def request_close():
    debug('REQUEST_CLOSE')
    result = OK
    for server in server_registry.keys():
        if close_server(server) is None:
            result = None
    return result

def server_opened(server=None):
    debug('SERVER_OPENED', 'server')
    if server in server_registry:
        return OK

def status_message(server=None):
    debug('STATUS_MESSAGE', 'server')
    return server_registry[server].status

def request_article(article, group=None, server=None, to_buffer=None):
    debug('REQUEST_ARTICLE', 'article', 'group', 'server', 'to_buffer')
    try:
        return server_registry[server].request_article(
            article, group, to_buffer)
    except Error:
        pass

def request_group(group, server=None, fast=None):
    debug('REQUEST_GROUP', 'group', 'server', 'fast')
    try:
        return server_registry[server].request_group(group, fast)
    except Error:
        pass

def close_group(group, server=None):
    debug('CLOSE_GROUP', 'group', 'server')
    try:
        return server_registry[server].close_group(group)
    except Error:
        pass

def request_list(server=None):
    debug('REQUEST_LIST', 'server')

    # Return a list of all groups available on SERVER.  And that means
    # _all_.

    # Here's an example from a server that only carries two groups:

    #      ifi.test 0000002200 0000002000 y
    #      ifi.discussion 3324 3300 n

    # On each line we have a group name, then the highest article number
    # in that group, the lowest article number, and finally a flag.

    #      active-file = *active-line
    #      active-line = name " " <number> " " <number> " " flags eol
    #      name        = <string>
    #      flags       = "n" / "y" / "m" / "x" / "j" / "=" name

    # The flag says whether the group is read-only (`n'), is moderated
    # (`m'), is dead (`x'), is aliased to some other group (`=other-group')
    # or none of the above (`y').

    report('request_list not implemented.')

def request_post(server=None):
    debug('REQUEST_POST', 'server')

    # This function should post the current buffer.  It might return whether
    # the posting was successful or not, but that's not required.  If, for
    # instance, the posting is done asynchronously, it has generally not
    # been completed by the time this function concludes.  In that case,
    # this function should set up some kind of sentinel to beep the user
    # loud and clear if the posting could not be completed.

    # There should be no result data from this function.

    report('request_post not implemented.')

### Optional Back End Functions

def retrieve_groups(groups, server=None):
    debug('RETRIEVE_GROUPS', 'groups', 'server')

    # GROUPS is a list of groups, and this function should request data on
    # all those groups.  How it does it is of no concern to Gnus, but it
    # should attempt to do this in a speedy fashion.

    # The return value of this function can be either `active' or `group',
    # which says what the format of the result data is.  The former is in
    # the same format as the data from `nnchoke-request-list', while the
    # latter is a buffer full of lines in the same format as
    # `nnchoke-request-group' gives.

    #      group-buffer = *active-line / *group-status

    report('retrieve_groups not implemented.')

def request_update_info(group, info, server=None):
    debug('REQUEST_UPDATE_INFO', 'group', 'info', 'server')

    # A Gnus group info (*note Group Info::) is handed to the back end for
    # alterations.  This comes in handy if the back end really carries all
    # the information (as is the case with virtual and imap groups).  This
    # function should destructively alter the info to suit its needs, and
    # should return the (altered) group info.

    # There should be no result data from this function.

    report('request_update_info not implemented.')

def request_type(group, article=None):
    debug('REQUEST_TYPE', 'group', 'article')

    # When the user issues commands for "sending news" (`F' in the summary
    # buffer, for instance), Gnus has to know whether the article the user
    # is following up on is news or mail.  This function should return
    # `news' if ARTICLE in GROUP is news, `mail' if it is mail and `unknown'
    # if the type can't be decided.  (The ARTICLE parameter is necessary in
    # `nnvirtual' groups which might very well combine mail groups and news
    # groups.)  Both GROUP and ARTICLE may be `nil'.

    # There should be no result data from this function.

    report('request_type not implemented.')

def request_set_mark(group, action, server=None):
    debug('REQUEST_SET_MARK', 'group', 'action', 'server')

    # Set/remove/add marks on articles.  Normally Gnus handles the article
    # marks (such as read, ticked, expired etc) internally, and store them
    # in `~/.newsrc.eld'.  Some back ends (such as IMAP) however carry all
    # information about the articles on the server, so Gnus need to
    # propagate the mark information to the server.

    # ACTION is a list of mark setting requests, having this format:

    #      (RANGE ACTION MARK)

    # Range is a range of articles you wish to update marks on.  Action is
    # `set', `add' or `del', respectively used for removing all existing
    # marks and setting them as specified, adding (preserving the marks not
    # mentioned) mark and removing (preserving the marks not mentioned)
    # marks.  Mark is a list of marks; where each mark is a symbol.
    # Currently used marks are `read', `tick', `reply', `expire', `killed',
    # `dormant', `save', `download' and `unsend', but your back end should,
    # if possible, not limit itself to these.

    # Given contradictory actions, the last action in the list should be the
    # effective one.  That is, if your action contains a request to add the
    # `tick' mark on article 1 and, later in the list, a request to remove
    # the mark on the same article, the mark should in fact be removed.

    # An example action list:

    #      (((5 12 30) 'del '(tick))
    #       ((10 . 90) 'add '(read expire))
    #       ((92 94) 'del '(read)))

    # The function should return a range of articles it wasn't able to set
    # the mark on (currently not used for anything).

    # There should be no result data from this function.

    report('request_set_mark not implemented.')

def request_update_mark(group, article, mark):
    debug('REQUEST_UPDATE_MARK', 'group', 'article', 'mark')
    try:
        if len(server_registry) == 1:
            server = server_registry.keys()[0]
        else:
            # REVOIR: On doit pouvoir faire mieux, j'imagine...
            lisp.error("Ambiguous server.")
        return server_registry[server].request_update_mark(
            group, article, mark)
    except Error:
        pass

def request_scan(group=None, server=None):
    debug('REQUEST_SCAN', 'group', 'server')
    try:
        return server_registry[server].request_scan(group)
    except Error:
        pass

def request_group_description(group, server=None):
    debug('REQUEST_GROUP_DESCRIPTION', 'group', 'server')

    # The result data from this function should be a description of GROUP.

    #      description-line = name <TAB> description eol
    #      name             = <string>
    #      description      = <text>

    report('request_group_description not implemented.')

def request_list_newsgroups(server=None):
    debug('REQUEST_LIST_NEWSGROUPS', 'server')

    # The result data from this function should be the description of all
    # groups available on the server.

    #      description-buffer = *description-line

    report('request_list_newsgroups not implemented.')

def request_newgroups(date, server=None):
    debug('REQUEST_NEWGROUPS', 'date', 'server')

    # The result data from this function should be all groups that were
    # created after `date', which is in normal human-readable date format.
    # The data should be in the active buffer format.

    report('request_newgroups not implemented.')

def request_create_group(group, server=None):
    debug('REQUEST_CREATE_GROUP', 'group', 'server')

    # This function should create an empty group with name GROUP.

    # There should be no return data.

    report('request_create_group not implemented.')

def request_expire_articles(articles, group=None, server=None, force=None):
    debug('REQUEST_EXPIRE_ARTICLES', 'articles', 'group', 'server', 'force')

    # This function should run the expiry process on all articles in the
    # ARTICLES range (which is currently a simple list of article numbers.)
    # It is left up to the back end to decide how old articles should be
    # before they are removed by this function.  If FORCE is non-`nil', all
    # ARTICLES should be deleted, no matter how new they are.

    # This function should return a list of articles that it did not/was not
    # able to delete.

    # There should be no result data returned.

    report('request_expire_articles not implemented.')

def request_move_article(article, group, server, accept_form, last=None):
    debug('REQUEST_MOVE_ARTICLE', 'article', 'group', 'server',
          'accept_form', 'last')

    # This function should move ARTICLE (which is a number) from GROUP
    # by calling ACCEPT-FORM.

    # This function should ready the article in question for moving by
    # removing any header lines it has added to the article, and generally
    # should "tidy up" the article.  Then it should `eval' ACCEPT-FORM in
    # the buffer where the "tidy" article is.  This will do the actual
    # copying.  If this `eval' returns a non-`nil' value, the article should
    # be removed.

    # If LAST is `nil', that means that there is a high likelihood that
    # there will be more requests issued shortly, so that allows some
    # optimizations.

    # The function should return a cons where the `car' is the group name
    # and the `cdr' is the article number that the article was entered as.

    # There should be no data returned.

    report('request_move_article not implemented.')

def request_accept_article(group, server=None, last=None):
    debug('REQUEST_ACCEPT_ARTICLE', 'group', 'server', 'last')

    # This function takes the current buffer and inserts it into GROUP.  If
    # LAST in `nil', that means that there will be more calls to this
    # function in short order.

    # The function should return a cons where the `car' is the group name
    # and the `cdr' is the article number that the article was entered as.

    # There should be no data returned.

    report('request_accept_article not implemented.')

def request_replace_article(article, group, buffer):
    debug('REQUEST_REPLACE_ARTICLE', 'article', 'group', 'buffer')
    assert len(server_registry) == 1
    server = server_registry.keys()[0]
    return server_registry[server].request_replace_article(
        article, group, buffer)

def request_delete_group(group, force, server=None):
    debug('REQUEST_DELETE_GROUP', 'group', 'force', 'server')

    # This function should delete GROUP.  If FORCE, it should really delete
    # all the articles in the group, and then delete the group itself.  (If
    # there is such a thing as "the group itself".)

    # There should be no data returned.

    report('request_delete_group not implemented.')

def request_rename_group(group, new_name, server=None):
    debug('REQUEST_RENAME_GROUP', 'group', 'new_name', 'server')

    # This function should rename GROUP into NEW-NAME.  All articles in
    # GROUP should move to NEW-NAME.

    # There should be no data returned.

    report('request_rename_group not implemented.')

### Service routines.

def report(message):
    # Register an error message with Gnus.  The function using `report'
    # should then return None, to signal Gnus that an error occurred.
    if test_mode:
        debug('REPORT', 'message')
    else:
        lisp.nnheader_report(lisp.nncourriel, message)

def pymacs_load_hook():
    # Initialise for Emacs communications.
    if (lisp.assoc('nncourriel', lisp.gnus_valid_select_methods.value())
        is None):
        lisp.gnus_declare_backend('nncourriel', 'mail', 'respool', 'address')
    lisp.provide(lisp.nncourriel)
    global debug
    debug = Debug('/tmp/nncourriel-debug')

def main(*arguments):
    # Just for debugging.  This function has no interesting code.
    server = Server('', None)
    assert len(arguments) == 1
    import os
    name = os.path.join(os.getcwd(), arguments[0])
    group = name[1:].replace('/', '.').replace('@', '.')
    print '*', group
    server.request_group(group, False)
    count = len(server.group_registry[group].folder)
    print '*', count, 'articles'
    server.retrieve_headers(range(1, count+1), group, None)
    for article in range(1, count+1):
        print '***', article
        server.request_article(article, group, None)

if __name__ == '__main__':
    # Just for debugging.  This module is not intended as a script.
    test_mode = True
    debug = Debug()
    import sys
    main(*sys.argv[1:])

# Local Variables:
# pymacs-auto-reload: t
# End:
