;; This script loads pymacs in a simple way

(defun load-test (testFile)
 
 (message testFile)
 (pymacs-load testFile)

 ;; (autoload 'pymacs-load "pymacs" nil t)
 ;; (autoload 'pymacs-eval "pymacs" nil t)
 ;; (autoload 'pymacs-apply "pymacs")
 ;; (autoload 'pymacs-call "pymacs")
 (message "[EMACS]:: Pymacs Test Finished")
)
(message "[EMACS]::: Pymacs Unit Testing:")
