import sys

from ..colors.colortrans import rgb2short
from ..colors import colorlist
from ..system import is_linux, terminalsize


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
	terminal_width, _ = terminalsize.get_terminal_size()
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

