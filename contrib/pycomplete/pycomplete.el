;;; Complete symbols at point using Pymacs.
;;; See pycomplete.py for the Python side of things and a short description
;;; of what to expect.

(require 'pymacs)
(require 'python-mode)

(pymacs-load "/home/jj/Projects/pymacs-2.0/extensions.pycomplete")

;;check if prev character is blank-type
(defun char-before-blank ()
  (save-excursion
  (forward-char -1)
  (looking-at "[\n\t\r]")))

(defun py-complete ()
  (interactive)
  (let ((pymacs-forget-mutability t))
    (if (and 
         (and (eolp) (not (bolp)) 
         (not (char-before-blank))))
      (insert (pycomplete-pycomplete (py-symbol-near-point) (py-find-global-imports)))
      (indent-for-tab-command))))

(defun py-find-global-imports ()
  (save-excursion
    (let (first-class-or-def imports)
      (goto-char (point-min))
      (setq first-class-or-def
        (re-search-forward "^ *\\(def\\|class\\) " nil t))
      (goto-char (point-min))
      (setq imports nil)
      (while (re-search-forward
          "\\(import \\|from \\([A-Za-z_][A-Za-z_0-9\\.]*\\) import \\).*"
          nil t)
    (setq imports (append imports
                  (list (buffer-substring
                     (match-beginning 0) 
                     (match-end 0))))))  
      imports)))

(define-key py-mode-map "\M-\C-i" 'py-complete)
(define-key py-mode-map "\t" 'py-complete)

(provide 'pycomplete)
