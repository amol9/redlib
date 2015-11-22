from six import print_

from .colortrans import rgb2short
from ..system import terminalsize, is_linux
from . import colorlist


def print_colorlist():
	count = 0
	color_name_col_width = 22
	terminal_width, _ = terminalsize.get_terminal_size()
	colors_per_line = int(terminal_width / (color_name_col_width + 3))

	for name, value in colorlist.items():
		if is_linux():
			short, _ = rgb2short(value[2 : ])
			print_('\x1b[38;5;%sm'%short, end='')

		print_(('{0:%d}'%color_name_col_width).format(name), end='')

		count += 1
		if count % colors_per_line == 0 :
			print('')
	if is_linux():
		print('\x1b[0m')

