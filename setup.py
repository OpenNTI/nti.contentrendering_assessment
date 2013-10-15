from setuptools import setup, find_packages
import codecs

VERSION = '0.0.0'

entry_points = {
}

setup(
    name = 'nti.assessment',
    version = VERSION,
    author = 'Jason Madden',
    author_email = 'jason@nextthought.com',
    description = "Support for automated assessments",
    long_description = codecs.open('README.rst', encoding='utf-8').read(),
    license = 'Proprietary',
    keywords = 'pyramid preference',
    #url = 'https://github.com/NextThought/nti.nose_traceback_info',
    classifiers = [
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
		'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        ],
	packages=find_packages('src'),
	package_dir={'': 'src'},
	namespace_packages=['nti',],
	install_requires=[
		'setuptools',
		'persistent',
		'dm.zope.schema',
		'zope.interface',
		'zope.datetime',
		'nti.plasTeX',
		'nti.openmath',

		# NOTE: We actually depend on nti.dataserver
		# as well, but for the sake of legacy
		# deployments, we do not yet declare that.
		# We will declare it when everything is in
		# buildout:
		# 'nti.utils.schema',
		# 'nti.externalization',
		# 'nti.contentfragments.schema'
	],
	entry_points=entry_points
)
