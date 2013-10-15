#!/usr/bin/env python

from zope.dottedname import resolve as dottedname

def test_import_interfaces():
	dottedname.resolve('nti.assessment.interfaces')
