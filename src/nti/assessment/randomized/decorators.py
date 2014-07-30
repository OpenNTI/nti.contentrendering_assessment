#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component
from zope import interface

from dolmen.builtins.interfaces import IList
from dolmen.builtins.interfaces import ITuple

from nti.externalization.singleton import SingletonDecorator
from nti.externalization.externalization import to_external_object
from nti.externalization.interfaces import IExternalObjectDecorator

from . import randomize
from . import shuffle_list

from .interfaces import IQRandomizedPart
from .interfaces import IQRandomizedMatchingPart
from .interfaces import IQRandomizedMultipleChoicePart
from .interfaces import IQRandomizedMultipleChoiceMultipleAnswerPart

from ..interfaces import IQuestion
from ..interfaces import IQAssessedPart
from ..interfaces import IQPartSolutionsExternalizer

# === matching

def _shuffle_matching_part_solutions(generator, values, ext_solutions):
	original = {idx:v for idx, v in enumerate(values)}
	shuffled = {v:idx for idx, v in enumerate(shuffle_list(generator, values))}
	for solution in ext_solutions:
		value = solution['value']
		for k in list(value.keys()):
			idx = int(value[k])
			uidx = shuffled[original[idx]]
			value[k] = uidx

@interface.implementer(IQPartSolutionsExternalizer)
@component.adapter(IQRandomizedMatchingPart)
class _RandomizedMatchingPartSolutionsExternalizer(object):

	__slots__ = ('part',)

	def __init__(self, part):
		self.part = part

	def to_external_object(self):
		solutions = to_external_object(self.part.solutions)
		generator = randomize()
		if generator:
			values = to_external_object(self.part.values)
			_shuffle_matching_part_solutions(generator, values, solutions)
		return solutions

@interface.implementer(IExternalObjectDecorator)
@component.adapter(IQRandomizedMatchingPart)
class _QRandomizedMatchingPartDecorator(object):

	__metaclass__ = SingletonDecorator

	def decorateExternalObject(self, context, result):
		generator = randomize()
		if generator:
			values = list(result['values'])
			generator.shuffle(result['values'])
			_shuffle_matching_part_solutions(generator, values, result['solutions'])

# === multiple choice

def _shuffle_multiple_choice_part_solutions(generator, choices, ext_solutions):
	original = {idx:v for idx, v in enumerate(choices)}
	shuffled = {v:idx for idx, v in enumerate(shuffle_list(generator, choices))}
	for solution in ext_solutions:
		value = int(solution['value'])
		uidx = shuffled[original[value]]
		solution['value'] = uidx

@interface.implementer(IQPartSolutionsExternalizer)
@component.adapter(IQRandomizedMultipleChoicePart)
class _RandomizedMultipleChoicePartSolutionsExternalizer(object):

	__slots__ = ('part',)

	def __init__(self, part):
		self.part = part

	def to_external_object(self):
		solutions = to_external_object(self.part.solutions)
		generator = randomize()
		if generator:
			choices = to_external_object(self.part.choices)
			_shuffle_multiple_choice_part_solutions(generator, choices, solutions)
		return solutions

@interface.implementer(IExternalObjectDecorator)
@component.adapter(IQRandomizedMultipleChoicePart)
class _QRandomizedMultipleChoicePartDecorator(object):

	__metaclass__ = SingletonDecorator

	def decorateExternalObject(self, context, result):
		generator = randomize()
		if generator:
			choices = list(result['choices'])
			generator.shuffle(result['choices'])
			solutions = result['solutions']
			_shuffle_multiple_choice_part_solutions(generator, choices, solutions)

# === multiple choice, multiple answer part

def _shuffle_multiple_choice_multiple_answer_part_solutions(generator,
															choices,
															ext_solutions):
	original = {idx:v for idx, v in enumerate(choices)}
	shuffled = {v:idx for idx, v in enumerate(shuffle_list(generator, choices))}
	for solution in ext_solutions:
		value = solution['value']
		for pos, v in enumerate(value):
			idx = int(v)
			uidx = shuffled[original[idx]]
			value[pos] = uidx

@interface.implementer(IQPartSolutionsExternalizer)
@component.adapter(IQRandomizedMultipleChoiceMultipleAnswerPart)
class _RandomizedMultipleChoiceMultipleAnswerPartSolutionsExternalizer(object):

	__slots__ = ('part',)

	def __init__(self, part):
		self.part = part

	def to_external_object(self):
		solutions = to_external_object(self.part.solutions)
		generator = randomize()
		if generator:
			choices = to_external_object(self.part.choices)
			_shuffle_multiple_choice_multiple_answer_part_solutions(generator,
																	choices,
																	solutions)
		return solutions

@interface.implementer(IExternalObjectDecorator)
@component.adapter(IQRandomizedMultipleChoiceMultipleAnswerPart)
class _QRandomizedMultipleChoiceMultipleAnswerPartDecorator(object):

	__metaclass__ = SingletonDecorator

	def decorateExternalObject(self, context, result):
		generator = randomize()
		if generator:
			choices = list(result['choices'])
			generator.shuffle(result['choices'])
			_shuffle_multiple_choice_multiple_answer_part_solutions(generator,
																	choices,
																	result['solutions'])

# === assessed part

@interface.implementer(IExternalObjectDecorator)
@component.adapter(IQAssessedPart)
class _QAssessedPartDecorator(object):

	__metaclass__ = SingletonDecorator

	def decorateExternalObject(self, context, result):
		#from IPython.core.debugger import Tracer; Tracer()()
		assessed_question = context.__parent__
		if assessed_question is None:
			return

		index = assessed_question.parts.index(context)

		question_id = assessed_question.questionId
		question = component.queryUtility(IQuestion, name=question_id)
		if question is None:
			return # old question?

		try:
			question_part = question.parts[index]
		except IndexError:
			return

		if not IQRandomizedPart.providedBy(question_part):
			return

		generator = randomize()
		if not generator:
			return

		response = context.submittedResponse
		if ITuple.providedBy(response) or IList.providedBy(response):
			generator.shuffle(result['submittedResponse'])
