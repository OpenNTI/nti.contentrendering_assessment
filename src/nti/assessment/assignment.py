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

from . import interfaces
from ._util import superhash

@interface.implementer(interfaces.IQAssignmentPart,
					   mime_interfaces.IContentTypeAware,
					   IAttributeAnnotatable)
class QAssignmentPart(Persistent,
					  SchemaConfigured,
					  zope.container.contained.Contained):

	mime_type = 'application/vnd.nextthought.naassignmentpart'

	auto_grade = True
	question_set = None
	content = ''

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
