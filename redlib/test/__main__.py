from unittest import defaultTestLoader, runner
from os.path import dirname, abspath
import sys


tests = defaultTestLoader.discover(dirname(abspath(__file__)))
testRunner = runner.TextTestRunner()
result = testRunner.run(tests)

sys.exit(not result.wasSuccessful())

