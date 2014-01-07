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
import zope.container.contained
from nti.dataserver.datastructures import PersistentCreatedModDateTrackingObject
from nti.dataserver.datastructures import ContainedMixin

from nti.externalization.externalization import make_repr

from nti.utils.schema import SchemaConfigured
from nti.utils.schema import createDirectFieldProperties

from . import interfaces

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


@interface.implementer(interfaces.IQuestionSubmission)
class QuestionSubmission(SchemaConfigured, zope.container.contained.Contained):
	createDirectFieldProperties(interfaces.IQuestionSubmission)

	__repr__ = make_repr()

@interface.implementer(interfaces.IQuestionSetSubmission)
class QuestionSetSubmission(SchemaConfigured, zope.container.contained.Contained):
	createDirectFieldProperties(interfaces.IQuestionSetSubmission)

	__repr__ = make_repr()


from zope.location.interfaces import ISublocations

@interface.implementer(interfaces.IQAssignmentSubmission,
					   ISublocations)
class AssignmentSubmission(PersistentCreatedModDateTrackingObject,
						   ContainedMixin,
						   SchemaConfigured):
	"""
	We do expect assignment submissions to be stored in the database
	for some period of time so it should be persistent. When you set
	the value of the ``parts`` attribute, you probably want to use
	a :class:`PersistentList` (because we can expect this value to be
	copied to the final assessed object; however, at this time
	that will still result in a partial data copy of the QuestionSetSubmission
	objects as they are not persistent).
	"""
	createDirectFieldProperties(interfaces.IQAssignmentSubmission)

	mime_type = 'application/vnd.nextthought.assessment.assignmentsubmission'

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
