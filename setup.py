import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
import platform
import imp
from mangoutils.version import __version__


setup(	name='mangoutils',
	description='A collection of commonly useful utilities.',
	version=__version__,
	author='Amol Umrale',
	author_email='babaiscool@gmail.com',
	url='http://pypi.python.org/pypi/mangoutils/',
	packages=['mangoutils', 'mangoutils.web', 'mangoutils.html', 'mangoutils.system'],
	scripts=['ez_setup.py'],
	classifiers=[
		'Development Status :: 4 - Beta',
		'License :: OSI Approved :: MIT License',
		'Natural Language :: English',
		'Operating System :: POSIX :: Linux',
		'Operating System :: Microsoft :: Windows'
	]		
)

