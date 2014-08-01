#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.schema.fieldproperty import createDirectFieldProperties

from .interfaces import IQuestionBank

from ..question import QQuestionSet

@interface.implementer(IQuestionBank)
class QQuestionBank(QQuestionSet):
	createDirectFieldProperties(IQuestionBank)
	
	__external_class_name__ = "QQuestionBank"
	mimeType = mime_type = 'application/vnd.nextthought.naquestionbank'
	
	def __eq__(self, other):
		try:
			return  super(QQuestionBank, self).__eq__(other) and \
					self.draw == other.draw
		except AttributeError:
			return NotImplemented
