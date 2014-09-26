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
from zope.container.contained import Contained
from zope.location.interfaces import ISublocations
from zope.interface.common.mapping import IWriteMapping
from zope.interface.common.sequence import IFiniteSequence

from nti.dataserver.datastructures import ContainedMixin
from nti.dataserver.datastructures import PersistentCreatedModDateTrackingObject

from nti.externalization.representation import WithRepr

from nti.schema.field import SchemaConfigured
from nti.schema.fieldproperty import createDirectFieldProperties

from .interfaces import IQBaseSubmission
from .interfaces import IQuestionSubmission
from .interfaces import IQuestionSetSubmission
from .interfaces import IQAssignmentSubmission

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

@interface.implementer(IQuestionSubmission, ISublocations, IFiniteSequence)
@WithRepr
class QuestionSubmission(SchemaConfigured, Contained):
	createDirectFieldProperties(IQBaseSubmission)
	createDirectFieldProperties(IQuestionSubmission)

	sublocations = _make_sublocations()

	def __getitem__(self, idx):
		return self.parts[idx]

	def __setitem__(self, idx, value):
		self.parts[idx] = value
		
	def __delitem__(self, idx):
		del self.parts[idx]
	
	def __len__(self):
		return len(self.parts)
	
@interface.implementer(IQuestionSetSubmission, ISublocations, IWriteMapping)
@WithRepr
class QuestionSetSubmission(SchemaConfigured, Contained):
	createDirectFieldProperties(IQBaseSubmission)
	createDirectFieldProperties(IQuestionSetSubmission)

	sublocations = _make_sublocations('questions')
	
	def get(self, key, default=None):
		try:
			return self[key]
		except KeyError:
			return default
		
	def index(self, key):
		for idx, question in enumerate(self.questions or ()):
			if question.questionId == key:
				return idx
		return -1

	def __getitem__(self, key):
		idx = self.index(key)
		if idx == -1:
			raise KeyError(key)
		return self.questions[idx]
	
	def __delitem__(self, key):
		idx = self.index(key)
		if idx == -1:
			raise KeyError(key)
		del self.questions[idx]
		
	def __setitem__(self, key, value):
		assert key == value.questionId
		idx = self.index(key)
		if idx == -1:
			self.questions.append(value)
		else:
			self.questions[idx] = value

	def __contains__(self, key):
		return self.index(key) != -1
		
	def __len__(self):
		return len(self.questions)

@interface.implementer(IQAssignmentSubmission, ISublocations, IWriteMapping)
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
	createDirectFieldProperties(IQBaseSubmission)
	createDirectFieldProperties(IQAssignmentSubmission)

	mime_type = 'application/vnd.nextthought.assessment.assignmentsubmission'

	sublocations = _make_sublocations()

	def __init__(self, *args, **kwargs):
		# schema configured is not cooperative
		ContainedMixin.__init__(self, *args, **kwargs)
		PersistentCreatedModDateTrackingObject.__init__(self)
	
	def index(self, key):
		for idx, question_set in enumerate(self.parts or ()):
			if question_set.questionSetId == key:
				return idx
		return -1

	def get(self, key, default=None):
		try:
			return self[key]
		except KeyError:
			return default

	def __getitem__(self, key):
		idx = self.index(key)
		if idx == -1:
			raise KeyError(key)
		return self.parts[idx]
	
	def __delitem__(self, key):
		idx = self.index(key)
		if idx == -1:
			raise KeyError(key)
		del self.parts[idx]
		
	def __setitem__(self, key, value):
		assert key == value.questionSetId
		idx = self.index(key)
		if idx == -1:
			self.parts.append(value)
		else:
			self.parts[idx] = value

	def __contains__(self, key):
		return self.index(key) != -1
	
	def __len__(self):
		return len(self.parts)
