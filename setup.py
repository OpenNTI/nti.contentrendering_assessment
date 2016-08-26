import codecs
from setuptools import setup, find_packages

VERSION = '0.0.0'

entry_points = {
	"z3c.autoinclude.plugin": [
		'target = nti.contentrendering',
	],
}

TESTS_REQUIRE = [
	'nose',
	'nose-timer',
	'nose-pudb',
	'nose-progressive',
	'nose2[coverage_plugin]',
	'pyhamcrest',
	'nti.testing'
]

setup(
	name = 'nti.contentrendering_assessment',
	version = VERSION,
	author = 'Jason Madden',
	author_email = 'jason@nextthought.com',
	description = "Support for assessment authoring",
	long_description = codecs.open('README.rst', encoding='utf-8').read(),
	license = 'Proprietary',
	keywords = 'Assessments Authoring Content',
	classifiers = [
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: Implementation :: CPython'
	],
	packages=find_packages('src'),
	package_dir={'': 'src'},
	namespace_packages=['nti'],
	tests_require=TESTS_REQUIRE,
	install_requires=[
		'setuptools',
		'Paste',
		'PasteDeploy',
		'persistent',
		'simplejson',
		'six',
		'zope.cachedescriptors',
		'zope.component',
		'zope.interface',
		'zope.mimetype',
		'zope.schema',
		'zope.security',
		'zope.traversing',
		'nti.assessment',
		'nti.contentfragments',
		'nti.contentrendering',
		'nti.externalization',
		'nti.mimetype',
		'nti.plasTeX',
		'nti.property'
	],
	extras_require={
		'test': TESTS_REQUIRE,
	},
	entry_points=entry_points
)
