#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Having to do with submitting external data for grading.

$Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.dataserver.datastructures import CreatedModDateTrackingObject

from nti.externalization.externalization import make_repr

from nti.utils.schema import SchemaConfigured

from . import interfaces

@interface.implementer(interfaces.IQuestionSubmission)
class QuestionSubmission(SchemaConfigured):
	questionId = None
	parts = ()

	__repr__ = make_repr()

@interface.implementer(interfaces.IQuestionSetSubmission)
class QuestionSetSubmission(SchemaConfigured):
	questionSetId = None
	questions = ()
	__repr__ = make_repr()


@interface.implementer(interfaces.IQAssignmentSubmission)
class AssignmentSubmission(CreatedModDateTrackingObject,SchemaConfigured):

	assignmentId = None
	parts = ()
	__repr__ = make_repr()
