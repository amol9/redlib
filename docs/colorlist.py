import sys
import os

from redlib.colors import colorlist


if len(sys.argv) < 2:
	print('please specify rst filename')
	sys.exit(1)

rst_filename = sys.argv[1]
colorlist_text = ''

for col_name, col_value in colorlist.items():
	colorlist_text += '| ' + col_name + os.linesep	

rstfile_template = None
with open('colors.template', 'r') as f:
	rstfile_template = f.read()
	
rstfile_text = rstfile_template.replace('<colorlist>', colorlist_text)

with open(rst_filename, 'w') as f:
	f.write(rstfile_text)

