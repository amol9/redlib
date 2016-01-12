from unittest import TestCase, main as ut_main
import os
from glob import glob
from os.path import exists

from redlib.misc.textfile import TextFile, TextFileError
from redlib.misc.docstring import trim


class TestTextFile(TestCase):
	dbg_print_file = False 

	test_file = trim(
	'''# this is a test file, like a BASH script

	# if running bash
	if [ -n "$BASH_VERSION" ]; then
	    # include .bashrc if it exists
	    if [ -f "$HOME/.bashrc" ]; then
		. "$HOME/.bashrc"
	    fi
	fi
	''')

	more1 = trim(
	'''# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
	HISTSIZE=1000
	HISTFILESIZE=2000
	''')

	line = 'export PATH="$PATH:/home/user/bin'

	section = trim(
	'''# set PATH so it includes user's private bin if it exists
	if [ -d "$HOME/bin" ] ; then
	    PATH="$HOME/bin:$PATH"
	fi
	''')

	id = 'my_change_1234'

	test_filename 		= 'test.sh'
	empty_filename 		= 'empty.sh'
	noexist_filename 	= 'does_not_exist.sh'

	def setUp(self):
		with open(self.test_filename, 'w') as f:
			f.write(self.test_file)

		with open(self.empty_filename, 'w') as f:
			pass


	def tearDown(self):
		os.remove(self.test_filename)
		os.remove(self.empty_filename)

	def print_file(self, filename, header=None):
		if self.dbg_print_file:
			print('')
			if header is not None:
				print('---' + header + '---')
			with open(filename, 'r') as f:
				print(f.read())
			print('-')


	def append_remove_line(self, filename, mod_after_append=False):
		self.print_file(filename, "original file")
		tf = TextFile(filename)

		orig_text = open(filename, 'r').read()
		tf.append_line(self.line, id=self.id)
		self.print_file(filename, "file after appending line")

		if mod_after_append:
			self.append_to_file(filename, self.more1)

		with open(filename, 'r') as f:
			self.assertNotEquals(f.read().find(self.line), -1)

		tf.remove_line(self.id)
		self.print_file(filename, "file after removing appended line")

		with open(filename, 'r') as f:
			text = f.read()
			self.assertEquals(text.find(self.line), -1)
			if not mod_after_append:
				self.assertEquals(text, orig_text)


	def append_to_file(self, filename, text):
		with open(filename, 'a+') as f:
			f.write(os.linesep)
			f.write(self.more1)

		self.print_file(filename, "file after addind more content")


	def test_append_remove_line(self):
		self.append_remove_line(self.test_filename)


	def test_append_mod_remove_line (self):
		self.append_remove_line(self.test_filename, mod_after_append=True)


	def test_append_remove_line_on_empty_file(self):
		self.append_remove_line(self.empty_filename)


	def test_append_mod_remove_line_on_empty_file(self):
		self.append_remove_line(self.empty_filename, mod_after_append=True)


	def append_remove_section(self, filename, section, mod_after_append=False):
		tf = TextFile(filename)
		self.print_file(filename, "original file")

		orig_text = open(filename, 'r').read()
		
		tf.append_section(section, id=self.id)
		self.print_file(filename, "file after appending section")

		if mod_after_append:
			self.append_to_file(filename, self.more1)

		with open(filename, 'r') as f:
			self.assertNotEquals(f.read().find(section), -1)

		tf.remove_section(self.id)
		self.print_file(filename, "file after removing appended section")

		with open(filename, 'r') as f:
			text = f.read()
			self.assertEquals(text.find(section), -1)
			if not mod_after_append:
				self.assertEquals(text, orig_text)


	def test_append_remove_section(self):
		self.append_remove_section(self.test_filename, self.section)


	def test_append_mod_remove_section (self):
		self.append_remove_section(self.test_filename, self.section, mod_after_append=True)


	def test_append_remove_section_on_empty_file(self):
		self.append_remove_section(self.empty_filename, self.section)


	def test_append_mod_remove_section_on_empty_file(self):
		self.append_remove_section(self.empty_filename, self.section, mod_after_append=True)


	def test_append_remove_single_line_section(self):
		self.append_remove_section(self.test_filename, self.line)


	def test_append_remove_single_line_section_on_empty_file(self):
		self.append_remove_section(self.empty_filename, self.line)


	def test_file_not_found(self):
		with self.assertRaises(TextFileError) as a:
			tf = TextFile(self.noexist_filename)


	def test_remove_nested_section(self):
		tf = TextFile(self.test_filename)

		with open(self.test_filename, 'a+') as f:
			f.write(tf._comment_prefix + tf.section_start_prefix + self.id + os.linesep)

		tf.append_section(self.section, id=self.id)

		with self.assertRaises(TextFileError) as a:
			tf.remove_section(self.id)


	def remove_last_line_from_file(self, filename):
		lines = []
		with open(filename, 'r') as f:
			lines = f.read().splitlines()

		with open(filename, 'w') as f:
			for line in lines[:-2]:
				f.write(line + os.linesep)
			f.write(lines[-2])


	def test_remove_section_with_no_end_marker(self):
		filename = self.test_filename

		tf = TextFile(filename)
		self.print_file(filename, "original file")

		tf.append_section(self.section, id=self.id)
		self.print_file(filename, "file after appending section")

		self.remove_last_line_from_file(self.test_filename)
		self.print_file(filename, "file after removing end marker of section")

		with self.assertRaises(TextFileError) as a:
			tf.remove_section(self.id)


	def test_remove_from_empty_file(self):
		filename = self.empty_filename

		tf = TextFile(filename)

		tf.remove_line(self.id)
		self.assertEquals(open(filename, 'r').read(), '')

		tf.remove_section(self.id)
		self.assertEquals(open(filename, 'r').read(), '')


	def test_backup(self):
		[os.remove(f) for f in glob('*.' + TextFile.default_backup_ext + '*')]

		filename = self.test_filename

		def create_files(suffixes):
			for s in suffixes:
				open(self.test_filename + '.' + TextFile.default_backup_ext + s, 'a').close()

		def remove_files(suffixes):
			for s in suffixes:
				os.remove(self.test_filename + '.' + TextFile.default_backup_ext + s)

		def test(suffixes, next_suffix):
			textfile = TextFile(self.test_filename, backup=True)
			create_files(suffixes)
			backup_filename = textfile.backup()
			self.assertEqual(backup_filename,  self.test_filename + '.' + TextFile.default_backup_ext + next_suffix)
			self.assertTrue(exists(backup_filename))
			remove_files(suffixes + [next_suffix])

		test(['', '1', '2', '3', 'a'], '4')
		test(['', '1', '2', '3', '10', 'a'], '11')
		test(['1', '2', '3', 'a'], '4')
		test([], '')
		test(['w'], '')
		test(['22'], '23')

	
	def append_line_multiple_times(self, textfile, n):
		for _ in range (0, n):
			textfile.append_line(self.line, id=self.id)


	def test_find_line(self):
		textfile = TextFile(self.test_filename)

		self.assertEqual(0, textfile.find_line(self.id))

		textfile.append_line(self.line, id=self.id)
		self.assertEqual(1, textfile.find_line(self.id))

		self.append_line_multiple_times(textfile, 4)
		self.assertEqual(5, textfile.find_line(self.id))

		textfile.remove_line(self.id)
		self.assertEqual(0, textfile.find_line(self.id))


	def test_remove_dups(self):
		textfile = TextFile(self.test_filename)

		self.append_line_multiple_times(textfile, 4)
		textfile.append_line(self.line, id=self.id, remove_dups=True)

		self.assertEqual(1, textfile.find_line(self.id))

		textfile.append_line(self.line, id=self.id, remove_dups=True)
		self.assertEqual(1, textfile.find_line(self.id))


if __name__ == '__main__':
	ut_main()

