fron unittest import TestCase, main as ut_main

from redlib.system import CronDBus, CronDBusError


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
		os.environ = cronenv


	@classmethod
	def tearDownClass(cls):
		os.environ = cls._orig_env


	def test_dbus_sesssion_bus_address(self):
		cd = CronDBus()
		cd.setup()

		#check for proper session bus address

		dsba = os.environ.get(cd.dbus_session_var, None)
		self.assertIsNotNone(dsba)


	def test_add_var(self):
		cd = CronDBus()
		cd.setup()
		cd.add_var('GDMSESSION')
		cd.add_var('DISPLAY')

		gdmsession = os.environ.get('GDMSESSION', None)
		self.assertIsNotNone(gdmsession)
		#

		display = os.environ.get('DISPLAY', None)
		self.assertIsNotNone(display)
		#


	def test_remove(self):
		cd = CronDBus()
		cd.setup()
		cd.add_var('GDMSESSION')

		cd.remove()

		self.assertIsNone(os.environ.get(cd.dbus_session_var, None))
		self.assertIsNone(os.environ.get('GDMSESSION', None))
		self.assertNotIn(cd.dbus_session_var, os.environ.keys())
		self.assertNotIn('GDMSESSION', os.environ.keys())


	def test_dbus_use(self):
		cd = CronDBus()
		cd.setup()

		rc, _ = sys_command('xdpyinfo')
		self.assertEquals(rc, 0)


#for test cases where we are not in a cron environment
class TestCronDBus2(TestCase):

	def test_not_in_cron(self):
		cd = CronDBus()
		self.assertRaises(CronDBusError, cd.setup)
		self.assertRaises(CronDBusError, cd.remove)


if __name__ == '__main__':
	ut_main()

