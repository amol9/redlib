from unittest import TestCase, main as ut_main
from itertools import cycle
from time import sleep

from redlib.api.prnt import ColumnPrinter, Column, ColumnPrinterError, ProgressColumn, SepColumn


class TestColumnPrinter(TestCase):

	def test_default(self):
		cp = ColumnPrinter()
		cp.printf('test123')
		cp.printf('really long string ' * 10)


	def test_2_col_fixed_width(self):
		cp = ColumnPrinter(cols=[Column(width=20), Column(width=40)])
		cp.printf('test', '123')
		cp.printf('test2', 'really long string ' * 10)


	def test_2_col_wrap_col_2(self):
		cp = ColumnPrinter(cols=[Column(width=20), Column(width=40, wrap=True)])
		cp.printf('test', '123')
		cp.printf('test2', 'really long string ' * 10)


	def test_2_col_wrap_both(self):
		cp = ColumnPrinter(cols=[Column(width=20, wrap=True), Column(width=40, wrap=True)])
		cp.printf('test', '123')
		cp.printf('test2 ' * 5, 'really long string ' * 10)


	def test_2_col_auto_fill(self):
		cp = ColumnPrinter(cols=[Column(fill=True), Column(fill=True)])
		s = self.gen_string(100)
		cp.printf(s, s)


	def test_3_col_fill_col_2(self):
		cp = ColumnPrinter(cols=[Column(width=20), Column(fill=True, max=90), Column(width=10)])
		s = self.gen_string(100)
		cp.printf('test', s, '1234')


	def test_3_col_fill_col_2_wrap(self):
		cp = ColumnPrinter(cols=[Column(width=20), Column(fill=True, max=90, wrap=True), Column(width=10)])
		s = self.gen_string(100)
		cp.printf('test', s, '1234')


	def test_align(self):
		cp = ColumnPrinter(cols=[Column(width=20, align='l'), Column(width=20, align='r'), Column(width=20, align='c'), Column(width=20)])
		cp.printf('left', 'right', 'center', 'left')

		print('-')
		cp = ColumnPrinter(cols=[Column(width=10, lmargin=1), Column(width=10, rmargin=0), Column(width=10, align='r'), Column(width=10, rmargin=0),
			Column(width=10, align='c'), Column(width=10, rmargin=0)])
		cp.printf('left', '0' * 10, 'right', '0' * 10, 'center12', '0' * 10)


	def test_margin(self):
		cp = ColumnPrinter(cols=[Column(width=20, lmargin=3), Column(width=20, rmargin=3, wrap=True), Column(width=1, rmargin=0)])
		s = self.gen_string(50)
		cp.printf('margin3l', s, '$')


	def test_ratio_2_col(self):
		cp = ColumnPrinter(cols=[Column(ratio=0.4, fill=True), Column(ratio=0.6, fill=True)])
		s = self.gen_string(100)
		cp.printf(s, s)

		print('-')
		cp = ColumnPrinter(cols=[Column(ratio=0.4, fill=True), Column(ratio=0.6, fill=True, wrap=True)])
		cp.printf(s, s + s)

		print('-')
		cp = ColumnPrinter(cols=[Column(ratio=0.4, fill=True), Column(ratio=0.6, fill=True, wrap=True, max=70)])
		cp.printf(s, s + s)

		print('-')
		cp = ColumnPrinter(cols=[Column(ratio=0.4, fill=True), Column(fill=True, wrap=True)])
		cp.printf(s, s + s)


	def test_exceptions(self):
		with self.assertRaises(ColumnPrinterError) as e:
			cp = ColumnPrinter(cols=[Column(ratio=0.4, fill=True), Column(ratio=1.2, fill=True, wrap=True)])
			cp = ColumnPrinter(cols=[Column(ratio=0.0, fill=True), Column(ratio=1.2, fill=True, wrap=True)])
			cp = ColumnPrinter(cols=[Column(width=10), Column(ratio=1.2, fill=True, wrap=True)])
			cp = ColumnPrinter(cols=[Column(width=1000), Column(ratio=0.2, fill=True, wrap=True)])
			cp = ColumnPrinter(cols=[Column(width=-1), Column(ratio=0.2, fill=True, wrap=True)])

			ColumnPrinter.get_terminal_width = lambda s : 100
			cp = ColumnPrinter(cols=[Column(width=99), Column(width=2)])
			cp = ColumnPrinter(cols=[Column(width=99), Column(fill=True), Column(fill=True)])
			cp = ColumnPrinter(cols=[Column(width=99), Column(fill=True, ratio=0.1)])


	def test_callbacks(self):
		pass


	def test_progress_column(self):
		pass


	def test_cp_in_cp(self):
		cp = ColumnPrinter(cols=[Column(width=20), Column(width=40)])
		incp = ColumnPrinter(cols=[Column(width=20), Column(width=20)], row_width=40)

		cp.printf('test', incp)
		incp.printf('first', '1')
		incp.printf('second', '2')
		incp.printf('third', '3')
		cp.printf('done')
		incp.done()

		incp.printf('extra')		# should not print


	def test_2_cp_in_cp(self):
		cp = ColumnPrinter(cols=[Column(width=20), Column(width=40), Column(width=40)])
		incp = ColumnPrinter(cols=[Column(width=20), Column(width=20)], row_width=40)
		incp2 = ColumnPrinter(cols=[Column(width=20), Column(fill=True)], row_width=40)

		cp.printf('test', incp, incp2)
		incp.printf('first-1', '1')
		incp2.printf('first-2', '1')
		incp.printf('second-1', '2')
		incp2.printf('second-2', '2')
		incp.printf('third-1', '3')
		incp.printf('fourth-1', '4')
		incp2.printf('third-2', '3')
		incp2.done()

		incp.printf('more-1', 'm')
		incp.printf('more-1', 'm')
		incp.printf('more-1', 'm')
		incp.done()

		cp.printf('done')


	def test_cb(self):
		cp = ColumnPrinter(cols=[Column(width=20), Column(width=20)])

		cb = cp.printf('test', '?', col_updt=True)
		for i in range(0, 100):
			cb.col_updt_cb(1, str(i))
			sleep(0.1)
			if i == 70:
				cp.printf('interrupt')
		cb.col_updt_cp()

		cp.printf('done')


	def test_progress(self):
		def progress(cp, col_num, lu=False, l=101):
			cb = cp.printf('progress', '?')
			for i in range(0, l):
				cb.progress_cb(col_num, i if not lu else None)
				sleep(0.05)

			cb.progress_cp(col_num)
			cp.printf('done', progress=False)

		cp = ColumnPrinter(cols=[Column(width=20), ProgressColumn(pwidth=10)])
		progress(cp, 1)

		cp = ColumnPrinter(cols=[Column(width=20), ProgressColumn(pwidth=10)])
		progress(cp, 1, lu=True)
	
		cp = ColumnPrinter(cols=[Column(width=20), ProgressColumn(pwidth=5, char='*')])
		progress(cp, 1, lu=True)

		cp = ColumnPrinter(cols=[Column(width=20), ProgressColumn(pwidth=10)])
		progress(cp, 1, l=70)
		
		cp = ColumnPrinter(cols=[Column(width=20), ProgressColumn(pwidth=1)])
		progress(cp, 1, lu=True)


	def test_progress_in_inner_cp(self):
		cp = ColumnPrinter(cols=[Column(width=20), Column(width=50)])
		incp = ColumnPrinter(cols=[Column(width=20), ProgressColumn(pwidth=10)], row_width=50)

		cp.printf('start')
		cp.printf('progress', incp)
		cb = incp.printf('downloading', '?')

		for i in range(0, 101):
			cb.progress_cb(1, i)
			sleep(0.05)
		cb.progress_cp(1)
		incp.done()
		cp.printf('done')


	def test_sep_column(self):
		cp = ColumnPrinter(cols=[Column(width=10, wrap=True), SepColumn(), Column(width=10, wrap=True)])

		cp.printf('one', '1')
		cp.printf('two')
		cp.printf('three', '3')
		cp.printf('wrap text', 'test ' * 4)
		cp.printf('wrap this column', 'text')
		cp.printf('wrap both columns', 'text ' * 3)		# need to fix
		cp.printf()
		cp.printf('done', '', 'extra')


	def enable_printf_sleep(self):
		self.saved_printf = ColumnPrinter.printf

		def p(*args, **kwargs):
			sleep(0.5)
			self.saved_printf(*args, **kwargs)

		ColumnPrinter.printf = p


	def gen_string(self, n=10):
		c = cycle('0123456789')
		output = ''
		for i in range(0, n):
			output += c.next()
		return output


if __name__ == '__main__':
	ut_main()

