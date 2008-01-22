"""
Python dot expression completion using Pymacs.

This almost certainly needs work, but if you add

    (require 'pycomplete)

to your .xemacs/init.el file (.emacs for GNU Emacs) and have Pymacs
installed, when you hit TAB it will try to complete the dot expression
before point.  For example, given this import at the top of the file:

    import time

typing "time.cl" then hitting TAB should complete "time.clock".

See pycomplete.el for the Emacs Lisp side of things.
"""
import sys
import os.path
import string 
from Pymacs import lisp


sys.path.append(".")

ENABLE_GG_FUZZY_GUESS=True

try:
    x = set
except NameError:
    from sets import Set as set
else:
    del x

def get_all_completions(s, imports=None):
    """Return contextual completion of s (string of >= zero chars).

    If given, imports is a list of import statements to be executed first.
    """
    locald = {}
    if imports is not None:
        for stmt in imports:
            try:
                exec stmt in globals(), locald
            except TypeError:
                raise TypeError, "invalid type: %s" % stmt
            except:
                continue
    dots = s.split(".") 
    if not s or len(dots) == 1:
        keys = set()
        keys.update(locald.keys())
        keys.update(globals().keys())
        import __builtin__
        keys.update(dir(__builtin__))
        keys = list(keys)
        keys.sort()
        if s:
            return [k for k in keys if k.startswith(s)]
        else:
            return keys

    sym = None
    for i in range(1, len(dots)):
        s = ".".join(dots[:i])   
        try:
            sym = eval(s, globals(), locald)
        except NameError:
            try:
                sym = __import__(s, globals(), locald, [])
            except ImportError:
                return []
    if sym is not None:  
        s = dots[-1]     
        return [k for k in dir(sym) if k.startswith(s)]

def get_keyword_completition(s):
    # Reserved keywords for Python 2.5 
    keywords=""" and       del       from      not       while    
as        elif      global    or        with     
assert    else      if        pass      yield    
break     except    import    print              
class     exec      in        raise              
continue  finally   is        return             
def       for       lambda    try
"""
    kl=keywords.split()
    
    return [ k+" " for k in kl if k.startswith(s)]

def get_common_fuzzy_completition(s):
    result=[]
    # Then we add  some *common* words 
    commonFuzzyWords=""" self. """    
    kl=commonFuzzyWords.split()
    result=[ k for k in kl if k.startswith(s)]
    if len(result)==0:
        dottedparts=s.split(".")
        if(len(dottedparts)>=2):
            mx=dottedparts[1]
            # This is a very tiny list of stuff
            kl=""" remove( append(  join(""".split()
            lisp.message("Hyper fuzzy extracted method:"+mx+" List:"+str(kl))
            result=[ k for k in kl if k.startswith(mx)]
    return result


def pycomplete(s, imports=None):
    completions = get_all_completions(s, imports)
    
    
    # [GG] Extension1:
    if ENABLE_GG_FUZZY_GUESS : # and len(completions)==0:
        #lisp.message("Trying to complete using a fuzzy guess for:"+s)
        k2=get_keyword_completition(s)
        k3=get_common_fuzzy_completition(s)
        # Integrate the fuzzy guess with other completitions
        for k in k2:
            completions.append(k)
        for k in k3:
            completions.append(k)
            
    lisp.message("DEBUG completions="+str(completions))
    dots = s.split(".")
    result = os.path.commonprefix([k[len(dots[-1]):] for k in completions])


    if result == "":
        if completions:
            width = lisp.window_width() - 2
            colum = width / 20
            white = "                    "
            
            msg = ""

            counter = 0
            for completion in completions :
                if completion.__len__() < 20 :
                    msg += completion + white[completion.__len__():]
                    counter += 1
                else :
                    msg += completion + white[completion.__len__() - 20:]
                    counter += 2

                if counter >= colum :
                    counter = 0
                    msg += '\n'

        else:
            msg = "no completions for:"+s

            
        lisp.message(msg)
    return  result       



def testPycomplete():
    print " ->", pycomplete("")
    print "sys.get ->", pycomplete("sys.get")
    print "sy ->", pycomplete("sy")
    print "sy (sys in context) ->", pycomplete("sy", imports=["import sys"])
    print "foo. ->", pycomplete("foo.")
    print "Enc (email * imported) ->", 
    print pycomplete("Enc", imports=["from email import *"])
    print "E (email * imported) ->",
    print pycomplete("E", imports=["from email import *"])

    print "Enc ->", pycomplete("Enc")
    print "E ->", pycomplete("E")


def test():
    from Pymacs import lisp,utility
    log=utility.log
    
    lisp.switch_to_buffer("*Messages*")
    log.info("Testing PyComplete extension... (GG)")
    log.info(" ->" + str(pycomplete("")))
    log.info("sys.get ->" + str(pycomplete("sys.get")))
    log.info("sy ->" + str(pycomplete("sy")))
    log.info("sy (sys in context) ->" + str(pycomplete("sy", imports=["import sys"])))
    log.info("foo. ->" + str(pycomplete("foo.")))
    log.info("Enc (email * imported) ->" + 
             str(pycomplete("Enc" , imports=["from email import *"])))
    log.info("E (email * imported) ->"+ str(pycomplete("E"  ,imports=["from email import *"])))

    log.info("Enc ->" + str(pycomplete("Enc")))
    log.info("E ->" + str(pycomplete("E")))
    log.info(" Test finished")

# Publish it:
interactions = {}
interactions[test]=''

if __name__ == "__main__":
    testPycomplete()
# Local Variables :
# pymacs-auto-reload : t
# End :
