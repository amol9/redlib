from unittest import TestCase, main as ut_main

from redlib.net.urls import AbsUrl, RelUrl, UrlException, UrlParseException


class TestUrls(TestCase):
	def test_extend(self):
		def make_abs(source_url, rel_url):
			return AbsUrl(source_url).extend(rel_url)

		test_urls = [
			('http://localhost', 'test.jpg', 'http://localhost/test.jpg'),
			('http://localhost/a/', 'test.jpg', 'http://localhost/a/test.jpg'),
			('http://localhost/a/', './test.jpg', 'http://localhost/a/test.jpg'),
			('http://localhost/a/b/', './test.jpg', 'http://localhost/a/b/test.jpg'),
			('http://localhost/a/', '../test.jpg', 'http://localhost/test.jpg'),
			('http://localhost/a/b/', '../../test.jpg', 'http://localhost/test.jpg'),
			('http://localhost/a/b', '../test.jpg', 'http://localhost/test.jpg'),
			('http://localhost/a/b', '../../test.jpg', UrlException),
			('localhost/a/b', '../../test.jpg', UrlException),
			('//localhost/a/', 'test.jpg', UrlException),
			('http://sub.domain.com', 'test.jpg', 'http://sub.domain.com/test.jpg'),
			('https://sub.domain.com', '//domain.com/test.jpg', 'https://domain.com/test.jpg'),
			('http://sub.domain.com/a/b', '/test.jpg', 'http://sub.domain.com/test.jpg'),
			('http://sub.domain.com', '../test.jpg', UrlException),
			('http://sub.domain.com/a/b/', '../../test.jpg', 'http://sub.domain.com/test.jpg'),
			('https://sub.domain.com/a/b/', '../../test.jpg', 'https://sub.domain.com/test.jpg'),
			('http://sub.domain.com/a/b/c/d', '../../../../../test.jpg', UrlException),
			('http://sub.domain.com/', 'test.jpg', 'http://sub.domain.com/test.jpg'),
			('http://sub.domain.com/a', './test.jpg', 'http://sub.domain.com/test.jpg')
		]

		for item in test_urls:
			if isinstance(item[2], str):
				self.assertEquals(make_abs(item[0], item[1]), item[2])
			else:
				self.assertRaises(item[2], make_abs, item[0], item[1])


	def test_parse(self):
		test_urls = [				#valid, scheme, subdomain, hostname, tld, domain
			('http://google.com', 		True, 'http', None, 'google', 'com', 'google.com'),
			('http://1.www.google.co.in', 	True, 'http', '1.www', 'google', 'co.in', 'google.co.in'),
			('http://1.2.co.www.google.co.in', 	True, 'http', '1.2.co.www', 'google', 'co.in', 'google.co.in'),
			('http://www.reddit.com', 	True, 'http', 'www', 'reddit', 'com', 'reddit.com'),
			('http://localhost/test', 	True, 'http', None, 'localhost', None, 'localhost'),
			('http://localhost/test?p=1', 	True, 'http', None, 'localhost', None, 'localhost'),
			('https://gmail.com', 		True, 'https', None, 'gmail', 'com', 'gmail.com'),
			('google.com', 			False),
			('http://', 			False),
			('http://a', 			True, 'http', None, 'a', None, 'a'),
			('http://a.com', 		True, 'http', None, 'a', 'com', 'a.com'),
			('http://11', 			False),
			('http://11.com', 		True, 'http', None, '11', 'com', '11.com'),
			('http://192.168.0.100', 	True, 'http', None, '192.168.0.100', None, '192.168.0.100'),
			('http://192.168.0.', 		False),
			('http://192.168.0', 		False)
		]
		

		for item in test_urls:
			abs_url = AbsUrl(item[0])
			#abs_url.parse()

			self.assertEquals(abs_url.valid, item[1])
			if item[1]:
				self.assertEquals(abs_url.scheme, item[2])
				self.assertEquals(abs_url.subdomain, item[3])
				self.assertEquals(abs_url.hostname, item[4])
				self.assertEquals(abs_url.tld, item[5])
				self.assertEquals(abs_url.domain, item[6])


	def test_regex(self):
		regex = AbsUrl.regex

		test_urls = [
			('http://google.com', True, 'http', 'google.com', None, None),
			('http://1.www.google.co.in', True, 'http', '1.www.google.co.in', None, None),
			('http://www.reddit.com', True, 'http', 'www.reddit.com', None, None),
			('http://localhost/test', True, 'http', None, 'localhost', None),
			('https://gmail.com', True, 'https', 'gmail.com', None, None),
			('google.com', False),
			('http://', False),
			('http://a', True, 'http', None, 'a', None),
			('http://a.com', True, 'http', 'a.com', None, None),
			('http://11.com', True, 'http', '11.com', None, None),
			('http://11', False),
			('http://192.168.0.100', True, 'http', None, None, '192.168.0.100'),
			('http://192.168.0.', False),
			('http://192.168.0', False)
		]

		#import pdb; pdb.set_trace()

		for item in test_urls:
			match = regex.match(item[0])
			self.assertEquals(match is not None, item[1], msg='failed: %s'%item[0])
			if match:
				self.assertEquals(match.group(1), item[2], msg='scheme match failed: %s'%item[0])
				self.assertEquals(match.group(2), item[3], msg='authority match failed: %s'%item[0])
				self.assertEquals(match.group(3), item[4], msg='local hostname match failed: %s'%item[0])
				self.assertEquals(match.group(4), item[5], msg='ip address match failed: %s'%item[0])



if __name__ == '__main__':
	ut_main()
			
