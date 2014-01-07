#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The assignment related objects.

$Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)


import zope.container.contained
from zope import interface
from zope.mimetype import interfaces as mime_interfaces
from zope.annotation.interfaces import IAttributeAnnotatable

from persistent import Persistent # Why are these persistent exactly?

from nti.externalization.externalization import make_repr

from nti.dataserver.datastructures import PersistentCreatedModDateTrackingObject
from nti.dataserver.datastructures import ContainedMixin

from nti.utils.schema import createDirectFieldProperties
from nti.utils.schema import SchemaConfigured
from nti.utils.schema import AdaptingFieldProperty

from nti.utils.property import alias

from . import interfaces

@interface.implementer(interfaces.IQAssignmentPart,
					   mime_interfaces.IContentTypeAware,
					   IAttributeAnnotatable)
class QAssignmentPart(Persistent,
					  SchemaConfigured,
					  zope.container.contained.Contained):
	title = AdaptingFieldProperty(interfaces.IQAssignmentPart['title'])
	createDirectFieldProperties(interfaces.IQAssignmentPart)

	mime_type = 'application/vnd.nextthought.assessment.assignmentpart'

	__repr__ = make_repr()

@interface.implementer(interfaces.IQAssignment,
					   mime_interfaces.IContentTypeAware,
					   IAttributeAnnotatable)
class QAssignment(Persistent,
				  SchemaConfigured,
				  zope.container.contained.Contained):

	title = AdaptingFieldProperty(interfaces.IQAssignment['title'])
	createDirectFieldProperties(interfaces.IQAssignment)

	available_for_submission_beginning = AdaptingFieldProperty(interfaces.IQAssignment['available_for_submission_beginning'])
	available_for_submission_ending = AdaptingFieldProperty(interfaces.IQAssignment['available_for_submission_ending'])

	mime_type = 'application/vnd.nextthought.assessment.assignment'

	__repr__ = make_repr()

from zope.location.interfaces import ISublocations

@interface.implementer(interfaces.IQAssignmentSubmissionPendingAssessment,
					   mime_interfaces.IContentTypeAware,
					   IAttributeAnnotatable,
					   ISublocations)
class QAssignmentSubmissionPendingAssessment(PersistentCreatedModDateTrackingObject,
											 SchemaConfigured,
											 ContainedMixin):
	createDirectFieldProperties(interfaces.IQAssignmentSubmissionPendingAssessment)
	# We get nti.dataserver.interfaces.IContained from ContainedMixin (containerId, id)
	# However, because these objects are new and not seen before, we can
	# safely cause name and id to be aliases
	__name__ = alias('id')

	mime_type = 'application/vnd.nextthought.assessment.assignmentsubmissionpendingassessment'
	__external_can_create__ = False

	__repr__ = make_repr()

	def sublocations(self):
		for part in self.parts:
			if hasattr(part, '__parent__'):
				if part.__parent__ is None:
					# XXX: HACK: Taking ownership because
					# of cross-database issues.
					logger.warn("XXX: HACK: Taking ownership of a sub-part")
					part.__parent__ = self
				if part.__parent__ is self:
					yield part
