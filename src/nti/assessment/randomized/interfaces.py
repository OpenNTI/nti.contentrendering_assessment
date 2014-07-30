#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

from nti.schema.field import Int

from ..interfaces import IQPart
from ..interfaces import IQuestionSet
from ..interfaces import IQMatchingPart
from ..interfaces import IQMatchingPartGrader
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
	"""
	An group of questions taken at random based on the taker.

	A maximum total of questions of the question set is drawn to be presented and evaluated. 
	"""
	
	max = Int(title="number of questions to be randomly drawn", min=1, required=True,
			  default=1)
	