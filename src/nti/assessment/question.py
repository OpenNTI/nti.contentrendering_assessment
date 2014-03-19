#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Code related to the question interfaces.

$Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface
from zope.container import contained
from zope.location.interfaces import ISublocations
from zope.mimetype import interfaces as mime_interfaces
from zope.annotation.interfaces import IAttributeAnnotatable

from persistent import Persistent

from nti.utils.schema import createDirectFieldProperties
from nti.utils.schema import SchemaConfigured
from nti.utils.schema import AdaptingFieldProperty

from . import interfaces
from ._util import superhash

@interface.implementer(interfaces.IQuestion,
					   mime_interfaces.IContentTypeAware,
					   IAttributeAnnotatable)
class QQuestion(Persistent,
				SchemaConfigured,
				contained.Contained):
	mime_type = 'application/vnd.nextthought.naquestion'

	createDirectFieldProperties(interfaces.IQuestion)

	def __eq__(self, other):
		return other is self or (isinstance(other, QQuestion)
								 and self.content == other.content
								 and self.parts == other.parts)
	def __ne__(self, other):
		return not (self == other)

	def __hash__(self):
		return 47 + (superhash(self.content) << 2) ^ superhash(self.parts)

@interface.implementer(interfaces.IQuestionSet,
					   mime_interfaces.IContentTypeAware,
					   IAttributeAnnotatable)
class QQuestionSet(Persistent,
				   SchemaConfigured,
				   contained.Contained):
	mime_type = 'application/vnd.nextthought.naquestionset'

	title = AdaptingFieldProperty(interfaces.IQuestionSet['title'])
	createDirectFieldProperties(interfaces.IQuestionSet)

	def __eq__(self, other):
		return other is self or (isinstance(other, QQuestionSet)
								 and self.questions == other.questions
								 and self.title == other.title)
	def __ne__(self, other):
		return not (self == other)

	def __hash__(self):
		return 47 + (superhash(self.questions) << 2)

@interface.implementer(interfaces.IQFillInTheBlankWithWordBankQuestion, ISublocations)
class QFillInTheBlankWithWordBankQuestion(QQuestion):

	__external_class_name__ = "Question"
	mime_type = mimeType = 'application/vnd.nextthought.naquestionfillintheblankwordbank'

	createDirectFieldProperties(interfaces.IQFillInTheBlankWithWordBankQuestion)

	def __setattr__(self, name, value):
		super(QFillInTheBlankWithWordBankQuestion, self).__setattr__(name, value)
		if name == "parts":
			for x in self.parts or ():
				x.__parent__ = self  # take ownership

	def __eq__(self, other):
		return	super(QFillInTheBlankWithWordBankQuestion, self).__eq__(other) and \
				(self is other or self.wordBank == other.wordBank)

	def sublocations(self):
		for part in self.parts or ():
			yield part
