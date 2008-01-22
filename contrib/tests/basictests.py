import random
import unittest
import os, os.path
import sys

# Giovanni Giorgi Unit testing
# The unit testing works if you install the python module befaure actually launching it
# In the meantime the tests are pretty simple

class TestBasicFunctions(unittest.TestCase):
    def setUp(self):
        self.fixture=os.path.dirname(os.path.abspath(sys.argv[0]))+"/fixture/";
        #print "Starting an emacs instance"

    
    def testEmacsBoot(self):
        print "---- EMACS PATH IS:"
        os.system("which emacs")
        print "-------------------------"
        print "Fixture Directory:"+self.fixture
        exitStatus=self.bootEmacs(self.fixture+"../../pymacs.el", self.fixture+"../../Pymacs.utility")
        print "Exit status:"+str(exitStatus)
        self.assertEqual(0,exitStatus)

    def testEmacsBootErrorTest(self):
        # Test the error 65280
        # Given when the provided file is not loaded
        print
        print "********** Please ignore the following ERROR"
        print "**********"
        exitStatus=self.bootEmacs(self.fixture+"../../pymacs.el", self.fixture+"../nonexistent")        
        self.assertEqual(65280,exitStatus)
        print "**********"
        print "********** OK"


        
    def bootEmacs(self,lispGate, fileToLoad):
        # The emacs launch line must be something like the following.
        # -q is need to ensure we do not load your custom .emacs which can alter our tests
        launchline="emacs  -batch  -q "
        l1=launchline+" -l "+lispGate
        ## See undocumented eval in http://www.emacswiki.org/cgi-bin/wiki/CategoryBatchMode
        l1=l1+"  --eval=\"(pymacs-load \\\""+fileToLoad+"\\\" )\""
        print "Launching emacs:"+l1
        return os.system(l1);
        

if __name__ == '__main__':
    unittest.main()

