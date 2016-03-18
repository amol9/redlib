from os.path import exists, join as joinpath
from os import mkdir, makedirs, remove
import hashlib
from glob import glob
from datetime import datetime, timedelta

from ..misc.singleton import Singleton


class CacheError(Exception):
	pass


class _Cache():
	def __init__(self, cache_dir):
		self._cache_dir = cache_dir
		self.check()


	def check(self):
		if not exists(self._cache_dir):
			makedirs(self._cache_dir)
			open(joinpath(self._cache_dir, (datetime.today() + timedelta(days=1)).strftime('expiry%d%b%Y')), 'w').close()
		else:
			expiry_file = glob(joinpath(self._cache_dir, 'expiry*'))
			expiry = datetime.strptime(expiry_file[0][-9:], '%d%b%Y') if len(expiry_file) > 0 else datetime(1970, 1, 1)
			today = datetime.today()
			if expiry <= today:
				self.clear_cache()
			

	def add(self, url, data):
		md5h = hashlib.md5()
		md5h.update(url.encode('utf-8'))
		
		with open(joinpath(self._cache_dir, md5h.hexdigest()), 'wb') as f:
			f.write(data)


	def get(self, url):
		md5h = hashlib.md5()
		md5h.update(url.encode('utf-8'))

		data = None
		path = joinpath(self._cache_dir, md5h.hexdigest())
		if exists(path):
			with open(path, 'rb') as f:
				data = f.read()

		return data
		

	def clear_cache(self):
		for filepath in glob(joinpath(self._cache_dir, '*')):
			remove(filepath)
		open(joinpath(self._cache_dir, (datetime.today() + timedelta(days=1)).strftime('expiry%d%b%Y')), 'w').close()


class Cache(Singleton):
	classtype = _Cache

