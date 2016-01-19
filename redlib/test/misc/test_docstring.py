from unittest import TestCase, main as ut_main

from redlib.misc.docstring import extract_help


class TestClass:
	def add(self, a, b):
		'''Add two numbers.
		a: first number
		b: second number'''
		pass

	def div(self, a, b):
		'''Divide  first number by second number.
		Note: result will be float.

		a: 	first number
		b: 	second number
			may not be zero

		This is extra help text (long).'''
		pass

	def sub(self, a, b):
		'''a: first number
		some more help on a
		b: second number'''
		pass

	def mul(self, a, b):
		'''Multiply two numbers.
		a: first number'''		
		pass

	def mod(self, a, b):
		pass

	def ceil(self, a):
		'Return nearest greater integer.'
		pass

	def floor(self, a):
		'''Return nearest smaller integer.
		a: input number, number type: int / float'''
		pass


class TestExtractHelp(TestCase):

	def test_no_long(self):
		help = extract_help(TestClass.add)

		self.assertEqual(len(help), 4)
		self.assertDictEqual(help, {'short'	: 'Add two numbers.',
					    'a'		: 'first number',
					    'b'		: 'second number',
					    'long'	: None})


	def test_multiline_short_and_long(self):
		help = extract_help(TestClass.div)

		self.assertEqual(len(help), 4)
		self.assertDictEqual(help, {'short'	: 'Divide  first number by second number.\nNote: result will be float.',
					    'a'		: 'first number',
					    'b'		: 'second number\nmay not be zero',
					    'long'	: 'This is extra help text (long).'})


	def test_no_short_multiline_arg_help(self):
		help = extract_help(TestClass.sub)

		self.assertEqual(len(help), 4)
		self.assertDictEqual(help, {'short'	: None,
					    'a'		: 'first number\nsome more help on a',
					    'b'		: 'second number',
					    'long'	: None})


	def test_one_arg_missing(self):
		help = extract_help(TestClass.mul)

		self.assertEqual(len(help), 3)
		self.assertDictEqual(help, {'short'	: 'Multiply two numbers.',
					    'a'		: 'first number',
					    'long'	: None})


	def test_no_docstring(self):
		help = extract_help(TestClass.mod)

		self.assertEqual(len(help), 2)


	def test_only_short(self):
		help = extract_help(TestClass.ceil)

		self.assertEqual(len(help), 2)
		self.assertDictEqual(help, {'short'	: 'Return nearest greater integer.',
					    'long'	: None})


	def test_colon_in_arg_help(self):
		help = extract_help(TestClass.floor)

		self.assertEqual(len(help), 3)
		self.assertDictEqual(help, {'short'	: 'Return nearest smaller integer.',
					    'a'		: 'input number, number type: int / float',	
					    'long'	: None})



if __name__ == '__main__':
	ut_main()

