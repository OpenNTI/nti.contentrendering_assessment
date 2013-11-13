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

from dm.zope.schema.schema import SchemaConfigured

from nti.externalization.externalization import make_repr
from nti.utils.schema import createDirectFieldProperties

from . import interfaces
from ._util import superhash

@interface.implementer(interfaces.IQAssignmentPart,
					   mime_interfaces.IContentTypeAware,
					   IAttributeAnnotatable)
class QAssignmentPart(Persistent,
					  SchemaConfigured,
					  zope.container.contained.Contained):
	createDirectFieldProperties(interfaces.IQAssignmentPart)
	mime_type = 'application/vnd.nextthought.naassignmentpart'

	__repr__ = make_repr()

@interface.implementer(interfaces.IQAssignment,
					   mime_interfaces.IContentTypeAware,
					   IAttributeAnnotatable)
class QAssignment(Persistent,
				  SchemaConfigured,
				  zope.container.contained.Contained):
	mime_type = 'application/vnd.nextthought.naassignment'

	content = ''
	__repr__ = make_repr()

@interface.implementer(interfaces.IQAssignmentSubmissionPendingAssessment,
					   mime_interfaces.IContentTypeAware,
					   IAttributeAnnotatable)
class QAssignmentSubmissionPendingAssessment(Persistent,
											 SchemaConfigured,
											 zope.container.contained.Contained):
	# TODO: This object may need to be  nti_interfaces.IContained, nti_interfaces.ICreated, nti_interfaces.ILastModified
	mime_type = 'application/vnd.nextthought.naassignmentsubmissionpendingassessment'

	assignmentId = None
	parts = ()
	__repr__ = make_repr()

	__external_can_create__ = False
