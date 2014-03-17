#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
$Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface
from zope.container import contained

import persistent

from nti.externalization.externalization import make_repr

from nti.utils.schema import SchemaConfigured
from nti.utils.schema import createDirectFieldProperties

from . import interfaces
from ._util import superhash

@interface.implementer(interfaces.IWordBankEntry)
class WordBankEntry(SchemaConfigured, contained.Contained, persistent.Persistent):
	createDirectFieldProperties(interfaces.IWordBankEntry)

	def __eq__(self, other):
		try:
			return self is other or (self.id == other.id)
		except AttributeError:
			return NotImplemented

	__repr__ = make_repr()

	def __hash__(self):
		xhash = 47
		xhash ^= hash(self.id)
		return xhash

@interface.implementer(interfaces.IWordBank)
class WordBank(SchemaConfigured, contained.Contained, persistent.Persistent):
	createDirectFieldProperties(interfaces.IWordBank)

	def __setattr__(self, name, value):
		super(WordBank, self).__setattr__(name, value)
		if name == "entries":
			for x in self.entries or ():
				x.__parent__ = self  # take ownership

	@property
	def words(self):
		return {x.word for x in self.entries}

	__repr__ = make_repr()

	def __eq__(self, other):
		try:
			return self is other or (self.entries == other.entries
									 and self.unique == other.unique)
		except AttributeError:
			return NotImplemented

	def __hash__(self):
		return 47 + (superhash(self.entries) << 2) ^ superhash(self.unique)

	def sublocations(self):
		for entry in self.entries or ():
			yield entry
