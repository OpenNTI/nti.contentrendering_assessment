#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from . import interfaces
from ..parts import QMatchingPart
from ..parts import QMultipleChoicePart
from ..parts import QMultipleChoiceMultipleAnswerPart

@interface.implementer(interfaces.IQRandomizedMatchingPart)
class QRandomizedMatchingPart(QMatchingPart):

	response_interface = None

	__external_class_name__ = "MatchingPart"
	mimeType = mime_type = "application/vnd.nextthought.assessment.randomizedmatchingpart"

	grader_interface = interfaces.IQRandomizedMatchingPartGrader

@interface.implementer(interfaces.IQRandomizedMultipleChoicePart)
class QRandomizedMultipleChoicePart(QMultipleChoicePart):

	response_interface = None

	__external_class_name__ = "MultipleChoicePart"
	mimeType = mime_type = "application/vnd.nextthought.assessment.randomizedmultiplechoicepart"

	grader_interface = interfaces.IQRandomizedMultipleChoicePartGrader

@interface.implementer(interfaces.IQRandomizedMultipleChoiceMultipleAnswerPart)
class QRandomizedMultipleChoiceMultipleAnswerPart(QMultipleChoiceMultipleAnswerPart):

	response_interface = None

	__external_class_name__ = "MultipleChoiceMultipleAnswerPart"
	mimeType = mime_type = "application/vnd.nextthought.assessment.randomizedmultiplechoicemultipleanswerpart"

	grader_interface = interfaces.IQRandomizedMultipleChoiceMultipleAnswerPartGrader
