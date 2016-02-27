from textwrap import wrap

from redlib.api.system import get_terminal_size


__all__ = ['ColumnPrinter']


class ColumnPrinter:

	def __init__(self, cols=[10, -1], ralign=[]):
		self._cols 		= cols
		self._fmt_string	= None
		self._last_col_wrap	= False
		self._ralign		= ralign

		self.make_fmt_string()


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


	def printf(self, *args):
		col_count = len(self._cols)

		if len(args) < col_count:
			args_copy = list(args) + ([''] * (col_count - len(args)))
		elif len(args) > col_count:
			args_copy = list(args[0 : col_count])
		else:
			args_copy = list(args)

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
			print(self._fmt_string.format(*args_copy))
		else:
			print(self._fmt_string.format(*(args_copy[0:-1] + [args_copy[-1][0]])))
			for line in args_copy[-1][1:]:
				print(self._fmt_string.format(*([''] * (len(args_copy) - 1) + [line])))

