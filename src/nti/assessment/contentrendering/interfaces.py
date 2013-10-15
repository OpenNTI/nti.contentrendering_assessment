#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""


$Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from nti.contentrendering.interfaces import IRenderedBookExtractor

class IAssessmentExtractor(IRenderedBookExtractor):
	"""
	Looks through the rendered book and extracts assessment information.
	"""

class ILessonQuestionSetExtractor(IRenderedBookExtractor):
	"""
	Looks through the rendered book and extracts the question sets in a lesson.
	"""
