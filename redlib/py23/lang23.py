
from ..system.common import *


__all__ = ['cmp', 'b', 's']


if is_py3():
	cmp = lambda a, b: (a > b) - (a < b)
else:
	cmp = cmp


def b(input, enc='utf-8'):
	if is_py3():
		return bytes(input, enc)
	else:
		return bytes(input)


def s(input, enc='utf-8'):
	if is_py3():
		return input.decode('utf-8')
	else:
		return input
