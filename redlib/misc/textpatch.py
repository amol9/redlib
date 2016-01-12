from os.path import exists
from os import linesep
import re
import sys

import six


class TextPatchError(Exception):
	pass


class TextPatch:
	section_end_prefix = 'end:'
	section_start_prefix = 'start:'


	def __init__(self, filepath, backup=False, comment_prefix='#'):
		if not exists(filepath):
			raise TextPatchError('%s does not exist'%filepath)

		self._filepath = filepath
		self._backup = backup
		self._comment_prefix = comment_prefix


	def append_line(self, line, id=None):
		with open(self._filepath, 'a+') as f:
			f.write(linesep)
			f.write(line + ('\t' + self._comment_prefix + id if id is not None else ''))


	def remove_line(self, id, count=six.MAXSIZE):
		if id is None or len(id) == 0:
			raise TextPatchError('need an identifier to find the line to remove')

		lines = []
		re_id = re.compile("^.*" + self._comment_prefix + ".*%s.*$"%id)
		rm_count = 0

		with open(self._filepath, 'r') as f:
			for line in f.read().splitlines():
				if re_id.match(line) is not None and rm_count < count:
					rm_count += 1
					continue
				lines.append(line + linesep)

		if len(lines) > 0:
			lines[-1] = lines[-1][:-1]

		with open(self._filepath, 'w') as f:
			f.writelines(lines)
				
		return rm_count


	def find_line(self, id):
		if id is None or len(id) == 0:
			raise TextPatchError('need an identifier to find the line to remove')

		re_id = re.compile("^.*" + self._comment_prefix + ".*%s.*$"%id)
		count = 0

		with open(self._filepath, 'r') as f:
			for line in f.read().splitlines():
				if re_id.match(line) is not None:
					count += 1

		return count


	def append_section(self, text, id=None):
		with open(self._filepath, 'a+') as f:
			f.write(linesep)
			if id is not None:
				f.write(self._comment_prefix + self.section_start_prefix + id + linesep)
			f.write(text + linesep)
			if id is not None:
				f.write(self._comment_prefix + self.section_end_prefix + id)


	def remove_section(self, id):
		if id is None or len(id) == 0:
			raise TextPatchError('need an identifier to find the section to remove')


		lines = []
		re_id_start = re.compile("^.*" + self._comment_prefix + ".*%s%s.*$"%(self.section_start_prefix, id))
		re_id_end = re.compile("^.*" + self._comment_prefix + ".*%s%s.*$"%(self.section_end_prefix, id))

		rm = False
		removed = False

		with open(self._filepath, 'r') as f:
			for line in f.read().splitlines():
				if re_id_start.match(line) is not None:
					if rm:
						raise TextPatchError('cannot remove nested sections')
					rm = True
					continue

				if re_id_end.match(line) is not None:
					if rm:
						rm = False
						removed = True
					continue

				if not rm:
					lines.append(line + linesep)

		if rm:
			raise TextPatchError('cannot remove section, end not found')

		if len(lines) > 0:
			lines[-1] = lines[-1][:-1]

		with open(self._filepath, 'w') as f:
			f.writelines(lines)

		return removed


	def prepend_line(self, line, id=None):
		pass

	
	def prepend_section(self, text, id=None):
		pass

