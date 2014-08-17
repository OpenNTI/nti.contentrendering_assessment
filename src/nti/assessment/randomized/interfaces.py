#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

from zope import interface

from nti.schema.field import Int
from nti.schema.field import Object
from nti.schema.field import ListOrTuple

from ..interfaces import IQPart
from ..interfaces import IQuestionSet
from ..interfaces import IQMatchingPart
from ..interfaces import IQOrderingPart
from ..interfaces import IQMatchingPartGrader
from ..interfaces import IQOrderingPartGrader
from ..interfaces import IQMultipleChoicePart
from ..interfaces import IQMultipleChoicePartGrader
from ..interfaces import IQMultipleChoiceMultipleAnswerPart
from ..interfaces import IQMultipleChoiceMultipleAnswerPartGrader

# parts

class IQRandomizedPart(IQPart):
	pass

# matching part

class IQRandomizedMatchingPart(IQRandomizedPart, IQMatchingPart):
	pass

class IQRandomizedMatchingPartGrader(IQMatchingPartGrader):
	pass

# ordering

class IQRandomizedOrderingPart(IQRandomizedPart, IQOrderingPart):
	pass

class IQRandomizedOrderingPartGrader(IQOrderingPartGrader):
	pass

# multiple choice

class IQRandomizedMultipleChoicePart(IQRandomizedPart, IQMultipleChoicePart):
	pass

class IQRandomizedMultipleChoicePartGrader(IQMultipleChoicePartGrader):
	pass


# multiple choice, multiple answer

class IQRandomizedMultipleChoiceMultipleAnswerPart(IQRandomizedPart,
												   IQMultipleChoiceMultipleAnswerPart):
	pass

class IQRandomizedMultipleChoiceMultipleAnswerPartGrader(IQMultipleChoiceMultipleAnswerPartGrader):
	pass

# question set

class IRandomizedQuestionSet(IQuestionSet):
	pass

class IQuestionIndexRange(interface.Interface):
	start = Int(title="start index range", min=0, required=True)
	end = Int(title="end index range", min=0, required=True)
	

class IQuestionBank(IQuestionSet):
	"""
	An group of questions taken at random based on the taker.

	A maximum total of questions of the question set is drawn to be presented and evaluated. 
	"""
	
	draw = Int(	title="number of questions to be randomly drawn", min=1, 
				required=True, default=1)

	ranges = ListOrTuple(Object(IQuestionIndexRange), title="Question index ranges", 
						 required=False, default=())

	def copy(questions=None, ranges=None):
		"""
		make a copy of this object w/ possibly new questions and/or ranges
		"""

class INonRandomizedQuestionBank(IQuestionBank):
	"""
	marker interface to avoid randomizing an obejct
	"""
	