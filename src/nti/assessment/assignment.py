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
from zope.container import contained
from zope.mimetype import interfaces as mime_interfaces
from zope.annotation.interfaces import IAttributeAnnotatable

from persistent import Persistent # Why are these persistent exactly?

from nti.externalization.externalization import WithRepr

from nti.dataserver.datastructures import PersistentCreatedModDateTrackingObject
from nti.dataserver.datastructures import ContainedMixin

from nti.schema.field import SchemaConfigured
from nti.schema.fieldproperty import AdaptingFieldProperty
from nti.schema.fieldproperty import createDirectFieldProperties

from nti.utils.property import alias

from . import interfaces
from ._util import make_sublocations as _make_sublocations

@interface.implementer(interfaces.IQAssignmentPart,
					   mime_interfaces.IContentTypeAware,
					   IAttributeAnnotatable)
@WithRepr
class QAssignmentPart(SchemaConfigured,
					  contained.Contained,
					  Persistent):

	title = AdaptingFieldProperty(interfaces.IQAssignmentPart['title'])
	createDirectFieldProperties(interfaces.IQAssignmentPart)

	mime_type = 'application/vnd.nextthought.assessment.assignmentpart'


@interface.implementer(interfaces.IQAssignment,
					   mime_interfaces.IContentTypeAware,
					   IAttributeAnnotatable)
@WithRepr
class QAssignment(SchemaConfigured,
				  contained.Contained,
				  Persistent):

	title = AdaptingFieldProperty(interfaces.IQAssignment['title'])
	createDirectFieldProperties(interfaces.IQAssignment)

	available_for_submission_beginning = AdaptingFieldProperty(interfaces.IQAssignment['available_for_submission_beginning'])
	available_for_submission_ending = AdaptingFieldProperty(interfaces.IQAssignment['available_for_submission_ending'])

	mime_type = 'application/vnd.nextthought.assessment.assignment'


from zope.location.interfaces import ISublocations

@interface.implementer(interfaces.IQAssignmentSubmissionPendingAssessment,
					   mime_interfaces.IContentTypeAware,
					   IAttributeAnnotatable,
					   ISublocations)
@WithRepr
class QAssignmentSubmissionPendingAssessment(ContainedMixin,
											 SchemaConfigured,
											 PersistentCreatedModDateTrackingObject):
	createDirectFieldProperties(interfaces.IQBaseSubmission)
	createDirectFieldProperties(interfaces.IQAssignmentSubmissionPendingAssessment)
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
