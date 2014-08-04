#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import functools

from zope import interface
from zope.container.contained import Contained
from zope.location.interfaces import ISublocations

from persistent import Persistent

from nti.contentfragments import interfaces as cfg_interfaces

from nti.externalization.externalization import WithRepr

from nti.schema.schema import EqHash
from nti.schema.field import SchemaConfigured
from nti.schema.fieldproperty import createDirectFieldProperties

from nti.utils.property import Lazy
from nti.utils.property import CachedProperty
from nti.utils.maps import CaseInsensitiveDict

from .interfaces import IWordBank
from .interfaces import IWordEntry

@functools.total_ordering
@interface.implementer(IWordEntry)
@WithRepr
@EqHash("wid") # XXX: The word isn't included?
class WordEntry(Contained, SchemaConfigured, Persistent):

	wid = None
	word = None
	lang = None

	createDirectFieldProperties(IWordEntry)

	__external_can_create__ = True
	mime_type = mimeType = 'application/vnd.nextthought.naqwordentry'

	def __init__(self, *args, **kwargs):
		Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)

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

@interface.implementer(IWordBank, ISublocations)
@WithRepr
@EqHash("ids", "unique")
class WordBank(Contained, SchemaConfigured, Persistent):

	entries = ()
	unique = None

	createDirectFieldProperties(IWordBank)

	__external_can_create__ = True
	mime_type = mimeType = 'application/vnd.nextthought.naqwordbank'

	def __init__(self, *args, **kwargs):
		Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)

	@CachedProperty('entries')
	def words(self):
		return frozenset({x.word for x in self.entries})

	@CachedProperty('entries')
	def ids(self):
		return frozenset({x.wid for x in self.entries})

	def sorted(self):
		return sorted(self.entries)

	def idOf(self, word):
		return self._word_map.get(str(word), None) if word is not None else None

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
		result = {x.wid: x for x in self.entries}
		return result

	@Lazy
	def _word_map(self):
		result = CaseInsensitiveDict()
		result.update({x.word: x.wid for x in self.entries})
		return result

@interface.implementer(IWordEntry)
def _wordentry_adapter(sequence):
	result = WordEntry(wid=unicode(sequence[0]), word=unicode(sequence[1]))
	result.lang = unicode(sequence[2]) if len(sequence) > 2 and sequence[2] else u'en'
	content = unicode(sequence[3]) if len(sequence) > 3 and sequence[3] else result.word
	result.content = cfg_interfaces.HTMLContentFragment(content)
	return result

@interface.implementer(IWordBank)
def _wordbank_adapter(entries, unique=True):
	entries = {e.wid:e for e in entries}
	result = WordBank(entries=list(entries.values()), unique=unique)
	return result
