from unittest import TestCase, main as ut_main

from mutils.misc import docstring


class TestClass:
	def add(self, a, b):
		'''Add two numbers.
		a: first number
		b: second number'''
		pass

	def div(self, a, b):
		'''Divide  first number by 2.
		Note: result will be float.
		a: first number
		b: second number\n may not be zero'''
		pass

	def sub(self, a, b):
		'''a: first number
		b: second number'''
		pass

	def mul(self, a, b):
		'''Multiply two numbers.
		a: first number'''
		pass


class TestDocstring(TestCase):

	def test_extract_help(self):
		help = docstring.extract_help(TestClass.add)

		self.assertEqual(len(help), 3)
		self.assertDictEqual(help, {'help'	: 'Add two numbers.',
					    'a'		: 'first number',
					    'b'		: 'second number'})


	def test_extract_help_multiline(self):
		help = docstring.extract_help(TestClass.div)

		self.assertEqual(len(help), 3)
		self.assertDictEqual(help, {'help'	: 'Divide  first number by 2.\n\t\tNote: result will be float.',
					    'a'		: 'first number',
					    'b'		: 'second number\n may not be zero'})


	def test_extract_help_no_main_help(self):
		help = docstring.extract_help(TestClass.sub)

		self.assertEqual(len(help), 3)
		self.assertDictEqual(help, {'help'	: '',
					    'a'		: 'first number',
					    'b'		: 'second number'})


	def test_extract_help_one_arg_missing(self):
		help = docstring.extract_help(TestClass.mul)

		self.assertEqual(len(help), 0)


if __name__ == '__main__':
	ut_main()

