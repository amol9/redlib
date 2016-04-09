from unittest import TestCase, main as ut_main
from itertools import cycle

from redlib.api.prnt import ColumnPrinter, Column, ColumnPrinterError


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


	def gen_string(self, n=10):
		c = cycle('0123456789')
		output = ''
		for i in range(0, n):
			output += c.next()
		return output


if __name__ == '__main__':
	ut_main()

