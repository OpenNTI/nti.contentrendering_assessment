#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

from ..interfaces import IQPart
from ..interfaces import IQMatchingPart
from ..interfaces import IQMatchingPartGrader
from ..interfaces import IQMultipleChoicePart
from ..interfaces import IQMultipleChoicePartGrader
from ..interfaces import IQMultipleChoiceMultipleAnswerPart
from ..interfaces import IQMultipleChoiceMultipleAnswerPartGrader

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

class IQRandomizedMultipleChoiceMultipleAnswerPart(IQRandomizedPart, IQMultipleChoiceMultipleAnswerPart):
	pass

class IQRandomizedMultipleChoiceMultipleAnswerPartGrader(IQMultipleChoiceMultipleAnswerPartGrader):
	pass
