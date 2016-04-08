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


	def test_ratio_2_col(self):
		pass


	def gen_string(self, n=10):
		c = cycle('0123456789')
		output = ''
		for i in range(0, n):
			output += c.next()
		return output


if __name__ == '__main__':
	ut_main()

