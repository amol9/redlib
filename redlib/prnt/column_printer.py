from textwrap import wrap
from functools import partial
import sys

from redlib.api.system import get_terminal_size
from .func import prints, printn


__all__ = ['ColumnPrinter', 'Column', 'ColumnPrinterError', 'ProgressColumn']

# overlap
# add ProgressColumn (normal, char, cont, rotate), SepColumn (w/ condition)
# url wrap
# column color, style, header

maxn = max
debug_msgs = False

def debug(msg):
	if debug_msgs:
		sys.stderr.write(msg + '\n')


class Callbacks:

	def __init__(self):
		self.col_updt_cb		= None		# column update callback
		self.col_updt_cp		= None		# column update complete callback


class Column:
	
	def __init__(self, width=1, fill=False, max=None, min=None, wrap=False, align='l', ratio=None, rmargin=1, lmargin=None, overlap=0):
		self.width	= width
		self.fill	= fill
		self.max	= max
		self.min	= maxn(min, 1)
		self.wrap	= wrap
		self.align	= align
		self.ratio	= ratio
		self.rmargin	= rmargin
		self.lmargin	= lmargin
		self.overlap	= overlap


class ProgressColumn(Column):

	def __init__(self, pwidth=1, fill=False, max=None, min=None, ratio=None, rmargin=1, char='#', char_rot=False, char_set=['-', '\\', '|', '/']):
		Column.__init__(self, width=pwidth+rmargin, fill=fill, max=max, min=min, ratio=ratio, rmargin=1)

		self.pwidth 	= pwidth
		self.char 	= char
		self.char_rot	= char_rot or (pwidth == 1)
		self.char_set	= char_set


class ColumnPrinterError(Exception):
	pass


class Var:	# empty class used to hold variables so that they are accessible in callbacks inside printf
	pass


class ColumnPrinter:

	def __init__(self, cols=[Column(fill=True, wrap=True)], max_width=None):
		self._cols 		= cols
		self._fmt_string	= None
		self._last_col_wrap	= False

		self._col_updt_in_progress	= False
		self._newline_pending		= False
		self._max_width			= max_width

		self.process_cols()
		self.make_fmt_string()

		self.outer_cb = None
		self.outer_cp = None
		
		self._line_num = 0


	def get_terminal_width(self):
		return self._max_width or (get_terminal_size()[0] - 2)


	def process_cols(self):
		tw = self.get_terminal_width()

		if any(map(lambda c : c.width < 1, filter(lambda c : c.fill == False, self._cols))):
			raise ColumnPrinterError('column width must be at least 1')

		fill_cols = filter(lambda c : c.fill == True, self._cols)
		if sum(map(lambda c : c.ratio or (1 / len(fill_cols)), fill_cols)) > 1:
			raise ColumnPrinterError('total of fill column ratios > 1')

		total_fixed_width = sum(map(lambda c : (c.width or 0) if not c.fill else 0, self._cols))
		if total_fixed_width > tw:
			raise ColumnPrinterError('total width of fixed width columns exceeds terminal width, %d > %d'%(total_fixed_width, tw))

		total_fill_width = tw - total_fixed_width

		if len(fill_cols) > 0 and total_fill_width == 0:
			raise ColumnPrinterError('no space for fill columns')

		fill_width_avl = total_fill_width

		for col in fill_cols:
			if col.ratio is not None and fill_width_avl < (col.ratio * total_fill_width):
				raise ColumnPrinterError('col:%d, space for fill columns exhausted'%(self._cols.index(col) + 1))

			if col.ratio is not None:
				col.width = int(col.ratio * total_fill_width)
			else:
				col.width = int(total_fill_width / len(fill_cols))

			if col.width < col.min:
				raise ColumnPrinterError('col:%d, width < minimum width, %d < %d'%(self._cols.index(col) + 1, col.width, col.min))
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
		def newline():
			self._line_num += 1
			print('')

		if self._col_updt_in_progress or self._newline_pending:		# flush any remaining of the previous line or inner cp column data
			self._col_updt_in_progress = False
			self._newline_pending = False			
			newline()

		col_updt = kwargs.get('col_updt', False)
		progress = kwargs.get('progress', True)
		self._col_updt_in_progress = col_updt

		args_copy = self.copy_args(*args)	

		var = Var()

		var.line_num = self._line_num
		var.cur_row = 0					# current line number for this printf call
		var.max_row = 1					# max line number (except any inner column printers)
		var.inner_cp_max_row = 1			# max line number (for any inner column printers) 
		var.inner_col_prntrs = []			# inner column printers
		var.cur_row_inner_col_prntrs = []		# inner column printers for which callback is pending for the current line

		progress_cols = []
		progress_col_count = {}

		def outer_cb(col, msg):		# callback: inner CP makes to update its containing column
			if not col in var.inner_col_prntrs:		
				return						# inner cp has already called done()

			args_copy[col].append(msg)
			var.inner_cp_max_row = maxn(var.inner_cp_max_row, len(args_copy[col]))
			debug('inner cp max row: %d'%var.inner_cp_max_row)
			if not col in var.cur_row_inner_col_prntrs:
				return

			var.cur_row_inner_col_prntrs.remove(col)
			debug('printing rows, col: %d, %s'%(col, msg))
			print_rows()

		def outer_cp(col):		# callback: inner CP makes to signal end of updates
			if col in var.cur_row_inner_col_prntrs:
				var.cur_row_inner_col_prntrs.remove(col)

			var.inner_col_prntrs.remove(col)

		for i in range(0, len(args_copy)):	
			if args_copy[i].__class__ == ColumnPrinter:
				cp = args_copy[i]
				cp.outer_cb = partial(outer_cb, i)
				cp.outer_cp = partial(outer_cp, i)
				var.inner_col_prntrs.append(i)
				args_copy[i] = []		# initially nothing, a line is appended by every callback
			else:
				col = self._cols[i]
				width = col.width - ((col.rmargin or 0) + (col.lmargin or 0))
				if len(args_copy[i]) > width:
					if col.wrap:		# wrap
						wrapped = wrap(args_copy[i], width)
						args_copy[i] = wrapped if len(wrapped) > 0 else ['']
						var.max_row = max(var.max_row, len(wrapped))
					else:			# trim
						args_copy[i] = [args_copy[i][0 : width]]
				else:
					args_copy[i] = [args_copy[i]]

				if col.__class__ == ProgressColumn and progress:
					progress_cols.append(i)
					progress_col_count[i] = 0
					self._col_updt_in_progress = True

		def prints_row(row_num):	# print a single line (row) of output
			margin = lambda col, s : s if col.align == 'c' else (((col.lmargin or 0) * ' ' + s)  if col.align == 'l' else
				(s + (col.rmargin or 0) * ' '))
			row = map(lambda (a, c) : margin(c, a[row_num]) if row_num < len(a) else '', zip(args_copy, self._cols))
			out = self._fmt_string.format(*row)

			if self.outer_cb is None:
				prints(out)
			else:
				self.outer_cb(out)

		def print_rows():		# print lines for current args
			for i in range(var.cur_row, maxn(var.max_row, var.inner_cp_max_row)):
				prints_row(i)

				if self._col_updt_in_progress or len(var.cur_row_inner_col_prntrs) > 0:
					prints('\r')
					self._newline_pending = True
					break

				if self.outer_cb is None:
					newline()
					self._newline_pending = False

				var.cur_row += 1
				wait_for_inner_cps()

		def wait_for_inner_cps():			# will not go to new line unless all inner cps call back
			var.cur_row_inner_col_prntrs = list(var.inner_col_prntrs)

		wait_for_inner_cps()
		print_rows()

		if col_updt or (len(progress_cols) > 0 and progress):
			cb = Callbacks()

			def col_update_cb(col_num, msg):
				if var.line_num != self._line_num:
					return			# printing has moved on to next line(s)

				col = self._cols[col_num]
				width = col.width - ((col.rmargin or 0) + (col.lmargin or 0))
				if len(msg) > width:
					msg = msg[0 : width]
				args_copy[col_num] = [msg]
				print_rows()

			def col_update_cp():
				if var.line_num != self._line_num:
					return

				self._col_updt_in_progress = False
				print_rows()

			def progress_str(col_num, progress, cp=False):
				col = self._cols[col_num]
				pstr = ''

				if not col.char_rot:
					if progress is not None:
						pstr = col.char * int((float(progress) / 100) * col.pwidth)	# progress in percentage
						progress_col_count[col_num] = None
					else:
						if progress_col_count[col_num] is not None:
							char_count = (progress_col_count[col_num] % col.pwidth + 1) if not cp else col.pwidth
							pstr = (col.char * char_count)					# continuous progress w/o known limit
							progress_col_count[col_num] += 1
						else:
							return None
				else:
					progress_col_count[col_num] += 1
					pstr = col.char_set[progress_col_count[col_num] % len(col.char_set)]

				return pstr

			def progress_cb(col_num, progress):
				if not col_num in progress_cols:
					return

				args_copy[col_num] = [progress_str(col_num, progress)]
				print_rows()

			def progress_cp(col_num):
				if col_num in progress_cols:
					progress_cols.remove(col_num)

				pstr = progress_str(col_num, None, cp=True)
				if pstr is None:
					return

				args_copy[col_num] = [pstr]
				print_rows()

			if col_updt:
				cb.col_updt_cb = col_update_cb
				cb.col_updt_cp = col_update_cp
			if len(progress_cols) > 0:
				cb.progress_cb = progress_cb
				cb.progress_cp = progress_cp

			return cb	# return callbacks only if column update was requested or progress column(s) present


	def copy_args(self, *args):
		col_count = len(self._cols)

		if len(args) < col_count:
			args_copy = list(args) + ([''] * (col_count - len(args)))
		elif len(args) > col_count:
			args_copy = list(args[0 : col_count])
		else:
			args_copy = list(args)

		return args_copy


	def done(self):
		if self.outer_cp is not None:
			self.outer_cp()

