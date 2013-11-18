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
from zope.mimetype import interfaces as mime_interfaces
from zope.annotation.interfaces import IAttributeAnnotatable

from persistent import Persistent

from . import interfaces
from ._util import superhash

@interface.implementer(interfaces.IQuestion,
					   mime_interfaces.IContentTypeAware,
					   IAttributeAnnotatable)
class QQuestion(Persistent,
				contained.Contained):
	mime_type = 'application/vnd.nextthought.naquestion'

	content = ''
	parts = ()

	def __init__(self, content=None, parts=None):
		if content:
			self.content = content
		if parts:
			self.parts = parts

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
				   contained.Contained):
	mime_type = 'application/vnd.nextthought.naquestionset'

	questions = ()

	def __init__(self, questions=None):
		if questions:
			self.questions = questions

	def __eq__(self, other):
		return other is self or (isinstance(other, QQuestionSet)
								 and self.questions == other.questions)
	def __ne__(self, other):
		return not (self == other)

	def __hash__(self):
		return 47 + (superhash(self.questions) << 2)
