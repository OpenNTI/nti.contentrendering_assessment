#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from . import randomize
from . import interfaces
from . import shuffle_list
from ..graders import MatchingPartGrader
from ..graders import MultipleChoiceGrader
from ..graders import MultipleChoiceMultipleAnswerGrader

@interface.implementer(interfaces.IQRandomizedMatchingPartGrader)
class RandomizedMatchingPartGrader(MatchingPartGrader):

	def _to_response_dict(self, the_dict):
		the_dict = MatchingPartGrader._to_int_dict(self, the_dict)
		generator = randomize()
		if generator is not None:
			values = list(self.part.values)
			original = {v:idx for idx, v in enumerate(values)}
			shuffled = {idx:v for idx, v in enumerate(shuffle_list(generator, values))}
			for k in list(the_dict.keys()):
				idx = int(the_dict[k])
				uidx = original.get(shuffled.get(idx), idx)
				the_dict[k] = uidx
		return the_dict

	response_converter = _to_response_dict

@interface.implementer(interfaces.IQRandomizedMultipleChoicePartGrader)
class RandomizedMultipleChoiceGrader(MultipleChoiceGrader):

	def _shuffle(self, the_value):
		generator = randomize()
		if generator is not None:
			the_value = int(the_value)
			choices = list(self.part.choices)
			original = {v:idx for idx, v in enumerate(choices)}
			shuffled = {idx:v for idx, v in enumerate(shuffle_list(generator, choices))}
			the_value = original[shuffled[the_value]]
		return the_value

	response_converter = _shuffle


@interface.implementer(interfaces.IQRandomizedMultipleChoiceMultipleAnswerPartGrader)
class RandomizedMultipleChoiceMultipleAnswerGrader(MultipleChoiceMultipleAnswerGrader):
	pass
