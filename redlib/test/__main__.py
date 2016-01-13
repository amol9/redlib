from os.path import dirname, abspath

from redlib.testlib.testrunner import TestRunner


testrunner = TestRunner(dirname(abspath(__file__)))
testrunner.run_all()

