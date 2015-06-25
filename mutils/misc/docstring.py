import sys
import inspect
import re


def trim(docstring):
        'source: https://www.python.org/dev/peps/pep-0257/'

	if not docstring:
		return ''
	# Convert tabs to spaces (following the normal Python rules)
	# and split into a list of lines:
	lines = docstring.expandtabs().splitlines()
	# Determine minimum indentation (first line doesn't count):
	indent = sys.maxint
	for line in lines[1:]:
		stripped = line.lstrip()
		if stripped:
			indent = min(indent, len(line) - len(stripped))
	# Remove indentation (first line is special):
	trimmed = [lines[0].strip()]
	if indent < sys.maxint:
		for line in lines[1:]:
			trimmed.append(line[indent:].rstrip())
	# Strip off trailing and leading blank lines:
	while trimmed and not trimmed[-1]:
		trimmed.pop()
	while trimmed and not trimmed[0]:
		trimmed.pop(0)
	# Return a single string:
	return '\n'.join(trimmed)


def extract_help(func):
	assert func.__doc__ is not None

	argspec = inspect.getargspec(func)
	if argspec.args[0] == 'self':
		del argspec.args[0]

	regex_args_help = ""
	for arg in argspec.args:
		regex_args_help += "((%s):(.*))"%arg

	regex = re.compile("(.*)" + regex_args_help, re.M | re.S)

	match = regex.match(func.__doc__)

	help = {}
	if match:
		help['help'] = match.group(1).strip()			#extract main help string

		i = 3
		for _ in range(len(argspec.args)):
			help[match.group(i)] = match.group(i+1).strip()
			i += 3

	return help
