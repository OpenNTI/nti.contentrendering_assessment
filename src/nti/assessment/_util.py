#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

_marker = object()

from nti.externalization.externalization import WithRepr

from nti.schema.schema import EqHash

@EqHash('value',
		superhash=True)
@WithRepr
class TrivialValuedMixin(object):

	value = None

	def __init__(self, *args, **kwargs):
		# The contents of ``self.value`` come from either the first arg
		# (if positional args are given) or the kwarg name such.

		if args:
			value = args[0]
		elif 'value' in kwargs:
			value = kwargs.get('value')
		else:
			value = None

		# Avoid the appearance of trying to pass args to object.__init__ to avoid a Py3K warning
		init = super(TrivialValuedMixin, self).__init__
		if getattr(init, '__objclass__', None) is not object:  # object's init is a method-wrapper
			init(*args, **kwargs)

		if value is not None:
			self.value = value

	def __str__(self):
		return str(self.value)

def make_sublocations(child_attr='parts'):
	def sublocations(self):
		for part in getattr(self, child_attr, None) or ():
			if hasattr(part, '__parent__'):
				if part.__parent__ is None:
					# XXX: HACK: Taking ownership because of cross-database issues.
					logger.warn("XXX: HACK: Taking ownership of a sub-part")
					part.__parent__ = self
				if part.__parent__ is self:
					yield part
	return sublocations
