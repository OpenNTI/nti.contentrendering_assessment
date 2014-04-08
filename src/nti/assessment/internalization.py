#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface
from zope import component

from nti.externalization import internalization
from nti.externalization import interfaces as ext_interfaces
from nti.externalization.datastructures import InterfaceObjectIO

from . import interfaces as asm_interfaces

@interface.implementer(ext_interfaces.IInternalObjectUpdater)
@component.adapter(asm_interfaces.IWordBank)
class _WordBankUpdater(object):

	__slots__ = ('obj',)

	def __init__(self, obj):
		self.obj = obj

	def updateFromExternalObject(self, parsed, *args, **kwargs):
		if 'entries' in parsed:
			new_entries = {}
			old_entries = parsed.pop('entries')
			for k, v in old_entries.items():
				factory = internalization.find_factory_for(v)
				assert factory is not None
				entry = factory()
				internalization.update_from_external_object(entry, v)
				new_entries[k] = entry
			parsed['entries'] = new_entries

		result = InterfaceObjectIO(
					self.obj,
					asm_interfaces.IWordBank).updateFromExternalObject(parsed)
		return result
