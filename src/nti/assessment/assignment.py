#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The assignment related objects.

.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface
from zope.container.contained import Contained
from zope.mimetype.interfaces import IContentTypeAware
from zope.annotation.interfaces import IAttributeAnnotatable

from persistent import Persistent # Why are these persistent exactly?

from nti.dataserver.datastructures import ContainedMixin
from nti.dataserver.datastructures import PersistentCreatedModDateTrackingObject

from nti.externalization.externalization import WithRepr

from nti.schema.field import SchemaConfigured
from nti.schema.fieldproperty import AdaptingFieldProperty
from nti.schema.fieldproperty import createDirectFieldProperties

from nti.utils.property import alias

from .interfaces import IQAssignment
from .interfaces import IQAssignmentPart
from .interfaces import IQBaseSubmission
from .interfaces import IQAssignmentSubmissionPendingAssessment

from ._util import make_sublocations as _make_sublocations

@interface.implementer(IQAssignmentPart,
					   IContentTypeAware,
					   IAttributeAnnotatable)
@WithRepr
class QAssignmentPart(SchemaConfigured,
					  Contained,
					  Persistent):

	title = AdaptingFieldProperty(IQAssignmentPart['title'])
	createDirectFieldProperties(IQAssignmentPart)

	mime_type = 'application/vnd.nextthought.assessment.assignmentpart'

	def copy(self):
		result = self.__class__()
		result.title = self.title
		result.content = self.content
		result.auto_grade = self.auto_grade
		result.question_set = self.question_set.copy()
		return result

@interface.implementer(IQAssignment,
					   IContentTypeAware,
					   IAttributeAnnotatable)
@WithRepr
class QAssignment(SchemaConfigured,
				  Contained,
				  Persistent):

	title = AdaptingFieldProperty(IQAssignment['title'])
	createDirectFieldProperties(IQAssignment)

	available_for_submission_ending = AdaptingFieldProperty(IQAssignment['available_for_submission_ending'])
	available_for_submission_beginning = AdaptingFieldProperty(IQAssignment['available_for_submission_beginning'])

	mime_type = 'application/vnd.nextthought.assessment.assignment'

	def copy(self):
		result = self.__class__()
		result.title = self.title
		result.content = self.content
		result.category_name = self.category_name
		result.is_non_public = self.is_non_public
		result.parts = [part.copy() for part in self.parts]
		result.available_for_submission_ending = self.available_for_submission_ending
		result.available_for_submission_beginning = self.available_for_submission_beginning
		return result
	
from zope.location.interfaces import ISublocations

@interface.implementer(IQAssignmentSubmissionPendingAssessment,
					   IContentTypeAware,
					   IAttributeAnnotatable,
					   ISublocations)
@WithRepr
class QAssignmentSubmissionPendingAssessment(ContainedMixin,
											 SchemaConfigured,
											 PersistentCreatedModDateTrackingObject):
	createDirectFieldProperties(IQBaseSubmission)
	createDirectFieldProperties(IQAssignmentSubmissionPendingAssessment)
	# We get nti.dataserver.interfaces.IContained from ContainedMixin (containerId, id)
	# However, because these objects are new and not seen before, we can
	# safely cause name and id to be aliases
	__name__ = alias('id')

	mime_type = 'application/vnd.nextthought.assessment.assignmentsubmissionpendingassessment'
	__external_can_create__ = False

	sublocations = _make_sublocations()


	def __init__(self, *args, **kwargs):
		# schema configured is not cooperative
		ContainedMixin.__init__(self, *args, **kwargs)
		PersistentCreatedModDateTrackingObject.__init__(self)
