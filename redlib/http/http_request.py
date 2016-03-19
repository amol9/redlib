from io import StringIO, BytesIO
import sys
from functools import partial
import socket

from enum import Enum

from redlib.api.system import *
from redlib.api.prnt import prints, format_size
from .cache import Cache


if is_py3():
	from urllib.error import HTTPError as UrllibHTTPError, URLError
	from urllib.request import urlopen, Request
else:
	from urllib2 import HTTPError as UrllibHTTPError, urlopen, URLError, Request


__all__ = ['HttpErrorType', 'HttpError', 'GlobalOptions', 'RequestOptions', 'HttpRequest']


HttpErrorType = Enum('HttpErrorType', ['other', 'timeout', 'size'])


class HttpError(Exception):

	def __init__(self, msg, err_type=HttpErrorType.other, code=None):
		super(HttpError, self).__init__(msg)
		self.err_type = err_type
		self.code = code


class GlobalOptions:

	def __init__(self, cache_dir=None, chunksize=50*1024, headers=None, timeout=120, max_content_length=1024*1024*10):
		self.cache_dir		= cache_dir
		self.chunksize		= chunksize
		self.headers		= headers
		self.timeout		= timeout
		self.max_content_length	= max_content_length


class RequestOptions:

	def __init__(self, save_filepath=None, nocache=False, open_file=None, headers=None,
			progress_cb=None, progress_cp=None, content_length_cb=None, max_content_length=None):

		self.save_filepath	= save_filepath
		self.nocache		= nocache
		self.open_file		= open_file
		self.headers		= headers
		self.progress_cb	= progress_cb
		self.progress_cp	= progress_cp
		self.content_length_cb	= content_length_cb
		self.max_content_length	= max_content_length


	def call_progress_cb(self, value):
		if self.progress_cb is not None:
			self.progress_cb(value)


	def call_progress_cp(self, value=None):
		if self.progress_cp is not None:
			self.progress_cp(value)


	def call_content_length_cb(self, value):
		if self.content_length_cb is not None:
			self.content_length_cb(value)


class HttpRequest:

	def __init__(self, global_options=None):
		self._goptions = GlobalOptions() if global_options is None else global_options
		self._cache = None

		if self._goptions.cache_dir is not None:
			try:
				self._cache = Cache(self._goptions.cache_dir)
			except CacheError as e:
				pass


	def get(self, url, request_options=None):
		roptions = RequestOptions() if request_options is None else request_options
		if roptions.max_content_length is None or (roptions.max_content_length > self._goptions.max_content_length):
			roptions.max_content_length = self._goptions.max_content_length

		cached_res = self.check_cache(url, roptions)
		if cached_res:
			return cached_res

		res = None
		headers = self.combine_headers(roptions)

		if headers is None:
			res = self.exc_call(urlopen, roptions, url, timeout=self._goptions.timeout)
		else:
			res = self.exc_call(urlopen, roptions, Request(url, None, headers), timeout=self._goptions.timeout)

		out = self.get_outbuffer(roptions)
		content_length = self.get_content_length(res, roptions)

		if content_length is not None and content_length > roptions.max_content_length:		# take care of open buffers
			res.close()
			raise HttpError('max content length exceeded', err_type=HttpErrorType.size)

		content_read = self.read_response_chunks(res, out, content_length, roptions)
		
		if content_length is None:
			roptions.call_content_length_cb(content_read)

		roptions.call_progress_cp(-1 if content_length is None else None)

		res.close()

		self.cache_response(url, out, roptions)
		return self.close_outbuffer(out, roptions)
	
	
	def combine_headers(self, roptions):
		headers = None
		if self._goptions.headers is not None:
			headers = self._goptions.headers
		
		if roptions.headers is not None:
			if headers is not None:
				headers.update(roptions.headers)
			else:
				headers = roptions.headers

		return headers	

	def read_response_chunks(self, response, out, content_length, roptions):
		chunk = response.read(self._goptions.chunksize)
		content_read = 0.0

		while chunk:
			buf = bytes(chunk)
			out.write(buf)

			content_read += len(chunk)

			if roptions.max_content_length is not None and content_read > roptions.max_content_length:
				res.close()
				raise HttpError('max content length exceeded', err_type=HttpErrorType.size)

			if content_length is not None:
				roptions.call_progress_cb((content_read / content_length) * 100)
			else:
				roptions.call_progress_cb(-1)

			chunk = response.read(self._goptions.chunksize)

		return content_read


	def cache_response(self, url, out, roptions):
		if not roptions.nocache and self._cache is not None:
			out.seek(0)
			self._cache.add(url, out.read())


	def close_outbuffer(self, out, roptions):
		if roptions.save_filepath is None and roptions.open_file is None:
			out.seek(0)
			buf = out.read()
			out.close()
			if is_py3():
				buf = buf.decode(encoding='utf-8')
			return buf
		elif roptions.save_filepath is not None:
			out.close()
			return True


	def get_outbuffer(self, roptions):
		if roptions.save_filepath is None:
			if roptions.open_file is None:
				out = BytesIO()
			else:
				out = roptions.open_file
		else:
			out = open(roptions.save_filepath, 'wb+')

		return out


	def get_content_length(self, response, roptions):
		content_length = response.headers.getheader('Content-Length')
		if content_length is not None:
			content_length = int(content_length) 

			roptions.call_content_length_cb(content_length)

		return content_length


	def exc_call(self, func, roptions, *args, **kwargs):
		try:
			r = func(*args, **kwargs)
			return r

		except (URLError, UrllibHTTPError) as e:
			roptions.progress_cp()

			if type(e.reason) == socket.timeout:
				err_type = HttpErrorType.timeout
			else:
				err_type = HttpErrorType.other

			raise HttpError(str(e), code=None, err_type=err_type)


	def check_cache(self, url, request_options=None):
		roptions = RequestOptions() if request_options is None else request_options

		if not roptions.nocache and self._cache is not None:
			data = self._cache.get(url)
			if data is not None:
				roptions.call_content_length_cb(len(data))
				roptions.call_progress_cp('[cached]')

				if roptions.save_filepath is None:
					if is_py3():
						data = data.decode(encoding='utf-8')	
					return data
				else:
					with open(save_filepath, 'wb') as f:			# except
						f.write(data)
					return True
		else:
			return False


	def exists(self, url, timeout=10):
		try:
			res = urlopen(url, timeout=timeout)
			if res.code == 200:
				res.close()
				return True
		except (URLError, UrllibHTTPError) as e:
			return False

