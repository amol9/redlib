import types
import sys
from pkgutil import iter_modules
from importlib import import_module
from os.path import dirname, join as joinpath


class _RedMetaPathImporter(object):

    """
    A meta path importer to import six.moves and its submodules.

    This class implements a PEP302 finder and loader. It should be compatible
    with Python 2.5 and all existing versions of Python3
    """

    def __init__(self, six_module_name):
        self.name = six_module_name
        self.known_modules = {}

    def _add_module(self, mod, *fullnames):
        for fullname in fullnames:
            self.known_modules[self.name + "." + fullname] = mod

    def _get_module(self, fullname):
        return self.known_modules[self.name + "." + fullname]

    def find_module(self, fullname, path=None):
        if fullname in self.known_modules:
            return self
        return None

    def __get_module(self, fullname):
        try:
            return self.known_modules[fullname]
        except KeyError:
            raise ImportError("This loader does not know module " + fullname)

    def load_module(self, fullname):
        try:
            # in case of a reload
            return sys.modules[fullname]
        except KeyError:
            pass
        mod = self.__get_module(fullname)
        #if isinstance(mod, MovedModule):
        #    mod = mod._resolve()
        #else:
        mod.__loader__ = self

        sys.modules[fullname] = mod
        return mod

    def is_package(self, fullname):
        """
        Return true, if the named module is a package.

        We need this method to get correct spec objects with
        Python 3.4 (see PEP451)
        """
        return hasattr(self.__get_module(fullname), "__path__")

    def get_code(self, fullname):
        """Return None

        Required, if is_package is implemented"""
        self.__get_module(fullname)  # eventually raises ImportError
        return None
    get_source = get_code  # same as get_code


class GenModule(types.ModuleType):
	
	def __init__(self, name, dirpath, package):
		super(GenModule, self).__init__(name)

		self._members 	= []
		self._name 	= name
		self._dirpath 	= dirpath
		self._package	= package

		self.load_modules()


	def load_modules(self):
		for _, modname, is_pkg in iter_modules(path=[joinpath(self._dirpath, self._name)]):
			if not is_pkg:
				print ' adding module', modname
				mod = import_module('.' + modname, self._package + '.' + self._name)
				all = getattr(mod, '__all__', None)

				if all is not None:
					for member in all:
						setattr(self, member, getattr(mod, member, None))
						self._members.append(member)
					

	def __dir__(self):
		return self._members


def add_modules(importer, dirpath, package_name, exclude):
	for _, name, is_pkg in iter_modules(dirpath):
		if is_pkg and name not in exclude:
			print 'adding pkg', name
			importer._add_module(GenModule(name, dirpath, package_name), name)


# Complete the moves implementation.
# This code is at the end of this module to speed up module loading.
# Turn this module into a package.
#__path__ = []  # required for PEP 302 and PEP 451
#__package__ = __name__  # see PEP 366 @ReservedAssignment
#if globals().get("__spec__") is not None:
#    __spec__.submodule_search_locations = []  # PEP 451 @UndefinedVariable
# Remove other six meta path importers, since they cause problems. This can
# happen if six is removed from sys.modules and then reloaded. (Setuptools does
# this for some reason.)

def make_api(module_name, filepath, package_name, exclude=[]):
	red_importer = _RedMetaPathImporter(module_name)
	add_modules(red_importer, dirname(filepath), package_name, exclude)

	if sys.meta_path:
	    for i, importer in enumerate(sys.meta_path):
		# Here's some real nastiness: Another "instance" of the six module might
		# be floating around. Therefore, we can't use isinstance() to check for
		# the six meta path importer, since the other six instance will have
		# inserted an importer with different class.
		if (type(importer).__name__ == "_RedMetaPathImporter" and
			importer.name == module_name):
		    del sys.meta_path[i]
		    break
	    del i, importer
	# Finally, add the importer to the meta path import hook.
	sys.meta_path.append(red_importer)

