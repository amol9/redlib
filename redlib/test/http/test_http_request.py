from unittest import TestCase, main as ut_main

from redlib.api.http import HttpRequest, RequestOptions, GlobalOptions, HttpError
from redlib.api.prnt import prints, ColumnPrinter, format_size


class TestHttpRequest(TestCase):

	def test_simple_get(self):
		hr = HttpRequest()
		hr.get('http://i.imgur.com/p5j2s79.jpg')


	def test_progress(self):
		def progress_cb(p):
			prints('\r%d'%p)

		print('')
		ro = RequestOptions(progress_cb=progress_cb)
		hr = HttpRequest()
		hr.get('http://i.imgur.com/eFglueb.jpg', ro)


	def test_with_column_printer(self):
		cp = ColumnPrinter(cols=[15, 15, 10])
		cb = cp.printf('getting image', progress_col=2, col_cb=True)

		hr = HttpRequest()
		clc = lambda l : cb.col_cb(1, format_size(l))
		pcb = lambda p : cb.progress_cb('%.2f %%'%p)
		ro = RequestOptions(progress_cb=pcb, progress_cp=cb.progress_cp, content_length_cb=clc)
		hr.get('http://i.imgur.com/eFglueb.jpg', ro)


if __name__ == '__main__':
	ut_main()

