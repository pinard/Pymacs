;;; Interface between Emacs LISP and Python - LISP part.
;;; Copyright © 2001 Progiciels Bourbeau-Pinard inc.
;;; François Pinard <pinard@iro.umontreal.ca>, 2001.

;;; See the Pymacs documentation for more information.

;;; Published functions.

(defvar pymacs-trace-transit nil
  "Keep the communication buffer growing, for debugging.
When this variable is nil, the `*Pymacs*' communication buffer gets erased
before each communication round-trip.  Setting it to `t' guarantees that
the full communication is saved, which is useful for debugging.")

(defvar pymacs-mutable-strings nil
  "Transmitting LISP strings to Python as opaque handles.
When this variable is nil, strings are transmitted as copies, and the
Python side thus has no way for modifying the original LISP strings.")

(defun python-import (module &optional prefix)
  "Import the Python module named MODULE into Emacs.
Each function in the Python module is made available as an Emacs function.
The LISP name of each function is the concatenation of PREFIX with
the Python name, in which underlines are replaced by dashes.  If PREFIX is
not given, it default to MODULE followed by a dash."
  (interactive
   (let* ((module (read-string "Python module? "))
	  (default (concat module "-"))
	  (prefix (read-string (format "Prefix? [%s] " default)
			       nil nil default)))
     (list module prefix)))
  (unless prefix
    (setq prefix (concat module "-")))
  (message "Importing %s..." module)
  (let ((value (python-apply "import_to_lisp" (list module prefix))))
    (unless value
      (error "Importing %s...failed" module))
    (eval value)
    (message "Importing %s...done" module)))

(defun python-eval (text)
  "Compile TEXT as a Python expression, and return its value."
  (interactive "sPython expression? ")
  (let ((value (python-apply "eval" (list text))))
    (when (interactive-p)
      (message "%S" value))
    value))

(defun python-exec (text)
  "Compile and execute TEXT as a sequence of Python statements.
This functionality is experimental, and does not appear to be useful."
  (interactive "sPython statements? ")
  (let ((value (pymacs-serve-until-reply
		`(progn (princ "exec ") (prin1 ,text)))))
    (when (interactive-p)
      (message "%S" value))
    value))

(defun python-apply (function arguments)
  "Return the result of calling a Python function FUNCTION over ARGUMENTS.
FUNCTION is a string denoting the Python function, ARGUMENTS is a list of
LISP expressions.  Immutable LISP constants are converted to Python
equivalents, other structures are converted into LISP handles."
  (pymacs-serve-until-reply `(pymacs-print-for-apply ',function ',arguments)))

;;; Interface for load-file, autoload, etc.

;; This function is very experimental -- it does not even work! :-)

(defun pymacs-file-handler (operation &rest arguments)
  ;; Emacs might want the contents of some `MODULE.el' which does not exist,
  ;; while there is a `MODULE.py' or `MODULE.pyc' file in the same directory.
  ;; The goal is to generate a virtual contents for this `MODULE.el' file, as
  ;; a set of LISP trampoline functions to the Python module functions.
  ;; Python modules can then be loaded or autoloaded as if they were LISP.
  (message "** %S %S" operation arguments)
  (cond ((and (eq operation 'file-readable-p)
	      (let ((module (substring (car arguments) 0 -3)))
		(or (pymacs-file-force operation arguments)
		    (file-readable-p (concat module ".py"))
		    (file-readable-p (concat module ".pyc"))))))
	((and (eq operation 'load)
	      (not (pymacs-file-force
		    'file-readable-p (list (car arguments))))
	      (file-readable-p (car arguments)))
	 (let ((lisp-code (python-apply
			   "import_to_lisp"
			   (list (substring (car arguments) 0 -3) nil))))
	   (unless lisp-code
	     (error "Python import error"))
	   (eval lisp-code)))
	((and (eq operation 'insert-file-contents)
	      (not (pymacs-file-force
		    'file-readable-p (list (car arguments))))
	      (file-readable-p (car arguments)))
	 (let ((lisp-code (python-apply
			   "import_to_lisp"
			   (list (substring (car arguments) 0 -3) nil))))
	   (unless lisp-code
	     (error "Python import error"))
	   (insert lisp-code)))
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
;; Python to LISP direction.  This is followed by a decimal number given the
;; length of the message text, a TAB character, and the message text itself.
;; Message direction alternates systematically between messages, it never
;; occurs that two successive messages are sent in the same direction.  The
;; very first message is received from the Python side, and reads `(started)`.

(defun pymacs-start-services ()
  ;; This function gets called automatically, as needed.  However, it is
  ;; marked interactive as a debugging convenience to reload a new copy of the
  ;; Python process, after having changed the Python code.
  (interactive)
  (let ((name "*Pymacs*"))
    (when (get-buffer name)
      (kill-buffer name))
    (setq pymacs-transit-buffer (get-buffer-create name)))
  (with-current-buffer pymacs-transit-buffer
    (let ((process (start-process "pymacs" pymacs-transit-buffer
				  "pymacs-services")))
      (process-kill-without-query process)
      (while (save-excursion
	       (goto-char (point-min))
	       (not (search-forward "<9\t(started)" nil t)))
	(accept-process-output process))))
  (when pymacs-trace-transit
    (pop-to-buffer pymacs-transit-buffer)
    (sit-for 0)))

(defun pymacs-terminate-services ()
  ;; This function is provided for completeness.  It is not really needed.
  (when pymacs-transit-buffer
    (kill-buffer pymacs-transit-buffer)
    (setq pymacs-transit-buffer nil)))

(defun pymacs-serve-until-reply (inserter)
  ;; This function evals INSERTER to print a Python request.  It sends it to
  ;; the Python sub-process, and serves all sub-requests coming from the
  ;; Python side, until either a reply or an error is finally received.
  (unless (and pymacs-transit-buffer
	       (buffer-name pymacs-transit-buffer)
	       (get-buffer-process pymacs-transit-buffer))
    (pymacs-start-services))
  (let (done value)
    (while (not done)
      (let ((reply (condition-case info
		       (eval (pymacs-round-trip inserter))
		     (error (cons 'pymacs-oops (prin1-to-string info))))))
	(cond ((eq (car reply) 'pymacs-reply)
	       (setq done t
		     value (cdr reply)))
	      ((eq (car reply) 'pymacs-error)
	       (error "Python: %s" (cdr reply)))
	      ((eq (car reply) 'pymacs-oops)
	       (setq inserter `(pymacs-print-for-apply 'error ',(cdr reply))))
	      ((eq (car reply) 'pymacs-expand)
	       (setq inserter `(pymacs-print-for-apply-expanded
				'reply ,(cdr reply))))
	      (t (setq inserter `(pymacs-print-for-apply 'reply ',reply))))))
    value))

(defun pymacs-reply (expression)
  ;; This pseudo-function returns `(pymacs-reply . EXPRESSION)'.
  ;; `serve-until-reply' recognises this form when returned.
  (cons 'pymacs-reply expression))

(defun pymacs-error (expression)
  ;; This pseudo-function returns `(pymacs-error . EXPRESSION)'.
  ;; `serve-until-reply' recognises this form when returned.
  (cons 'pymacs-error expression))

(defun pymacs-expand (expression)
  ;; This pseudo-function returns `(pymacs-expand . EXPRESSION)'.
  ;; `serve-until-reply' recognises this form when returned.
  (cons 'pymacs-expand expression))

(defun pymacs-round-trip (inserter)
  ;; This function evals INSERTER to print a Python request.  It sends it to
  ;; the Python sub-process, and await for any kind of reply.
  (save-excursion
    (set-buffer pymacs-transit-buffer)
    (unless pymacs-trace-transit
      (erase-buffer))
    (let* ((process (get-buffer-process pymacs-transit-buffer))
	   (marker (process-mark process))
	   send-position reply-position)
      (goto-char marker)
      (unless (= (preceding-char) ?\n)
	(princ "\n" marker))
      ;; Encode request.
      (setq send-position (marker-position marker))
      (let ((standard-output marker))
	(eval inserter))
      (goto-char marker)
      (unless (= (preceding-char) ?\n)
	(princ "\n" marker))
      ;; Send request.
      (goto-char send-position)
      (insert (format ">%d\t" (- marker send-position)))
      (setq reply-position (marker-position marker))
      (process-send-region process send-position marker)
      ;; Receive reply.
      (while (progn
	       (goto-char reply-position)
	       (not (re-search-forward "^<\\([0-9]+\\)\t" nil t)))
	(accept-process-output process))
      (let ((limit-position (+ (match-end 0)
			       (string-to-number (match-string 1)))))
	(while (< (marker-position marker) limit-position)
	  (accept-process-output process))))
    ;; Return decoded reply.
    (goto-char (match-end 0))
    (read (current-buffer))))

;;; Generating Python code.

;; Many LISP expressions cannot fully be represented in Python, at least
;; because the object is mutable on the LISP side.  Such objects are allocated
;; somewhere into a vector of handles, and the handle ordinal is used for
;; communication instead of the expression itself.
(defvar pymacs-handles nil
  "Vector of handles to hold transmitted expressions.")
(defvar pymacs-freed-list nil
  "List of unallocated indices in HANDLE-VECTOR.")

;; When the Python CG is done with a LISP object, a special communication
;; occurs so to free the object on the LISP side as well.  I did not find a
;; way to do it the other way around, however.  So I'm not transmitting opaque
;; Python objects to LISP.  Since these do not really miss me in LISP, this is
;; not a problem in practice.  Yet, it would be nicer (for the elegance of
;; symmetry) if LISP was offering me a mean to know when a dead object is
;; about to be garbage-collected.  On the LISP flavours I know, there is
;; Gambit which has the concept of associating a "will" to an object, the GC
;; executes that will before reclaiming the object.  But even if EMACS had
;; wills, it would require great care to use them, as I use synchronous
;; message round-trips for the communication protocol, while the Emacs GC is
;; rather asynchronous. :-)

(defun pymacs-allocate-handle (expression)
  ;; This function allocates some handle for an EXPRESSION, and return its
  ;; ordinal.
  (unless pymacs-freed-list
    (let* ((previous pymacs-handles)
	   (old-size (length previous))
	   (new-size (if (zerop old-size) 100 (+ old-size (/ old-size 2))))
	   (counter 0))
      (setq pymacs-handles (make-vector new-size nil))
      (while (< counter new-size)
	(if (< counter old-size)
	    (aset pymacs-handles counter (aref previous counter))
	  (setq pymacs-freed-list (cons counter pymacs-freed-list)))
	(setq counter (1+ counter)))))
  (let ((number (car pymacs-freed-list)))
    (setq pymacs-freed-list (cdr pymacs-freed-list))
    (aset pymacs-handles number expression)
    number))

(defun pymacs-free-handle (number)
  ;; This function is triggered from Python side whenever a LISP handle looses
  ;; its last reference.  The reference should be cut on the LISP side as
  ;; well, or else, the object will never be garbage-collected.
  (aset pymacs-handles number nil)
  (setq pymacs-freed-list (cons number pymacs-freed-list))
  ;; Avoid transmitting back useless information.
  nil)

(defun pymacs-handle-length (number)
  ;; This function supports Python `len(HANDLE)'.
  (let ((handle (aref pymacs-handles number)))
    (cond ((arrayp handle) (length handle))
	  ((listp handle) (length handle))
	  (t 0))))

(defun pymacs-handle-ref (number key)
  ;; This function supports Python `HANDLE[KEY]'.
  (let ((handle (aref pymacs-handles number)))
    (cond ((arrayp handle) (aref handle key))
	  ((listp handle) (nth key handle)))))

(defun pymacs-handle-set (number key value)
  ;; This function supports Python `HANDLE[KEY] = VALUE'.
  (let ((handle (aref pymacs-handles number)))
    (cond ((arrayp handle) (aset handle key value))
	  ((listp handle) (setcar (nthcdr key handle) value)))))

(defun pymacs-print-for-apply (function arguments)
  ;; This function prints a Python expression calling FUNCTION, which is
  ;; a string, over all its ARGUMENTS, which are LISP expressions.
  (let ((separator "")
	argument)
    (princ function)
    (princ "(")
    (while arguments
      (setq argument (car arguments)
	    arguments (cdr arguments))
      (princ separator)
      (setq separator ", ")
      (pymacs-print-for-eval argument))
    (princ ")")))

(defun pymacs-print-for-apply-expanded (function arguments)
  ;; This function acts like `print-for-apply', except that it uses
  ;; `print-for-eval-expanded' (which sees) insteaad of `print-for-eval'.
  (let ((separator "")
	argument)
    (princ function)
    (princ "(")
    (while arguments
      (setq argument (car arguments)
	    arguments (cdr arguments))
      (princ separator)
      (setq separator ", ")
      (pymacs-print-for-eval-expanded argument))
    (princ ")")))

(defun pymacs-print-for-eval (expression)
  ;; This function prints a Python expression out of a LISP EXPRESSION.
  (cond ((not expression) (princ "None"))
	((numberp expression) (princ expression))
	((and (not pymacs-mutable-strings) (stringp expression))
	 (prin1 expression))
	((symbolp expression)
	 (let ((name (symbol-name expression)))
	   (cond ((string-match "^[A-Za-z][-A-Za-z0-9]*$"  name)
		  (princ "lisp.")
		  (princ (replace-regexp-in-string "-" "_" name t t)))
		 (t (princ "sym[")
		    (prin1 (prin1-to-string (symbol-name expression)))
		    (princ "]")))))
	(t (princ "Handle(")
	   (princ (pymacs-allocate-handle expression))
	   (princ ")"))))

(defun pymacs-print-for-eval-expanded (expression)
  ;; This function prepares a Python expression that will reproduce a copy
  ;; of EXPRESSION, as much as possible, instead of producing an handle.
  ;; Proper lists are turned into tuples, vectors are turned into lists.
  (cond ((not expression) (princ "None"))
	((stringp expression) (prin1 expression))
	((vectorp expression)
	 (let ((limit (length expression))
	       (counter 0))
	   (princ "[")
	   (while (< counter limit)
	     (unless (zerop counter)
	       (princ ", "))
	     (pymacs-print-expanded (aref expression counter)))
	   (princ "]")))
	((listp expression)
	 (let ((single (= (length expression) 1)))
	   (princ "(")
	   (pymacs-print-expanded (car expression))
	   (while (setq expression (cdr expression))
	     (princ ", ")
	     (pymacs-print-expanded (car expression)))
	   (when single
	     (princ ", "))
	   (princ ")")))
	((consp expression)
	 (princ "Dotted(")
	 (pymacs-print-expanded (car expression))
	 (while (consp (cdr expression))
	   (princ ", ")
	   (setq expression (cdr expression))
	   (pymacs-print-expanded (car expression)))
	 (princ ", ")
	 (pymacs-print-expanded (cdr expression))
	 (princ ")"))
	(t (pymacs-print-for-eval expression))))

;(autoload 'essai-test "essai")

(defun test-pymacs ()
  ;; Test function to play with! :-)
  (interactive)
  (setq pymacs-handles nil
	pymacs-freed-list nil)
  (let ((pymacs-trace-transit t)
	bonjour)
    (pymacs-terminate-services)
    (python-import "essai")
    (setq bonjour '(allo))
    (message "%S" (essai-test bonjour))
    (end-of-buffer)
    (recenter -1)))

(provide 'pymacs)
