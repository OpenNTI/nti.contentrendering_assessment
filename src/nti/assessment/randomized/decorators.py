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

from nti.app.renderers.decorators import AbstractAuthenticatedRequestAwareDecorator

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
		generator = randomize()
		values = to_external_object(self.part.values)
		solutions = to_external_object(self.part.solutions)
		_shuffle_matching_part_solutions(generator, values, solutions)
		return solutions

@component.adapter(IQRandomizedMatchingPart)
class _QRandomizedMatchingPartDecorator(AbstractAuthenticatedRequestAwareDecorator):

	def _do_decorate_external(self, context, result):
		values = list(result['values'])
		generator = randomize(self.remoteUser)
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
		generator = randomize()
		choices = to_external_object(self.part.choices)
		solutions = to_external_object(self.part.solutions)
		_shuffle_multiple_choice_part_solutions(generator, choices, solutions)
		return solutions

@component.adapter(IQRandomizedMultipleChoicePart)
class _QRandomizedMultipleChoicePartDecorator(AbstractAuthenticatedRequestAwareDecorator):

	def _do_decorate_external(self, context, result):
		choices = list(result['choices'])
		generator = randomize(self.remoteUser)
		generator.shuffle(result['choices'])
		_shuffle_multiple_choice_part_solutions(generator, choices, result['solutions'])

# === multiple choice, multiple answer part

def _shuffle_multiple_choice_multiple_answer_part_solutions(generator, choices, ext_solutions):
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
		generator = randomize()
		choices = to_external_object(self.part.choices)
		solutions = to_external_object(self.part.solutions)
		_shuffle_multiple_choice_multiple_answer_part_solutions(generator, choices, solutions)
		return solutions

@component.adapter(IQRandomizedMultipleChoiceMultipleAnswerPart)
class _QRandomizedMultipleChoiceMultipleAnswerPartDecorator(AbstractAuthenticatedRequestAwareDecorator):

	def _do_decorate_external(self, context, result):
		choices = list(result['choices'])
		generator = randomize(self.remoteUser)
		generator.shuffle(result['choices'])
		_shuffle_multiple_choice_multiple_answer_part_solutions(generator, choices, result['solutions'])


# === asssed part

@interface.implementer(IExternalObjectDecorator)
@component.adapter(IQAssessedPart)
class _QAssessedPartDecorator(object):
	
	__metaclass__ = SingletonDecorator

	def decorateExternalObject(self, context, mapping):
		assessed_question = context.__parent__
		index = assessed_question.parts.index(context)
		
		question_id = assessed_question.questionId
		question = component.queryUtility(IQuestion, name=question_id)
		if question is None:
			return
		
		try:
			question_part = question.parts[index]
			if not IQRandomizedPart.providedBy(question_part):
				return
		except IndexError:
			return
