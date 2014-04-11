#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
$Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface
from zope.container import contained

import dolmen.builtins.interfaces

import persistent

from nti.externalization.externalization import make_repr

from nti.utils.schema import SchemaConfigured
from nti.utils.schema import createDirectFieldProperties

from . import interfaces

@interface.implementer(interfaces.IRegEx)
class RegEx(SchemaConfigured, persistent.Persistent, contained.Contained):
	createDirectFieldProperties(interfaces.IRegEx)
	
	__external_can_create__ = True
	mime_type = mimeType = 'application/vnd.nextthought.naqregex'

	def __init__(self, *args, **kwargs):
		persistent.Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)

	def __eq__(self, other):
		try:
			return self is other or self.pattern == other.pattern
		except AttributeError:
			return NotImplemented

	__repr__ = make_repr()

	def __hash__(self):
		xhash = 47
		xhash ^= hash(self.pattern)
		return xhash
					
@component.adapter(dolmen.builtins.interfaces.IString)
@interface.implementer(interfaces.IRegEx)
def _regex_adapter(pattern, maxchars=10):
	result = RegEx(pattern=pattern, maxchars=maxchars)
	return result
