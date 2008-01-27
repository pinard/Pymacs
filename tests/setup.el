(load "pymacs.el" nil t)

(defun emacs (text)
  (let ((standard-output t))
    (pymacs-print-for-eval text)))

(defun emacs-eval (text)
  (let ((standard-output t))
    (pymacs-print-for-eval (pymacs-eval text))))
