from setuptools import setup

setup(
	name='termivision',
	version='1.0',
	license='WTFPL',
	py_modules=['termivision'],
	install_requires=[
	'Click',
	'colorama',
	'scrapy',
	'lxml',
	'requests'
	],
	entry_points='''
		[console_scripts]
		tv=termivision:cli
	'''
)