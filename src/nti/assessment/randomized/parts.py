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
from ..parts import QMatchingPart
from ..parts import QMultipleChoicePart

@interface.implementer(interfaces.IQRandomizedMatchingPart)
class QRandomizedMatchingPart(QMatchingPart):

	response_interface = None

	__external_class_name__ = "MatchingPart"
	mimeType = mime_type = "application/vnd.nextthought.assessment.randomizedmatchingpart"

	grader_interface = interfaces.IQRandomizedMatchingPartGrader

	def _unshuffle_response(self, response):
		generator = randomize()
		if generator is not None:
			values = list(self.values)
			original = {v:idx for idx, v in enumerate(values)}
			shuffled = {idx:v for idx, v in enumerate(shuffle_list(generator, values))}
			for k in list(response.keys()):
				idx = response[k]
				uidx = original.get(shuffled.get(idx), idx)
				response[k] = uidx
		return response

	def grade(self, response):
		self._unshuffle_response(response)
		return super(QRandomizedMatchingPart, self).grade(response)

@interface.implementer(interfaces.IQRandomizedMultipleChoicePart)
class QRandomizedMultipleChoicePart(QMultipleChoicePart):

	response_interface = None

	__external_class_name__ = "MultipleChoicePart"
	mimeType = mime_type = "application/vnd.nextthought.assessment.randomizedmultiplechoicepart"

	grader_interface = interfaces.IQRandomizedMultipleChoicePartGrader

# 	def _unshuffle_response(self, response):
# 		generator = randomize()
# 		if generator is not None:
# 			values = list(self.values)
# 			original = {v:idx for idx, v in enumerate(values)}
# 			shuffled = {idx:v for idx, v in enumerate(shuffle_list(generator, values))}
# 			for k in list(response.keys()):
# 				idx = response[k]
# 				uidx = original.get(shuffled.get(idx), idx)
# 				response[k] = uidx
# 		return response

	def grade(self, response):
		# from IPython.core.debugger import Tracer; Tracer()()
		# response = response.value if IQDictResponse.providedBy(response) else response
		# self._unshuffle_response(response)
		return super(QRandomizedMultipleChoicePart, self).grade(response)
