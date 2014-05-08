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

from nti.externalization.externalization import to_external_object

from . import randomize
from . import shuffle_list
from . import interfaces as rand_interfaces
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
@component.adapter(rand_interfaces.IQRandomizedMatchingPart)
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

@component.adapter(rand_interfaces.IQRandomizedMatchingPart)
class QRandomizedMatchingPartDecorator(AbstractAuthenticatedRequestAwareDecorator):

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
@component.adapter(rand_interfaces.IQRandomizedMultipleChoicePart)
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

@component.adapter(rand_interfaces.IQRandomizedMultipleChoicePart)
class QRandomizedMultipleChoicePartDecorator(AbstractAuthenticatedRequestAwareDecorator):

	def _do_decorate_external(self, context, result):
		choices = list(result['choices'])
		generator = randomize(self.remoteUser)
		generator.shuffle(result['choices'])
		_shuffle_multiple_choice_part_solutions(generator, choices, result['solutions'])
