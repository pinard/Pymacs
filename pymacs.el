;;; Interface between Emacs LISP and Python - LISP part.
;;; Copyright © 2001 Progiciels Bourbeau-Pinard inc.
;;; François Pinard <pinard@iro.umontreal.ca>, 2001.

;;; See the Pymacs documentation for more information.

;;; Published functions.

(defvar pymacs-load-path nil
  "List of additional directories to search for Python modules.
The directories listed will be searched first, in the order given.")

(defvar pymacs-trace-transit nil
  "Keep the communication buffer growing, for debugging.
When this variable is nil, the `*Pymacs*' communication buffer gets erased
before each communication round-trip.  Setting it to `t' guarantees that
the full communication is saved, which is useful for debugging.")

(defvar pymacs-forget-mutability nil
  "Transmit copies to Python instead of LISP handles, as much as possible.
When this variable is nil, most mutable objects are transmitted as handles.
This variable is meant to be temporarily rebound to force copies.")

(defvar pymacs-mutable-strings nil
  "Prefer transmitting LISP strings to Python as handles.
When this variable is nil, strings are transmitted as copies, and the
Python side thus has no way for modifying the original LISP strings.
This variable is ignored whenever `forget-mutability' is set.")

(defun pymacs-load (module &optional prefix noerror)
  "Import the Python module named MODULE into Emacs.
Each function in the Python module is made available as an Emacs function.
The LISP name of each function is the concatenation of PREFIX with
the Python name, in which underlines are replaced by dashes.  If PREFIX is
not given, it defaults to MODULE followed by a dash.
If NOERROR is not nil, do not raise error when the module is not found."
  (interactive
   (let* ((module (read-string "Python module? "))
	  (default (concat module "-"))
	  (prefix (read-string (format "Prefix? [%s] " default)
			       nil nil default)))
     (list module prefix)))
  (message "Pymacs loading %s..." module)
  (let ((lisp-code (pymacs-apply "pymacs_load_helper" (list module prefix))))
    (cond (lisp-code (let ((result (eval lisp-code)))
		       (message "Pymacs loading %s...done" module)
		       result))
	  (noerror (message "Pymacs loading %s...failed" module) nil)
	  (t (error "Pymacs loading %s...failed" module)))))

(defun pymacs-eval (text)
  "Compile TEXT as a Python expression, and return its value."
  (interactive "sPython expression? ")
  (let ((value (pymacs-apply "eval" (list text))))
    (when (interactive-p)
      (message "%S" value))
    value))

(defun pymacs-exec (text)
  "Compile and execute TEXT as a sequence of Python statements.
This functionality is experimental, and does not appear to be useful."
  (interactive "sPython statements? ")
  (let ((value (pymacs-serve-until-reply
		`(progn (princ "exec ") (prin1 ,text)))))
    (when (interactive-p)
      (message "%S" value))
    value))

(defun pymacs-apply (function arguments)
  "Return the result of calling a Python function FUNCTION over ARGUMENTS.
FUNCTION is a string denoting the Python function, ARGUMENTS is a list of
LISP expressions.  Immutable LISP constants are converted to Python
equivalents, other structures are converted into LISP handles."
  (pymacs-serve-until-reply `(pymacs-print-for-apply ',function ',arguments)))

;;; Integration details.

;; Python functions and modules should ideally look like LISP functions and
;; modules.  This page tries to increase the integration seamlessness.

(defadvice documentation (around pymacs-ad-documentation activate)
  ;; Integration of doc-strings.
  (let ((python-doc (let ((reference (pymacs-python-reference function)))
		      (when reference
			(pymacs-eval (format "doc_string(%s)" reference))))))
    (if python-doc
	(setq ad-return-value
	      (concat
	       "It interfaces to a Python function.\n\n"
	       (if raw python-doc (substitute-command-keys python-doc))))
      ad-do-it)))

(defun pymacs-python-reference (object)
  ;; Return the text reference of a Python object if possible, else nil.
  (cond ((eq (car-safe object) 'pymacs-python)
	 (format "python[%d]" (cdr object)))
	((functionp object)
	 (let* ((definition (indirect-function object))
		(body (and (eq (car-safe definition) 'lambda)
			   (cddr definition))))
	   (and body
		(= (length (cddr definition)) 1)
		(eq (caar body) 'pymacs-apply)
		(cadr (car body)))))))

;; The following functions are experimental -- they are not satisfactory yet.

(defun pymacs-file-handler (operation &rest arguments)
  ;; Integration of load-file, autoload, etc.
  ;; Emacs might want the contents of some `MODULE.el' which does not exist,
  ;; while there is a `MODULE.py' or `MODULE.pyc' file in the same directory.
  ;; The goal is to generate a virtual contents for this `MODULE.el' file, as
  ;; a set of LISP trampoline functions to the Python module functions.
  ;; Python modules can then be loaded or autoloaded as if they were LISP.
  ;(message "** %S %S" operation arguments)
  (cond ((and (eq operation 'file-readable-p)
	      (let ((module (substring (car arguments) 0 -3)))
		(or (pymacs-file-force operation arguments)
		    (file-readable-p (concat module ".py"))
		    (file-readable-p (concat module ".pyc"))))))
	((and (eq operation 'load)
	      (not (pymacs-file-force
		    'file-readable-p (list (car arguments))))
	      (file-readable-p (car arguments)))
	 (let ((lisp-code (pymacs-apply
			   "pymacs_load_helper"
			   (list (substring (car arguments) 0 -3) nil))))
	   (unless lisp-code
	     (error "Python import error"))
	   (eval lisp-code)))
	((and (eq operation 'insert-file-contents)
	      (not (pymacs-file-force
		    'file-readable-p (list (car arguments))))
	      (file-readable-p (car arguments)))
	 (let ((lisp-code (pymacs-apply
			   "pymacs_load_helper"
			   (list (substring (car arguments) 0 -3) nil))))
	   (unless lisp-code
	     (error "Python import error"))
	   (insert (prin1-to-string lisp-code))))
	(t (pymacs-file-force operation arguments))))

(defun pymacs-file-force (operation arguments)
  ;; Bypass the file handler.
  (let ((inhibit-file-name-handlers
	 (cons 'pymacs-file-handler
	       (and (eq inhibit-file-name-operation operation)
		    inhibit-file-name-handlers)))
	(inhibit-file-name-operation operation))
    (apply operation arguments)))

;(add-to-list 'file-name-handler-alist '("\\.el\\'" . pymacs-file-handler))

;;; Gargabe collection of Python IDs.

;; Python objects which have no LISP representation are allocated on the
;; Python side as `python[INDEX]', and INDEX is transmitted to Emacs, with
;; the value to use on the LISP side for it.  Whenever LISP does not need a
;; Python object anymore, it should be freed on the Python side.  The
;; following variables and functions are meant to fill this duty.

(defvar pymacs-use-hash-tables nil
  "Automatically set to t if hash tables are available.")

(defvar pymacs-used-ids nil
  "List of received IDs, currently allocated on the Python side.")

(defvar pymacs-weak-hash nil
  "Weak hash table, meant to find out which IDs are still needed.")

(defvar pymacs-gc-wanted nil
  "Flag if it is time to clean up unused IDs on the Python side.")

(defvar pymacs-gc-running nil
  "Flag telling that a Pymacs garbage collection is in progress.")

(defvar pymacs-gc-timer nil
  "Timer to trigger Pymacs garbage collection at regular time intervals.
The timer is used only if `post-gc-hook' is not available.")

(defun pymacs-schedule-gc ()
  (unless pymacs-gc-running
    (setq pymacs-gc-wanted t)))

(defun pymacs-garbage-collect ()
  ;; Clean up unused IDs on the Python side.
  (when pymacs-use-hash-tables
    (let ((pymacs-gc-running t)
	  (pymacs-forget-mutability t)
	  (ids pymacs-used-ids)
	  used-ids unused-ids)
      (while ids
	(let ((id (car ids)))
	  (setq ids (cdr ids))
	  (if (gethash id pymacs-weak-hash)
	      (setq used-ids (cons id used-ids))
	    (setq unused-ids (cons id unused-ids)))))
      (setq pymacs-used-ids used-ids
	    pymacs-gc-wanted nil)
      (when unused-ids
	(pymacs-apply "free_python" unused-ids)))))

(defun pymacs-defuns (arguments)
  ;; Take one argument, a single list holding an even number of items.
  ;; The first argument is an INDEX, the second is a NAME, and so forth.
  ;; Register Python INDEX with a function with that NAME on the LISP side.
  ;; The strange calling convention is to minimise quoting at call time.
  (while (>= (length arguments) 2)
    (let ((index (car arguments))
	  (name (cadr arguments)))
      (fset name (pymacs-defun index))
      (setq arguments (cddr arguments)))))

(defun pymacs-defun (index)
  ;; Register INDEX on the LISP side with a Python object that is a function,
  ;; and return a lambda form calling that function.
  (let ((object (pymacs-python index)))
    `(lambda (&rest arguments) (pymacs-apply ',object arguments))))

(defun pymacs-python (index)
  ;; Register on the LISP side a Python object having INDEX, and return it.
  ;; The result is meant to be recognised specially by `print-for-eval', and
  ;; in the function position by `print-for-apply'.
  (let ((object (cons 'pymacs-python index)))
    (when pymacs-use-hash-tables
      (puthash index object pymacs-weak-hash)
      (setq pymacs-used-ids (cons index pymacs-used-ids)))
    object))

;;; Generating Python code.

;; Many LISP expressions cannot fully be represented in Python, at least
;; because the object is mutable on the LISP side.  Such objects are allocated
;; somewhere into a vector of handles, and the handle index is used for
;; communication instead of the expression itself.

(defvar pymacs-lisp nil
  "Vector of handles to hold transmitted expressions.")

(defvar pymacs-freed-list nil
  "List of unallocated indices in LISP.")

;; When the Python CG is done with a LISP object, a communication occurs so to
;; free the object on the LISP side as well.

(defun pymacs-allocate-lisp (expression)
  ;; This function allocates some handle for an EXPRESSION, and return its
  ;; index.
  (unless pymacs-freed-list
    (let* ((previous pymacs-lisp)
	   (old-size (length previous))
	   (new-size (if (zerop old-size) 100 (+ old-size (/ old-size 2))))
	   (counter new-size))
      (setq pymacs-lisp (make-vector new-size nil))
      (while (> counter 0)
	(setq counter (1- counter))
	(if (< counter old-size)
	    (aset pymacs-lisp counter (aref previous counter))
	  (setq pymacs-freed-list (cons counter pymacs-freed-list))))))
  (let ((index (car pymacs-freed-list)))
    (setq pymacs-freed-list (cdr pymacs-freed-list))
    (aset pymacs-lisp index expression)
    index))

(defun pymacs-free-lisp (&rest indices)
  ;; This function is triggered from Python side for LISP handles which lost
  ;; their last reference.  These references should be cut on the LISP side as
  ;; well, or else, the objects will never be garbage-collected.
  (while indices
    (let ((index (car indices)))
      (aset pymacs-lisp index nil)
      (setq pymacs-freed-list (cons index pymacs-freed-list)
	    indices (cdr indices)))))

(defun pymacs-print-for-apply-expanded (function arguments)
  ;; This function acts like `print-for-apply', but produce arguments which
  ;; are expanded copies whenever possible, instead of handles.  Proper lists
  ;; are turned into Python lists, vectors are turned into Python tuples.
  (let ((pymacs-forget-mutability t))
    (pymacs-print-for-apply function arguments)))

(defun pymacs-print-for-apply (function arguments)
  ;; This function prints a Python expression calling FUNCTION, which is a
  ;; string naming a Python function, or a Python reference, over all its
  ;; ARGUMENTS, which are LISP expressions.
  (let ((separator "")
	argument)
    (if (eq (car-safe function) 'pymacs-python)
	(princ (format "python[%d]" (cdr function)))
      (princ function))
    (princ "(")
    (while arguments
      (setq argument (car arguments)
	    arguments (cdr arguments))
      (princ separator)
      (setq separator ", ")
      (pymacs-print-for-eval argument))
    (princ ")")))

(defun pymacs-print-for-eval (expression)
  ;; This function prints a Python expression out of a LISP EXPRESSION.
  (let (done)
    (cond ((not expression)
	   (princ "None")
	   (setq done t))
	  ((numberp expression)
	   (princ expression)
	   (setq done t))
	  ((stringp expression)
	   (when (or pymacs-forget-mutability
		     (not pymacs-mutable-strings))
	     (let ((text (copy-sequence expression)))
	       (set-text-properties 0 (length text) nil text)
	       (princ (mapconcat 'identity
				 (split-string (prin1-to-string text) "\n")
				 "\\n")))
	     (setq done t)))
	  ((symbolp expression)
	   (let ((name (symbol-name expression)))
	     ;; The symbol can only be transmitted when in the main oblist.
	     (when (eq expression (intern-soft name))
	       (cond
		((save-match-data
		   (string-match "^[A-Za-z][-A-Za-z0-9]*$" name))
		 (princ "lisp.")
		 (princ (mapconcat 'identity (split-string name "-") "_")))
		(t (princ "lisp[")
		   (prin1 name)
		   (princ "]")))
	       (setq done t))))
	  ((vectorp expression)
	   (when pymacs-forget-mutability
	     (let ((limit (length expression))
		   (counter 0))
	       (princ "(")
	       (while (< counter limit)
		 (unless (zerop counter)
		   (princ ", "))
		 (pymacs-print-for-eval (aref expression counter)))
	       (when (= limit 1)
		 (princ ","))
	       (princ ")")
	       (setq done t))))
	  ((eq (car-safe expression) 'pymacs-python)
	   (princ "python[")
	   (princ (cdr expression))
	   (princ "]"))
	  ((pymacs-proper-list-p expression)
	   (when pymacs-forget-mutability
	     (princ "[")
	     (pymacs-print-for-eval (car expression))
	     (while (setq expression (cdr expression))
	       (princ ", ")
	       (pymacs-print-for-eval (car expression)))
	     (princ "]")
	     (setq done t))))
    (unless done
      (let ((class (cond ((vectorp expression) "Vector")
			 ((and pymacs-use-hash-tables
			       (hash-table-p expression))
			  "Table")
			 ((bufferp expression) "Buffer")
			 ((pymacs-proper-list-p expression) "List")
			 (t "Lisp"))))
	(princ class)
	(princ "(")
	(princ (pymacs-allocate-lisp expression))
	(princ ")")))))

;;; Communication protocol.

(defvar pymacs-transit-buffer nil
  "Communication buffer between Emacs and Python.")

;; The principle behind the communication protocol is that it is easier to
;; generate than parse, and that each language already has its own parser.
;; So, the Emacs side generates Python text for the Python side to interpret,
;; while the Python side generates LISP text for the LISP side to interpret.
;; About nothing but expressions are transmitted, which are evaluated on
;; arrival.  The pseudo `reply' function is meant to signal the final result
;; of a series of exchanges following a request, while the pseudo `error'
;; function is meant to explain why an exchange could not have been completed.

;; The protocol itself is rather simple, and contains human readable text
;; only.  A message starts at the beginning of a line in the communication
;; buffer, either with `>' for the LISP to Python direction, or `<' for the
;; Python to LISP direction.  This is followed by a decimal number giving the
;; length of the message text, a TAB character, and the message text itself.
;; Message direction alternates systematically between messages, it never
;; occurs that two successive messages are sent in the same direction.  The
;; first message is received from the Python side, it is `(version VERSION)'.

(defun pymacs-start-services ()
  ;; This function gets called automatically, as needed.
  (let ((buffer (get-buffer-create "*Pymacs*")))
    (with-current-buffer buffer
      (save-match-data
	;; Launch the Python helper.
	(let ((process (apply 'start-process "pymacs" buffer "pymacs-services"
			      (mapcar 'expand-file-name pymacs-load-path))))
	  (process-kill-without-query process)
	  ;; Receive the synchronising reply.
	  (while (progn
		   (goto-char (point-min))
		   (not (re-search-forward "<\\([0-9]+\\)\t" nil t)))
	    (unless (accept-process-output process 5)
	      (error "Pymacs helper did not start within 5 seconds.")))
	  (let ((marker (process-mark process))
		(limit-position (+ (match-end 0)
				   (string-to-number (match-string 1)))))
	    (while (< (marker-position marker) limit-position)
	      (unless (accept-process-output process 5)
		(error "Pymacs helper probably was interrupted at start.")))))
	;; Check that synchronisation occurred.
	(goto-char (match-end 0))
	(let ((reply (read (current-buffer))))
	  (if (and (pymacs-proper-list-p reply)
		   (= (length reply) 2)
		   (eq (car reply) 'pymacs-version))
	      (unless (string-equal (cadr reply) "@VERSION@")
		(error "Pymacs LISP version is @VERSION@, Python is %s."
		       (cadr reply)))
	    (error "Pymacs got an invalid initial reply.")))))
    (setq pymacs-use-hash-tables (and (fboundp 'make-hash-table)
				      (fboundp 'gethash)
				      (fboundp 'puthash)))
    (when pymacs-use-hash-tables
      (if pymacs-weak-hash
	  ;; A previous Pymacs session occurred in *this* Emacs session.  Some
	  ;; IDs may hang around, which do not correspond to anything on the
	  ;; Python side.  Python should not recycle such IDs for new objects.
	  (when pymacs-used-ids
	    (let ((pymacs-transit-buffer buffer)
		  (pymacs-forget-mutability t))
	      (pymacs-apply "zombie_python" pymacs-used-ids)))
	(setq pymacs-weak-hash (make-hash-table :weakness 'value)))
      (if (boundp 'post-gc-hook)
	  (add-hook 'post-gc-hook 'pymacs-schedule-gc)
	(setq pymacs-gc-timer (run-at-time 20 20 'pymacs-schedule-gc))))
    ;; If nothing failed, only then declare the Pymacs has started!
    (setq pymacs-transit-buffer buffer)))

(defun pymacs-terminate-services ()
  ;; This function is mainly provided for documentation purposes.
  (interactive)
  (garbage-collect)
  (pymacs-garbage-collect)
  (when (or (not pymacs-used-ids)
	    (yes-or-no-p "\
Killing the helper might create zombie objects.  Kill? "))
    (cond ((boundp 'post-gc-hook)
	   (remove-hook 'post-gc-hook 'pymacs-schedule-gc))
	  ((timerp pymacs-gc-timer)
	   (cancel-timer pymacs-gc-timer)))
    (when pymacs-transit-buffer
      (kill-buffer pymacs-transit-buffer))
    (setq pymacs-gc-running nil
	  pymacs-gc-timer nil
	  pymacs-transit-buffer nil
	  pymacs-lisp nil
	  pymacs-freed-list nil)))

(defun pymacs-serve-until-reply (inserter)
  ;; This function evals INSERTER to print a Python request.  It sends it to
  ;; the Python helper, and serves all sub-requests coming from the
  ;; Python side, until either a reply or an error is finally received.
  (unless (and pymacs-transit-buffer
	       (buffer-name pymacs-transit-buffer)
	       (get-buffer-process pymacs-transit-buffer))
    (pymacs-start-services))
  (when pymacs-gc-wanted
    (pymacs-garbage-collect))
  (let (done value)
    (while (not done)
      (let* ((text (pymacs-round-trip inserter))
	     (reply (condition-case info
			(eval text)
		      (error (cons 'pymacs-oops (prin1-to-string info))))))
	(cond ((not (consp reply))
	       (setq inserter
		     `(pymacs-print-for-apply 'reply '(,reply))))
	      ((eq 'pymacs-reply (car reply))
	       (setq done t value (cdr reply)))
	      ((eq 'pymacs-error (car reply))
	       (error "Python: %s" (cdr reply)))
	      ((eq 'pymacs-oops (car reply))
	       (setq inserter
		     `(pymacs-print-for-apply 'error '(,(cdr reply)))))
	      ((eq 'pymacs-expand (car reply))
	       (setq inserter
		     `(pymacs-print-for-apply-expanded 'reply
						       '(,(cdr reply)))))
	      (t (setq inserter
		       `(pymacs-print-for-apply 'reply '(,reply)))))))
    value))

(defun pymacs-reply (expression)
  ;; This pseudo-function returns `(pymacs-reply . EXPRESSION)'.
  ;; `serve-until-reply' later recognises this form.
  (cons 'pymacs-reply expression))

(defun pymacs-error (expression)
  ;; This pseudo-function returns `(pymacs-error . EXPRESSION)'.
  ;; `serve-until-reply' later recognises this form.
  (cons 'pymacs-error expression))

(defun pymacs-expand (expression)
  ;; This pseudo-function returns `(pymacs-expand . EXPRESSION)'.
  ;; `serve-until-reply' later recognises this form.
  (cons 'pymacs-expand expression))

(defun pymacs-round-trip (inserter)
  ;; This function evals INSERTER to print a Python request.  It sends it to
  ;; the Python helper, awaits for any kind of reply, and returns it.
  (with-current-buffer pymacs-transit-buffer
    (unless pymacs-trace-transit
      (erase-buffer))
    (let* ((process (get-buffer-process pymacs-transit-buffer))
	   (status (process-status process))
	   (marker (process-mark process))
	   (moving (= (point) marker))
	   send-position reply-position reply)
      (save-excursion
	(save-match-data
	  ;; Encode request.
	  (setq send-position (marker-position marker))
	  (let ((standard-output marker))
	    (eval inserter))
	  (goto-char marker)
	  (unless (= (preceding-char) ?\n)
	    (princ "\n" marker))
	  ;; Send request text.
	  (goto-char send-position)
	  (insert (format ">%d\t" (- marker send-position)))
	  (setq reply-position (marker-position marker))
	  (process-send-region process send-position marker)
	  ;; Receive reply text.
	  (while (and (eq status 'run)
		      (progn
			(goto-char reply-position)
			(not (re-search-forward "<\\([0-9]+\\)\t" nil t))))
	    (unless (accept-process-output process 4)
	      (setq status (process-status process))))
	  (when (eq status 'run)
	    (let ((limit-position (+ (match-end 0)
				     (string-to-number (match-string 1)))))
	      (while (and (eq status 'run)
			  (< (marker-position marker) limit-position))
		(unless (accept-process-output process 2)
		  (setq status (process-status process))))))
	  ;; Decode reply.
	  (if (not (eq status 'run))
	      (error "Pymacs helper status is `%S'." status)
	    (goto-char (match-end 0))
	    (setq reply (read (current-buffer))))))
      (when (and moving (not pymacs-trace-transit))
	(goto-char marker))
      reply)))

(defun pymacs-proper-list-p (expression)
  (cond ((not expression))
	((consp expression) (not (cdr (last expression))))))

(provide 'pymacs)
