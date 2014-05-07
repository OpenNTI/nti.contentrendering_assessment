#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface
from zope.container import contained

from nti.externalization.externalization import make_repr

from nti.utils.schema import SchemaConfigured
from nti.utils.schema import createDirectFieldProperties

from . import interfaces

@interface.implementer(interfaces.IQGrade)
class QGrade(SchemaConfigured, contained.Contained):
	createDirectFieldProperties(interfaces.IQGrade)

	__repr__ = make_repr()

	def __eq__(self, other):
		try:
			return self is other or (self.value == other.value and
									 self.response == other.response)
		except AttributeError:  # pragma: no cover
			return NotImplemented

	def __hash__(self):
		xhash = 47
		xhash ^= hash(self.value)
		return xhash
