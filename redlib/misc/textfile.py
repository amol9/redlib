from os.path import exists, dirname, join as joinpath, basename
from os import linesep
import re
import sys
from glob import glob
from shutil import copy

import six


class TextFileError(Exception):
	pass



class TextFile:

	section_end_prefix 	= 'end:'
	section_start_prefix 	= 'start:'
	default_comment_prefix	= '#'
	default_backup_ext	= 'bkp'


	def __init__(self, filepath, backup=False, comment_prefix=None, backup_ext=None):
		if not exists(filepath):
			raise TextFileError('%s does not exist'%filepath)

		self._filepath 		= filepath
		self._backup 		= backup
		self._comment_prefix 	= comment_prefix if comment_prefix is not None else self.default_comment_prefix
		self._backup_ext 	= backup_ext if backup_ext is not None else self.default_backup_ext


	def backup(self):
		if not self._backup:
			return None

		dirpath = dirname(self._filepath)
		backup_files = glob(joinpath(dirpath, basename(self._filepath) + '.' + self._backup_ext + '*'))

		def str_to_int(n):
			try:
				return int(n)
			except ValueError:
				return 0

		n = None
		if len(backup_files) > 0:
			backup_nos = [str_to_int(n) for n in [f[f.rfind(self._backup_ext) + len(self._backup_ext):] for f in backup_files]]
			n = max(backup_nos)
		else:
			n = 0

		ext = self._backup_ext if n == 0 else self._backup_ext + str(n + 1)

		try:
			backup_filepath = joinpath(dirpath, basename(self._filepath) + '.' + ext)
			copy(self._filepath, backup_filepath)
			return backup_filepath
		except IOError as e:
			raise TextFileError('aborting operation, could not create backup file: %s'%backup_filepath)


	def append_line(self, line, id=None, remove_dups=False):
		if remove_dups:
			count = self.find_line(id)
			if count > 0:
				if count > 1:
					self.remove_line(id, count=count-1)
				return

		with open(self._filepath, 'a+') as f:
			f.write(linesep)
			f.write(line + ('\t' + self._comment_prefix + id if id is not None else ''))


	def remove_line(self, id, startswith=None, endswith=None, regex=None, count=six.MAXSIZE):
		if id is None or len(id) == 0:
			raise TextFileError('need an identifier to find the line to remove')

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
			raise TextFileError('need an identifier to find the line to remove')

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
			raise TextFileError('need an identifier to find the section to remove')


		lines = []
		re_id_start = re.compile("^.*" + self._comment_prefix + ".*%s%s.*$"%(self.section_start_prefix, id))
		re_id_end = re.compile("^.*" + self._comment_prefix + ".*%s%s.*$"%(self.section_end_prefix, id))

		rm = False
		removed = False

		with open(self._filepath, 'r') as f:
			for line in f.read().splitlines():
				if re_id_start.match(line) is not None:
					if rm:
						raise TextFileError('cannot remove nested sections')
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
			raise TextFileError('cannot remove section, end not found')

		if len(lines) > 0:
			lines[-1] = lines[-1][:-1]

		with open(self._filepath, 'w') as f:
			f.writelines(lines)

		return removed


	def prepend_line(self, line, id=None):
		pass

	
	def prepend_section(self, text, id=None):
		pass

