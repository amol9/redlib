from .misc.makeapi import make_api, Move

moves = [
		Move('misc.trim', 'misc.trim_docstring')
	]

exclude = ['test', 'version']

make_api(__name__, __file__, __package__, exclude=exclude, moves=moves)

__path__ = []

