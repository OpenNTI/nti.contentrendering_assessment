#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Having to do with submitting external data for grading.

$Id$
"""
from __future__ import unicode_literals, print_function, absolute_import
__docformat__ = "restructuredtext en"

from zope import interface

from nti.utils.schema import SchemaConfigured
from nti.dataserver.datastructures import CreatedModDateTrackingObject

from nti.externalization.externalization import make_repr

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
