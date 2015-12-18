import re
import os
import sys

from . import sys_command, is_linux


def in_cron():
	return not os.isatty(sys.stdin.fileno()) or os.environ.get('TERM', None) is None



class CronDBusError(Exception):
	pass


class CronDBus:
	dbus_sba_var = 'DBUS_SESSION_BUS_ADDRESS'

	def __init__(self):
		if not is_linux():
			raise CronDBusError('cron/dbus only supported on linux')

		self._dbusd_environ = None
		self._remove_list = []


	def setup(self):
		if not self.cron_session():
			raise CronDBusError('not a cron session')

		if self.environ_var_set(self.dbus_sba_var):
			return

		uid = os.getuid()
		if uid is None:
			raise CronDBusError('could not get uid')

		dbusd_pids = []
		rc, pids = sys_command('pgrep dbus-daemon -u %s'%uid)

		if rc != 0:
			raise CronDBusError('could not get pid of dbus-daemon')

		dbusd_pids = pids.split()

		dbus_session_bus_addr = None
		dbus_session_bus_addr_re = re.compile(b'%s.*?\x00'%self.dbus_sba_var)

		for pid in dbusd_pids:
			self._dbusd_env = None
			with open('/proc/%s/environ'%pid, 'rb') as f:
				self._dbusd_env = f.read()

			matches = dbus_session_bus_addr_re.findall(self._dbusd_env)
			if len(matches) == 0:
				continue

			dbus_session_bus_addr = matches[0][matches[0].index('=') + 1:-1]

			os.environ[self.dbus_sba_var] = dbus_session_bus_addr
			self._remove_list.append(self.dbus_sba_var)
			break
	

	def remove(self):
		if not self.cron_session():
			raise CronDBusError('not a cron session')

		for var in self._remove_list:
			os.environ.pop(var)

		self._remove_list = []


	def add_var(self, var, overwrite=False):
		if self.environ_var_set(var) and not overwrite:
			return

		matches = re.compile(b'%s.*?\x00'%var).findall(self._dbusd_env)

		if len(matches) == 0:
			raise CronDBusError('%s not found in dbus-daemon environment'%var)
		else:
			val = matches[0][matches[0].index('=') + 1:-1]
			os.environ[var] = val
			self._remove_list.append(var)


	def cron_session(self):
		return in_cron()


	def environ_var_set(self, var):
		dsba = os.environ.get(var, None)
		if dsba is not None and len(dsba) > 1:
			return True


def uses_dbus_in_cron(func):
	if not is_linux():
		return func

	def new_func(*args, **kwargs):
		cd = CronDBus()
		cd.setup()
		result = func(*args, **kwargs)
		cd.remove()

	return new_func

