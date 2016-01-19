from unittest import TestCase, main as ut_main


class TestMakeAPI(TestCase):

	def test_import(self):
		from redlib.api import system

		system_dir = ['FrequencyError', 'PlatformError', 'Scheduler', 'get_scheduler', 'sys_command', 'CronDBus', 'is_linux', 'in_cron']
		for i in system_dir:
			self.assertIn(i, dir(system))


		from redlib.api import misc

		misc_dir = ['log', 'Logger', 'Retry', 'Singleton', 'trim_docstring', 'TextFile']
		for i in misc_dir:
			self.assertIn(i, dir(misc))



	def test_moves(self):
		from redlib.api.misc import trim
		
		self.assertEqual(trim.__name__, 'trim_docstring')



if __name__ == '__main__':
	ut_main()

