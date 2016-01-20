import sys
from types import ModuleType
from pkgutil import iter_modules
from importlib import import_module
from os.path import dirname, join as joinpath


__all__ = ['make_api', 'Move']


# fix:
# recurse dirs
# duplicate name check
# issue deprecation warning on moves


class _RedMetaPathImporter(object):
	'A meta path importer to import api and its submodules. Copied from package: six.'

	def __init__(self, module_name):
		self.name = module_name
		self.known_modules = {}


	def _add_module(self, mod, *fullnames):
		for fullname in fullnames:
			self.known_modules[self.name + "." + fullname] = mod


	#def _get_module(self, fullname):


	def get_module(self, fullname):
		mod = self.known_modules.get(fullname, None)

		if mod is None:
			if fullname in self.moves.keys():
				mod = self.known_modules.get(self.moves[fullname], None)
			else:
				raise ImportError('cannot import name ' + fullname)

		mod.load()

		return mod


	def find_module(self, fullname, path=None):
		if fullname in self.known_modules:
			return self
		return None


	def __get_module(self, fullname):
		return self.get_module(fullname)


	def load_module(self, fullname):
		try:
			# in case of a reload
			return sys.modules[fullname]
		except KeyError:
			pass
		mod = self.__get_module(fullname)
		mod.__loader__ = self

		sys.modules[fullname] = mod
		return mod


	def is_package(self, fullname):
		'''Return true, if the named module is a package.

		We need this method to get correct spec objects with
		Python 3.4 (see PEP451)'''

		return hasattr(self.__get_module(fullname), "__path__")


	def get_code(self, fullname):
		'''Return None
		Required, if is_package is implemented'''

		self.__get_module(fullname)  # eventually raises ImportError
		return None


	get_source = get_code  # same as get_code


class GenModule(ModuleType):
	
	def __init__(self, name, dirpath, package, moves):
		super(GenModule, self).__init__(name)

		self._members	= []
		self._name	= name
		self._dirpath	= dirpath
		self._package	= package
		self._moves 	= moves

		self._loaded	= False


	def load(self):
		if self._loaded:
			return

		for _, modname, is_pkg in iter_modules(path=[joinpath(self._dirpath, self._name)]):
			if not is_pkg:
				mod = import_module(self._package + '.' + self._name + '.' + modname)
				all = getattr(mod, '__all__', None)

				if all is not None:
					for member in all:
						# add member to this module
						setattr(self, member, getattr(mod, member, None))
						self._members.append(member)

						# check moves
						impname = self._name + '.' + member
						for m in self._moves:
							if m.new == impname:
								setattr(self, m.old_member_name(), getattr(mod, member, None))




		self._loaded = True
	

	def __dir__(self):
		return self._members


def add_modules(importer, dirpath, package_name, exclude, moves):
	for _, name, is_pkg in iter_modules([dirpath]):
		if name not in exclude:
			pkg_moves = []
			for move in moves:
				if move.old.startswith(name):
					pkg_moves.append(move)
			importer._add_module(GenModule(name, dirpath, package_name, pkg_moves), name)


class Move:
	def __init__(self, old, new):
		self.old = old
		self.new = new


	def old_member_name(self):
		return self.old[self.old.rfind('.') + 1:]

	def new_member_name(self):
		return self.new[self.new.rfind('.') + 1:]

	
def make_api(module_name, api_mod_filepath, package_name, exclude=[], moves=[]):
	red_importer = _RedMetaPathImporter(module_name)

	exclude.append(module_name[module_name.rfind('.') + 1:])

	add_modules(red_importer, dirname(api_mod_filepath), package_name, exclude, moves)

	if sys.meta_path:
		for i, importer in enumerate(sys.meta_path):
			if (type(importer).__name__ == "_RedMetaPathImporter" and
				importer.name == module_name):
				del sys.meta_path[i]
				break
			del i, importer
	sys.meta_path.append(red_importer)

