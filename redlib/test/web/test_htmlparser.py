from unittest import TestCase, main as ut_main
import sys
from os.path import join as joinpath
from glob import glob
import os

from redlib.web.htmlparser import HtmlParser
from redlib.web.htmlparser_debugger import HtmlParserDebugger
from redlib.test.common import get_test_data_dir


class TestHtmlParser(TestCase):
	data_dir = joinpath(get_test_data_dir(), 'html')
	html_files = []

	@classmethod
	def setUpClass(cls):
		cls.html_files = glob(joinpath(cls.data_dir, '*.html'))


	def test_parser(self):
		hpd = HtmlParserDebugger(debug=False) #filter=[('class', 'left main')])

		for html_file in self.html_files:
			if html_file.split(os.sep)[-1].startswith('imgur'):	#currently, testing only imgur html
				parser = HtmlParser(skip_tags=['head'], debugger=hpd)

				with open(html_file, 'r') as f:
					parser.feed(f.read())

				etree = parser.etree
				image_divs = etree.findall('.//div[@class=\'post-image\']')

				self.assertEquals(len(image_divs), 10)


if __name__ == '__main__':
	ut_main()

