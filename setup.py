import codecs
from setuptools import setup, find_packages

VERSION = '0.0.0'

entry_points = {
    "z3c.autoinclude.plugin": [
        'target = nti.contentrendering',
    ],
}

TESTS_REQUIRE = [
    'nti.testing',
    'zope.testrunner',
]


def _read(fname):
    with codecs.open(fname, encoding='utf-8') as f:
        return f.read()


setup(
    name='nti.contentrendering_assessment',
    version=VERSION,
    author='Jason Madden',
    author_email='jason@nextthought.com',
    description="Support for assessment authoring",
    long_description=(_read('README.rst') + '\n\n' + _read("CHANGES.rst")),
    url="https://github.com/NextThought/nti.contentrendering_assessment",
    license='Apache',
    keywords='assessments authoring content',
    classifiers=[
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
        'nti.assessment',
        'nti.contentfragments',
        'nti.contentrendering',
        'nti.externalization',
        'nti.mimetype',
        'nti.plasTeX',
        'nti.property',
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
    ],
    extras_require={
        'test': TESTS_REQUIRE,
    },
    entry_points=entry_points
)
