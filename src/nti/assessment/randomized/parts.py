#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from ..parts import QMatchingPart
from ..parts import QMultipleChoicePart
from ..parts import QMultipleChoiceMultipleAnswerPart

from .interfaces import IQRandomizedMatchingPart
from .interfaces import INonRandomizedMatchingPart
from .interfaces import INonRandomizedOrderingPart
from .interfaces import IQRandomizedMatchingPartGrader
from .interfaces import IQRandomizedOrderingPartGrader
from .interfaces import IQRandomizedMultipleChoicePart
from .interfaces import INonRandomizedMultipleChoicePart
from .interfaces import IQRandomizedMultipleChoicePartGrader
from .interfaces import IQRandomizedMultipleChoiceMultipleAnswerPart
from .interfaces import INonRandomizedMultipleChoiceMultipleAnswerPart
from .interfaces import IQRandomizedMultipleChoiceMultipleAnswerPartGrader

@interface.implementer(IQRandomizedMatchingPart)
class QRandomizedMatchingPart(QMatchingPart):

	response_interface = None

	__external_class_name__ = "MatchingPart"
	mimeType = mime_type = "application/vnd.nextthought.assessment.randomizedmatchingpart"

	grader_interface = IQRandomizedMatchingPartGrader
	
	nonrandomized_interface = INonRandomizedMatchingPart
	
@interface.implementer(IQRandomizedMatchingPart)
class QRandomizedOrderingPart(QRandomizedMatchingPart):

	__external_class_name__ = "OrderingPart"
	mimeType = mime_type = "application/vnd.nextthought.assessment.randomizedorderingpart"

	grader_interface = IQRandomizedOrderingPartGrader
	
	nonrandomized_interface = INonRandomizedOrderingPart
	
@interface.implementer(IQRandomizedMultipleChoicePart)
class QRandomizedMultipleChoicePart(QMultipleChoicePart):

	response_interface = None

	__external_class_name__ = "MultipleChoicePart"
	mimeType = mime_type = "application/vnd.nextthought.assessment.randomizedmultiplechoicepart"

	grader_interface = IQRandomizedMultipleChoicePartGrader
	
	nonrandomized_interface = INonRandomizedMultipleChoicePart

@interface.implementer(IQRandomizedMultipleChoiceMultipleAnswerPart)
class QRandomizedMultipleChoiceMultipleAnswerPart(QMultipleChoiceMultipleAnswerPart):

	response_interface = None

	__external_class_name__ = "MultipleChoiceMultipleAnswerPart"
	mimeType = mime_type = "application/vnd.nextthought.assessment.randomizedmultiplechoicemultipleanswerpart"

	grader_interface = IQRandomizedMultipleChoiceMultipleAnswerPartGrader
	
	nonrandomized_interface = INonRandomizedMultipleChoiceMultipleAnswerPart

