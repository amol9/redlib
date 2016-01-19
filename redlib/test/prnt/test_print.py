from unittest import TestCase, main as ut_main

from redlib.prnt.func import prints, printc, print_colorlist


class TestPrint(TestCase):

	def test_prints(self):
		print('')
		prints('1')
		prints('2')
		print('3')
		print('all above numbers should be on the same line, no spaces')


	def test_printc(self):
		print('')
		printc('red', color='red')
		printc('blue', color='blue')
		printc('hex-grey', color='0x888888')
		printc('none')
		printc('invalid', color='jigglypuf')


	def test_print_colorlist(self):
		print('')
		print_colorlist()


if __name__ == '__main__':
	ut_main()

