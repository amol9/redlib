
from ..system.common import is_py2


__all__ = ['ob']


def ob(input, key=b'48bldg03yghsl;741dfbml<?x8jgbv3805'):
	s = None
	mask = None

	if is_py2():
		s = bytearray(input)
		mask = bytearray(key)
	else:
		s = input
		mask = key

	lmask = len(mask)
	output = [c ^ mask[i % lmask] for i, c in enumerate(s)]

	if is_py2():
		return str(bytearray(output))
	else:
		return bytes(output)

