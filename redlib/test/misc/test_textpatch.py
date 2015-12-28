from unittest import TestCase, main as ut_main
import os

from redlib.misc.textpatch import TextPatch


class TestTextPatch(TestCase):
	test_file =\
	'''# this is a test file, like a BASH script

	# if running bash
	if [ -n "$BASH_VERSION" ]; then
	    # include .bashrc if it exists
	    if [ -f "$HOME/.bashrc" ]; then
		. "$HOME/.bashrc"
	    fi
	fi
	'''

	test_filename = 'test.sh'

	def setUp(self):
		with open(self.test_filename, 'w') as f:
			f.write(self.test_file)

	def tearDown(self):
		os.remove(self.test_filename)

	def test_append_remove_line(self):
		tp = TextPatch(self.test_filename)

		line = 'export PATH="$PATH:/home/user/bin'
		id = 'my_change_1234'
		tp.append_line(line, id=id)

		with open(self.test_filename, 'r') as f:
			self.assertNotEquals(f.read().find(line), -1)

		tp.remove_line(id)

		with open(self.test_filename, 'r') as f:
			text = f.read()
			self.assertEquals(text.find(line), -1)
			self.assertEquals(text, self.test_file)


	def test_append_remove_section(self):
		tp = TextPatch(self.test_filename)

		section =\
		'''# set PATH so it includes user's private bin if it exists
		if [ -d "$HOME/bin" ] ; then
		    PATH="$HOME/bin:$PATH"
		fi
		'''
		id = 'my_change_1234'
		tp.append_section(section, id=id)

		with open(self.test_filename, 'r') as f:
			self.assertNotEquals(f.read().find(section), -1)

		tp.remove_section(id)

		with open(self.test_filename, 'r') as f:
			text = f.read()
			self.assertEquals(text.find(section), -1)
			self.assertEquals(text, self.test_file)


if __name__ == '__main__':
	ut_main()

