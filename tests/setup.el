; Emacs side of the testing protocol.

(load "pymacs.el" nil t)

(let ((buffer (get-buffer-create "*Tests*")))
  (with-current-buffer buffer
    (buffer-disable-undo)
    (while t
      (insert-file-contents-literally "_request")
      (let ((lisp-code (read (current-buffer)))
	    (standard-output (current-buffer)))
	(delete-region (point-min) (point-max))
	(eval lisp-code))
      (write-region nil nil "_reply" nil 0)
      (delete-region (point-min) (point-max))
      (delete-file "_request")
      (while (file-exists-p "_reply")
	(sleep-for 0 10)))))
