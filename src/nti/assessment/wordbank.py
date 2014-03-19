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
from zope.location.interfaces import ISublocations

import persistent

from nti.externalization.externalization import make_repr

from nti.utils.schema import SchemaConfigured
from nti.utils.schema import createDirectFieldProperties

from . import interfaces
from ._util import superhash

@interface.implementer(interfaces.IWordEntry)
class WordEntry(SchemaConfigured, persistent.Persistent, contained.Contained):
	createDirectFieldProperties(interfaces.IWordEntry)

	def __init__(self, *args, **kwargs):
		persistent.Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)

	def __eq__(self, other):
		try:
			return self is other or self.id == other.id
		except AttributeError:
			return NotImplemented

	__repr__ = make_repr()

	def __hash__(self):
		xhash = 47
		xhash ^= hash(self.id)
		return xhash

@interface.implementer(interfaces.IWordBank, ISublocations)
class WordBank(SchemaConfigured, persistent.Persistent, contained.Contained):
	createDirectFieldProperties(interfaces.IWordBank)

	def __init__(self, *args, **kwargs):
		persistent.Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)

	@property
	def words(self):
		return {x.word for x in self.entries.values()}

	def idOf(self, word):
		lower = word.lower()
		for wid, x in self.entries.items():
			if x.word.lower() == lower:
				return wid
		return None
	
	def contains_word(self, word):
		return self.idOf(word) != None

	def get(self, wid, default=None):
		result = self.entries.get(wid, default)
		return result

	def __setattr__(self, name, value):
		super(WordBank, self).__setattr__(name, value)
		if name == "entries" and value is not None:
			for x in self.entries.values():
				x.__parent__ = self  # take ownership

	def __contains__(self, wid):
		return wid in self.entries
	contains_id = __contains__

	def __getitem__(self, wid):
		return self.entries[wid]

	def __len__(self):
		return len(self.entries)
	
	def __iter__(self):
		return iter(self.entries.values())

	def __eq__(self, other):
		try:
			return self is other or (self.entries == other.entries
									 and self.unique == other.unique)
		except AttributeError:
			return NotImplemented

	def __hash__(self):
		return 47 + (superhash(self.entries) << 2) ^ superhash(self.unique)

	__repr__ = make_repr()

	def sublocations(self):
		for entry in self:
			yield entry
