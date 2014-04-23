#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import functools

from zope import component
from zope import interface
from zope.container import contained
from zope.location.interfaces import ISublocations

import dolmen.builtins.interfaces

import persistent

from nti.contentfragments import interfaces as cfg_interfaces

from nti.externalization.externalization import make_repr

from nti.utils.property import Lazy
from nti.utils.maps import CaseInsensitiveDict

from nti.utils.schema import SchemaConfigured
from nti.utils.schema import createDirectFieldProperties

from . import interfaces
from ._util import superhash

@functools.total_ordering
@interface.implementer(interfaces.IWordEntry)
class WordEntry(SchemaConfigured, persistent.Persistent, contained.Contained):
	createDirectFieldProperties(interfaces.IWordEntry)
	
	__external_can_create__ = True
	mime_type = mimeType = 'application/vnd.nextthought.naqwordentry'

	def __init__(self, *args, **kwargs):
		persistent.Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)

	def __eq__(self, other):
		try:
			return self is other or self.wid == other.wid
		except AttributeError:
			return NotImplemented

	__repr__ = make_repr()

	def __hash__(self):
		xhash = 47
		xhash ^= hash(self.wid)
		return xhash

	def __lt__(self, other):
		try:
			return (self.word.lower(), self.lang.lower()) < (other.word.lower(), other.self.lang.lower())
		except AttributeError:
			return NotImplemented

	def __gt__(self, other):
		try:
			return  (self.word.lower(), self.lang.lower()) > (other.word.lower(), other.self.lang.lower())
		except AttributeError:
			return NotImplemented

@interface.implementer(interfaces.IWordBank, ISublocations)
class WordBank(SchemaConfigured, persistent.Persistent, contained.Contained):
	createDirectFieldProperties(interfaces.IWordBank)

	__external_can_create__ = True
	mime_type = mimeType = 'application/vnd.nextthought.naqwordbank'

	def __init__(self, *args, **kwargs):
		persistent.Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)

	@property
	def words(self):
		return {x.word for x in self.entries}

	@property
	def ids(self):
		return {x.wid for x in self.entries}

	def sorted(self):
		return sorted(self.entries)

	def idOf(self, word):
		return self._word_map.get(word, None)
	
	def contains_word(self, word):
		return self.idOf(word) != None
	
	def get(self, wid, default=None):
		result = self._id_map.get(wid, default)
		return result

	def __contains__(self, wid):
		return wid in self._id_map
	contains_id = __contains__

	def __getitem__(self, wid):
		return self._id_map[wid]

	def __len__(self):
		return len(self.entries)
	
	def __iter__(self):
		return iter(self.entries)

	def __eq__(self, other):
		try:
			return self is other or (self.ids == other.ids
									 and self.unique == other.unique)
		except AttributeError:
			return NotImplemented

	def __hash__(self):
		return 47 + (superhash(self.entries) << 2) ^ superhash(self.unique)

	__repr__ = make_repr()

	def __add__(self, other):
		unique = self.unique
		entries = set(self.entries)
		if other is not None:
			entries.update(other.entries)
			unique = unique and other.unique
		result = WordBank(entries=list(entries), unique=unique)
		return result

	def sublocations(self):
		for entry in self:
			yield entry

	@Lazy
	def _id_map(self):
		result = {x.wid:x for x in self.entries}
		return result

	@Lazy
	def _word_map(self):
		result = CaseInsensitiveDict()
		result.update({x.word:x.wid for x in self.entries})
		return result
					
@component.adapter(dolmen.builtins.interfaces.IList)
@interface.implementer(interfaces.IWordEntry)
def _wordentry_adapter(lst):
	result = WordEntry(wid=unicode(lst[0]), word=unicode(lst[1]))
	result.lang = unicode(lst[2]) if len(lst) > 2 and lst[2] else u'en'
	content = unicode(lst[3]) if len(lst) > 3 and lst[3] else result.word
	result.content = cfg_interfaces.HTMLContentFragment(content)
	return result

@component.adapter(dolmen.builtins.interfaces.IList)
@interface.implementer(interfaces.IWordBank)
def _wordbank_adapter(entries, unique=True):
	entries = {e.wid:e for e in entries}
	result = WordBank(entries=list(entries.values()), unique=unique)
	return result
