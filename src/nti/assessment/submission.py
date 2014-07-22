#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Having to do with submitting external data for grading.

.. $Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface
from zope.container import contained
from zope.location.interfaces import ISublocations

from nti.dataserver.datastructures import ContainedMixin
from nti.dataserver.datastructures import PersistentCreatedModDateTrackingObject

from nti.externalization.externalization import WithRepr

from nti.schema.field import SchemaConfigured
from nti.schema.fieldproperty import createDirectFieldProperties

from . import interfaces
from ._util import make_sublocations as _make_sublocations

# NOTE that these objects are not Persistent. Originally this is
# because they were never intended for storage in the database; only
# the assessed versions were stored in the database.
# With assignments that have grading pending, however, they
# can be stored in the database.
# It IS NOT SAFE to change the superclass to be Persistent if there
# are already objects out there that are not Persistent (they cannot be
# unpickled)
# In general, these will be small objects consisting of the IQResponse
# subclasses, which already were persistent, so there should be
# negligible performance impact. Just remember they CANNOT
# be mutated.
# A side effect of the submission objects being persistent
# is that they get added to the user's _p_jar *before* being
# transformed; the transformed object may or may not
# be directly added.

@interface.implementer(interfaces.IQuestionSubmission,
					   ISublocations)
@WithRepr
class QuestionSubmission(SchemaConfigured, contained.Contained):
	createDirectFieldProperties(interfaces.IQBaseSubmission)
	createDirectFieldProperties(interfaces.IQuestionSubmission)

	sublocations = _make_sublocations()

@interface.implementer(interfaces.IQuestionSetSubmission,
					   ISublocations)
@WithRepr
class QuestionSetSubmission(SchemaConfigured, contained.Contained):
	createDirectFieldProperties(interfaces.IQBaseSubmission)
	createDirectFieldProperties(interfaces.IQuestionSetSubmission)

	sublocations = _make_sublocations('questions')

@interface.implementer(interfaces.IQAssignmentSubmission,
					   ISublocations)
@WithRepr
class AssignmentSubmission(ContainedMixin,
						   SchemaConfigured,
						   PersistentCreatedModDateTrackingObject):
	"""
	We do expect assignment submissions to be stored in the database
	for some period of time so it should be persistent. When you set
	the value of the ``parts`` attribute, you probably want to use
	a :class:`PersistentList` (because we can expect this value to be
	copied to the final assessed object; however, at this time
	that will still result in a partial data copy of the QuestionSetSubmission
	objects as they are not persistent).
	"""
	createDirectFieldProperties(interfaces.IQBaseSubmission)
	createDirectFieldProperties(interfaces.IQAssignmentSubmission)

	mime_type = 'application/vnd.nextthought.assessment.assignmentsubmission'

	sublocations = _make_sublocations()

	def __init__(self, *args, **kwargs):
		# schema configured is not cooperative
		ContainedMixin.__init__(self, *args, **kwargs)
		PersistentCreatedModDateTrackingObject.__init__(self)
