import sys
import inspect
import re
import os


def trim(docstring):
	'source: https://www.python.org/dev/peps/pep-0257/'

	if not docstring:
		return ''
	# Convert tabs to spaces (following the normal Python rules)
	# and split into a list of lines:
	lines = docstring.expandtabs().splitlines()
	# Determine minimum indentation (first line doesn't count):
	indent = sys.maxsize
	for line in lines[1:]:
		stripped = line.lstrip()
		if stripped:
			indent = min(indent, len(line) - len(stripped))
	# Remove indentation (first line is special):
	trimmed = [lines[0].strip()]
	if indent < sys.maxsize:
		for line in lines[1:]:
			trimmed.append(line[indent:].rstrip())
	# Strip off trailing and leading blank lines:
	while trimmed and not trimmed[-1]:
		trimmed.pop()
	while trimmed and not trimmed[0]:
		trimmed.pop(0)
	# Return a single string:
	return '\n'.join(trimmed)


def extract_help_w_regex(func):
	help = {}

	if func.__doc__ is not None:
		argspec = inspect.getargspec(func)
		if argspec.args[0] == 'self':
			del argspec.args[0]

		regex_args_help = "(.*)"				# short
		for arg in argspec.args:
			regex_args_help += "((%s):(.*))"%arg		# argument help
		regex_args_help += "(?:\n\s*\n.*)"			# longer help text

		regex = re.compile(regex_args_help, re.M | re.S)

		match = regex.match(func.__doc__)

		if match:
			help['short'] = match.group(1).strip()				# extract short description

			i = 3
			for _ in range(len(argspec.args)):
				help[match.group(i)] = match.group(i + 1).strip()
				i += 3

			help['long'] = match.group(i - 2).strip()			# extract long description

		if getattr(func, '__extrahelp__', None) is not None:			# extract any extra help
			help['extra'] = func.__extrahelp__.strip()

	return help


def extract_help(func):
	help = {}

	if func.__doc__ is not None:
		argspec = inspect.getargspec(func)
		item = 'short'

		for line in func.__doc__.splitlines():
			if len(line.strip()) == 0:
				item = 'long'
				continue

			if line.find(':') > 0:
				parts = line.split(':')
				item = parts[0].strip()
				help[item] = parts[1].strip()
			else:
				if item in help.keys():
					help[item] += os.linesep + line.strip()
				else:
					help[item] = line.strip()

	return help

