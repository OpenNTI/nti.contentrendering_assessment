#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from nti.contentrendering.interfaces import IRenderedBookExtractor


class IAssessmentExtractor(IRenderedBookExtractor):
    """
    Looks through the rendered book and extracts assessment information.
    """


class ILessonQuestionSetExtractor(IRenderedBookExtractor):
    """
    Looks through the rendered book and extracts the question sets in a lesson.
    """


class ILessonSurveyExtractor(IRenderedBookExtractor):
    """
    Looks through the rendered book and extracts the surveys in a lesson.
    """
