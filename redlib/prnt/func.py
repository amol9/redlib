'This module contains miscellaneous printing functions.'

import sys

from ..colors.colortrans import rgb2short
from ..colors.clist import colorlist
from ..system.common import is_linux
from ..system.terminalsize import get_terminal_size


__all__ = ['printc', 'prints', 'print_colorlist']


def printc(msg, color=None):
	colorval = None
	if color is not None:
		if color.startswith('0x'):
			colorval = color
		else:
			colorval = colorlist.get(color, None)

	if colorval is not None:
		short, _ = rgb2short(colorval[2 : ])
		prints('\x1b[38;5;%sm'%short)
		prints(msg)

		if is_linux():
			print('\x1b[0m')
		else:
			print('')
	else:
		print(msg)


def prints(msg):
	if sys.stdout is not None:
		sys.stdout.write(msg)
		sys.stdout.flush()


def print_colorlist():
	count = 0
	color_name_col_width = 22
	terminal_width, _ = get_terminal_size()
	colors_per_line = int(terminal_width / (color_name_col_width + 3))

	for name, value in colorlist.items():
		if is_linux():
			short, _ = rgb2short(value[2 : ])
			prints('\x1b[38;5;%sm'%short)

		prints(('{0:%d}'%color_name_col_width).format(name))

		count += 1
		if count % colors_per_line == 0 :
			print('')
	if is_linux():
		print('\x1b[0m')


# docs:

printc.__doc__ = \
	"""Print the given message in specified color.

	Args:
		msg (str): The message to be printed.
		color (str): Color name. (e.g. red, blue, etc.) Or, color hex value (e.g. 0xaaaaaa).

	Notes:
		If no color is specified, the message will be printed in the default color.

		Use function `print_colorlist()` to print a list of all available color names.

		Supported Platform: Linux only.

	"""

prints.__doc__ = \
	"""Python version independent (2.7/3.x) way to print without newline.

	Args:
		msg (str): The message to be printed.
	  
	"""

print_colorlist.__doc__ = \
	"""Print a list of all available color names.

	Example:

	.. testcode::

		from redlib.prnt import *
		print_colorlist()

	.. testoutput::
	    :options: +ELLIPSIS

	    indigo, 

	"""

