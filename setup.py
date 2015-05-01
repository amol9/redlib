import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
import platform
import imp
from mutils.version import __version__


setup(	name='mutils',
	description='A collection of commonly useful utilities.',
	version=__version__,
	author='Amol Umrale',
	author_email='babaiscool@gmail.com',
	url='http://pypi.python.org/pypi/mutils/',
	packages=find_packages(),
	scripts=['ez_setup.py'],
	classifiers=[
		'Development Status :: 4 - Beta',
		'License :: OSI Approved :: MIT License',
		'Natural Language :: English',
		'Operating System :: POSIX :: Linux',
		'Operating System :: Microsoft :: Windows'
	]		
)

