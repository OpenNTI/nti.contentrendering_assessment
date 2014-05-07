#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from zope.dottedname import resolve as dottedname

import unittest

class TestInterfaces(unittest.TestCase):

	def test_import_interfaces(self):
		dottedname.resolve('nti.assessment.interfaces')
