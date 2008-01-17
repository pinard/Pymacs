from pymacs import lisp

def test(objet):
    lisp.setcar(objet, "Bonjour")
    lisp.setcdr(objet, ("chez vous!",))
    return objet
