from unittest import TestCase, main as ut_main
import os
import subprocess

from redlib.system.crondbus import CronDBus, CronDBusError, sys_command


cronenv = {
		'LANGUAGE'	: 'en_IN:en',
		'HOME'		: '/home/amol',
		'LOGNAME'	: 'amol',
		'PATH'		: '/usr/bin:/bin',
		'LANG'		: 'en_IN',
		'SHELL'		: '/bin/sh',
		'PWD'		: '/home/amol'
	}


class TestCronDBus(TestCase):

	@classmethod
	def setUpClass(cls):
		cls._orig_env = os.environ


	@classmethod
	def tearDownClass(cls):
		os.environ = cls._orig_env

	
	def setUp(self):
		os.environ = cronenv.copy()


	def test_dbus_sesssion_bus_address(self):
		cd = CronDBus()
		cd.setup()

		dsba = os.environ.get(cd.dbus_sba_var, None)
		self.assertIsNotNone(dsba)
		self.assertTrue(dsba.startswith('unix:abstract=/tmp/dbus-'))


	def test_add_var(self):
		cd = CronDBus()
		cd.setup()
		cd.add_var('GDMSESSION')
		cd.add_var('DISPLAY')

		gdmsession = os.environ.get('GDMSESSION', None)
		self.assertIsNotNone(gdmsession)
		self.assertGreater(len(gdmsession), 1)

		display = os.environ.get('DISPLAY', None)
		self.assertIsNotNone(display)
		self.assertGreater(len(display), 1)


	def test_remove(self):
		cd = CronDBus()
		cd.setup()
		cd.add_var('GDMSESSION')

		cd.remove()

		self.assertIsNone(os.environ.get(cd.dbus_sba_var, None))
		self.assertIsNone(os.environ.get('GDMSESSION', None))
		self.assertNotIn(cd.dbus_sba_var, os.environ.keys())
		self.assertNotIn('GDMSESSION', os.environ.keys())


	def test_dbus_use(self):
		cd = CronDBus()

		def use_dbus():
			devnull = open(os.devnull, 'w')
			p = subprocess.Popen('xdpyinfo', env=os.environ, stdout=devnull, stderr=devnull)
			p.wait()
			return p.returncode

		self.assertNotEquals(use_dbus(), 0)

		cd.setup()
		cd.add_var('DISPLAY')
		self.assertEquals(use_dbus(), 0)


#for test cases where we are not in a cron environment
class TestCronDBus2(TestCase):

	def test_not_in_cron(self):
		cd = CronDBus()
		#self.assertRaises(CronDBusError, cd.setup)
		#self.assertRaises(CronDBusError, cd.remove)


if __name__ == '__main__':
	ut_main()

