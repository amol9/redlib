from os.path import dirname, abspath, join as joinpath


def get_test_data_dir():
	return joinpath(dirname(abspath(__file__)), 'data')

