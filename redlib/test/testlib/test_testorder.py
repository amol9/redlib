from unittest import TestCase, main as ut_main

from redlib.testlib.testorder import order


class TestTestOrder(TestCase):
	reg = []

	@order(0)
	def test_zero(self):
		self.assertEqual(len(self.reg), 0)
		self.reg.append(0)


	@order(1)
	def test_one(self):
		self.assertEqual(len(self.reg), 1)
		self.assertEqual(self.reg, [0])
		self.reg.append(1)


	@order(2)
	def test_two(self):
		self.assertEqual(len(self.reg), 2)
		self.assertEqual(self.reg, [0, 1])
		self.reg.append(2)


class TestDefaultOrder(TestCase):
	reg = []

	def test_a(self):
		self.assertEqual(len(self.reg), 0)
		self.reg.append(0)


	def test_b(self):
		self.assertEqual(len(self.reg), 1)
		self.assertEqual(self.reg, [0])
		self.reg.append(1)


	def test_c(self):
		self.assertEqual(len(self.reg), 2)
		self.assertEqual(self.reg, [0, 1])
		self.reg.append(2)


if __name__ == '__main__':
	ut_main()

