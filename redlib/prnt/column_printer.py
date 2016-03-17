from textwrap import wrap

from redlib.api.system import get_terminal_size
from .func import prints, printn


__all__ = ['ColumnPrinter']


class ColumnPrinter:

	def __init__(self, cols=[10, -1], ralign=[]):
		self._cols 		= cols
		self._fmt_string	= None
		self._last_col_wrap	= False
		self._ralign		= ralign

		self.make_fmt_string()

		self._progress_col	= None


	def make_fmt_string(self):
		fmt_string = u''
		term_width = get_terminal_size()[0]
		last_col_width = term_width - sum(self._cols[0:-1]) - 3

		i = 0
		for c in self._cols:
			align = '<'
			if i in self._ralign:
				align = '>'

			if c != -1:
				fmt_string += u'{%d:%s%d} '%(i, align, c)
			else:
				fmt_string += u'{%d:%s%d} '%(i, align, last_col_width)
			i += 1

		self._fmt_string = fmt_string
		self._last_col_wrap = self._cols[-1] == -1
		self._last_col_width = last_col_width


	def printf(self, *args, **kwargs):
		col_count = len(self._cols)
		progress_col = kwargs.get('progress_col', None)
		col_cb = kwargs.get('col_cb', False)
		ret_cb = {}

		if len(args) < col_count:
			args_copy = list(args) + ([''] * (col_count - len(args)))
		elif len(args) > col_count:
			args_copy = list(args[0 : col_count])
		else:
			args_copy = list(args)

		print_fn = printn
		if progress_col is not None:
			print_fn = prints

		last_col_wrap = False
		for i in range(0, len(args_copy)):
			col_width = self._cols[i]
			if len(args_copy[i]) > col_width:
				if col_width == -1:
					wrapped = wrap(args_copy[i], self._last_col_width)
					args_copy[i] = wrapped if len(wrapped) > 0 else ['']
					last_col_wrap = True
				else:
					args_copy[i] = args_copy[i][0 : col_width]


		if not last_col_wrap:
			print_fn(self._fmt_string.format(*args_copy))
		else:
			print(self._fmt_string.format(*(args_copy[0:-1] + [args_copy[-1][0]])))
			for line in args_copy[-1][1:]:
				print(self._fmt_string.format(*([''] * (len(args_copy) - 1) + [line])))

		if progress_col is not None:
			def progress_cb(progress):
				if len(progress) > self._cols[progress_col]:
					progress = progress[0 : self._cols[progress_col]]
				args_copy[progress_col] = progress

				prints('\r')
				prints(self._fmt_string.format(*args_copy))


			def progress_cp(msg=None):
				if msg is not None:
					progress_cb(msg)
				print('')


			ret_cb['progress_cb'] = progress_cb
			ret_cb['progress_cp'] = progress_cp

		if col_cb:
			def col_update_cb(col, msg):
				if len(msg) > self._cols[col]:
					msg = msg[0 : self._cols[col]]
				args_copy[col] = msg

				prints('\r')
				prints(self._fmt_string.format(*args_copy))
				
			ret_cb['col_cb'] = col_update_cb

		return ret_cb

	def print_progress(self, *args, **kwargs):
		self._progress_col = args[-1]
		return self.printf(*args[0 : -1])

