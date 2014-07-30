#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Code related to the question interfaces.

.. $Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface
from zope.container.contained import Contained
from zope.location.interfaces import ISublocations
from zope.mimetype.interfaces import IContentTypeAware
from zope.annotation.interfaces import IAttributeAnnotatable

from persistent import Persistent

from nti.schema.field import SchemaConfigured
from nti.schema.fieldproperty import AdaptingFieldProperty
from nti.schema.fieldproperty import createDirectFieldProperties

from ._util import superhash

from .interfaces import IQuestion
from .interfaces import IQuestionSet
from .interfaces import IRandomizedQuestionSet
from .interfaces import IQFillInTheBlankWithWordBankQuestion

@interface.implementer(IQuestion,
					   IContentTypeAware,
					   IAttributeAnnotatable)
class QQuestion(Contained, SchemaConfigured, Persistent):
	createDirectFieldProperties(IQuestion)
	
	mimeType = mime_type = 'application/vnd.nextthought.naquestion'

	def __init__(self, *args, **kwargs):
		Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)
		
	def __eq__(self, other):
		try:
			return other is self or (isinstance(other, QQuestion)
								 	 and self.content == other.content
								 	 and self.parts == other.parts)
		except AttributeError:
			return NotImplemented

	def __ne__(self, other):
		return not (self == other)

	def __hash__(self):
		return 47 + (superhash(self.content) << 2) ^ superhash(self.parts)

@interface.implementer(IQuestionSet,
					   ISublocations,
					   IContentTypeAware,
					   IAttributeAnnotatable)
class QQuestionSet(Contained, SchemaConfigured, Persistent):
	createDirectFieldProperties(IQuestionSet)
	title = AdaptingFieldProperty(IQuestionSet['title'])

	mimeType = mime_type = 'application/vnd.nextthought.naquestionset'

	def __init__(self, *args, **kwargs):
		Persistent.__init__(self)
		SchemaConfigured.__init__(self, *args, **kwargs)
		
	def __eq__(self, other):
		try:
			return other is self or (isinstance(other, QQuestionSet)
								 	 and self.questions == other.questions
									 and self.title == other.title)
		except AttributeError:
			return NotImplemented

	def __ne__(self, other):
		return not (self == other)

	def __hash__(self):
		return 47 + (superhash(self.questions) << 2)
	
	def sublocations(self):
		for question in self.questions or ():
			yield question

@interface.implementer(IRandomizedQuestionSet)
class QRandomizedQuestionSet(QQuestionSet):
	createDirectFieldProperties(IRandomizedQuestionSet)
	
	__external_class_name__ = "QQuestionSet"
	mimeType = mime_type = 'application/vnd.nextthought.narandomizedquestionset'
	
	def __eq__(self, other):
		try:
			return 	super(QRandomizedQuestionSet, self).__eq__(other) and \
					self.limit == other.limit
		except AttributeError:
			return NotImplemented
	
@interface.implementer(IQFillInTheBlankWithWordBankQuestion, ISublocations)
class QFillInTheBlankWithWordBankQuestion(QQuestion):
	createDirectFieldProperties(IQFillInTheBlankWithWordBankQuestion)

	__external_class_name__ = "Question"
	mime_type = mimeType = 'application/vnd.nextthought.naquestionfillintheblankwordbank'

	def __setattr__(self, name, value):
		super(QFillInTheBlankWithWordBankQuestion, self).__setattr__(name, value)
		if name == "parts":
			for x in self.parts or ():
				x.__parent__ = self  # take ownership

	def __eq__(self, other):
		try:
			return	super(QFillInTheBlankWithWordBankQuestion, self).__eq__(other) and \
					(self is other or self.wordBank == other.wordBank)
		except AttributeError:
			return NotImplemented

	def sublocations(self):
		for part in self.parts or ():
			yield part
