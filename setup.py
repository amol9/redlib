import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
import platform
import imp
from redlib.version import __version__


setup(	name			= 'redlib',
	description		= 'A collection of classes and functions for general utility.',
	version			= __version__,
	author			= 'Amol Umrale',
	author_email		= 'babaiscool@gmail.com',
	url			= 'http://pypi.python.org/pypi/redlib/',
	install_requires 	= ['six'],
	packages		= find_packages(),
	scripts			= ['ez_setup.py'],
	classifiers		= [
		'Development Status :: 4 - Beta',
		'License :: OSI Approved :: MIT License',
		'Natural Language :: English',
		'Operating System :: POSIX :: Linux',
		'Operating System :: Microsoft :: Windows'
	]		
)

