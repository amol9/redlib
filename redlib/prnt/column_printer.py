from textwrap import wrap

from redlib.api.system import get_terminal_size
from .func import prints, printn


__all__ = ['ColumnPrinter', 'Column', 'ColumnPrinterError']

# margin, factor it in on width calc
# CP inside CP
# overlap

class Callbacks:
	def __init__(self):
		self.col_cb		= None
		self.col_cp		= None


class Column:
	
	def __init__(self, width=1, fill=False, max=None, min=None, wrap=False, align='l', ratio=None, rmargin=1, lmargin=None, overlap=0):
		self.width	= width
		self.fill	= fill
		self.max	= max
		self.min	= min or 1
		self.wrap	= wrap
		self.align	= align
		self.ratio	= ratio
		self.rmargin	= rmargin
		self.lmargin	= lmargin
		self.overlap	= overlap


class ColumnPrinterError(Exception):
	pass


class ColumnPrinter:

	def __init__(self, cols=[Column(fill=True, wrap=True)]):
		self._cols 		= cols
		self._fmt_string	= None
		self._last_col_wrap	= False

		self.check_cols()
		self.make_fmt_string()

		self._row_not_cp	= False


	def check_cols(self):
		tw, _ = get_terminal_size()
		tw -= 2

		if any(map(lambda c : c.width < 1, filter(lambda c : c.fill == False, self._cols))):
			raise ColumnPrinterError()

		fill_cols = filter(lambda c : c.fill == True, self._cols)

		total_fill_width = tw - sum(map(lambda c : (c.width or 0) if not c.fill else 0, self._cols))

		if len(fill_cols) > 0 and total_fill_width == 0:
			raise ColumnPrinterError()

		fill_width_avl = total_fill_width

		for col in fill_cols:
			if col.ratio is not None and fill_width_avl < (col.ratio * total_fill_width):
				raise ColumnPrinterError()

			if col.ratio is not None:
				col.width = col.ratio * total_fill_width
			else:
				col.width = int(total_fill_width / len(fill_cols))

			if col.width < col.min:
				raise ColumnPrinterError()
			if col.max is not None and col.width > col.max:
				col.width = col.max

			fill_width_avl -= col.width


	def make_fmt_string(self):
		fmt_string = u''
		align_map = {'l': '<', 'r': '>', 'c': '^'}

		i = 0
		for c in self._cols:
			fmt_string += u'{%d:%s%d}'%(i, align_map[c.align], c.width)
			i += 1

		self._fmt_string = fmt_string


	def printf(self, *args, **kwargs):
		if self._row_not_cp:
			self._row_not_cp = False
			print('')

		col_count = len(self._cols)
		col_cb = kwargs.get('col_cb', False)
		ret_cb = Callbacks()

		if len(args) < col_count:
			args_copy = list(args) + ([''] * (col_count - len(args)))
		elif len(args) > col_count:
			args_copy = list(args[0 : col_count])
		else:
			args_copy = list(args)

		self._row_not_cp = col_cb

		max_row = 1
		for i in range(0, len(args_copy)):
			col = self._cols[i]
			width = col.width - ((col.rmargin or 0) + (col.lmargin or 0))
			if len(args_copy[i]) > width:
				if col.wrap:		# wrap
					wrapped = wrap(args_copy[i], width)
					args_copy[i] = wrapped if len(wrapped) > 0 else ['']
					max_row = max(max_row, len(wrapped))
				else:			# trim
					args_copy[i] = [args_copy[i][0 : width]]
			else:
				args_copy[i] = [args_copy[i]]


		last_row = None
		for i in range(0, max_row):
			if i > 0:
				print('')

			# fix for c align, or short strings
			margin = lambda col, s : (col.lmargin or 0) * ' ' + s + (col.rmargin or 0) * ' ' 
			last_row = map(lambda (a, c) : margin(c, a[i]) if i < len(a) else '', zip(args_copy, self._cols))
			prints(self._fmt_string.format(*last_row))

		if not self._row_not_cp:
			print('')

		'''if not col_wrapped:
			print_fn(self._fmt_string.format(*args_copy))
		else:
			print(self._fmt_string.format(*(args_copy[0:-1] + [args_copy[-1][0]])))
			for line in args_copy[-1][1:]:
				print(self._fmt_string.format(*([''] * (len(args_copy) - 1) + [line])))'''

		if col_cb:
			def col_update_cb(col, msg):
				if len(msg) > self._cols[col].width:
					msg = msg[0 : self._cols[col].width]
				last_row[col] = msg

				prints('\r')
				prints(self._fmt_string.format(*last_row))

			def col_update_cp():
				print('')
				self._row_not_cp = False
				
			ret_cb.col_cb = col_update_cb
			ret_cb.col_cp = col_update_cp

		return ret_cb

