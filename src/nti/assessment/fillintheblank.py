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

from nti.utils.schema import createDirectFieldProperties

from . import parts
from . import question
from . import interfaces as asm_interfaces

@interface.implementer(asm_interfaces.IQFillInTheBlankPart)
class QFillInTheBlankPart(parts.QPart):
	pass

@interface.implementer(asm_interfaces.IQFillInTheBlankPartWithWordBank)
class QFillInTheBlankPartWithWordBank(QFillInTheBlankPart, contained.Contained):

	wordBank = None

	def __getattr__(self, name):
		result = super(QFillInTheBlankPartWithWordBank, self).__getattr__(name)
		if name == "wordBank" and result is None:
			result = getattr(self.__parent__, 'wordBank', None)
		return result

@interface.implementer(asm_interfaces.IQFillInTheBlankWithWordBankQuestion)
class QFillInTheBlankWithWordBankQuestion(question.QQuestion):
	createDirectFieldProperties(asm_interfaces.IQFillInTheBlankWithWordBankQuestion)

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
