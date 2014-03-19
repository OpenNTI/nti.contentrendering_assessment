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
from zope import component
from zope.container import contained
from zope.location.interfaces import ISublocations

from persistent import Persistent
from persistent.list import PersistentList

from nti.externalization.externalization import make_repr

from nti.utils.schema import InvalidValue
from nti.utils.schema import SchemaConfigured
from nti.utils.schema import createDirectFieldProperties

# EWW...but we need to be IContained in order to be stored
# in container data structures.
# We also want to be ILastModified
# so that we can cheaply store and access lastmodified times
# without going through the expense of ZopeDublinCore (since we expect no other
# annotations and no mutability)
from nti.dataserver import interfaces as nti_interfaces
from nti.dataserver.datastructures import ContainedMixin

from . import interfaces
from ._util import superhash
from ._util import make_sublocations as _make_sublocations

@interface.implementer(interfaces.IQAssessedPart, ISublocations)
class QAssessedPart(SchemaConfigured, contained.Contained, Persistent):
	createDirectFieldProperties(interfaces.IQAssessedPart)
	__external_can_create__ = False

	def __eq__(self, other):
		try:
			return self is other or (self.submittedResponse == other.submittedResponse
									 and self.assessedValue == other.assessedValue)
		except AttributeError: # pragma: no cover
			return NotImplemented

	def __ne__(self, other):
		return not self == other

	__repr__ = make_repr()

	def __hash__(self):
		return superhash((self.submittedResponse, self.assessedValue))

	def sublocations(self):
		part = self.submittedResponse
		if hasattr(part, '__parent__'):
			if part.__parent__ is None:
				# XXX: HACK: Taking ownership because
				# of cross-database issues.
				logger.warn("XXX: HACK: Taking ownership of a sub-part")
				part.__parent__ = self
			if part.__parent__ is self:
				yield part

import time
from zope.datetime import parseDatetimetz

def _dctimes_property_fallback(attrname, dcname):
	# For BWC, if we happen to have annotations that happens to include
	# zope dublincore data, we will use it
	# TODO: Add a migration to remove these
	def get(self):
		self._p_activate()  # make sure there's a __dict__
		if attrname in self.__dict__:
			return self.__dict__[attrname]

		if '__annotations__' in self.__dict__:
			try:
				dcdata = self.__annotations__['zope.app.dublincore.ZopeDublinCore']
				date_modified = dcdata[dcname]  # tuple of a string
				datetime = parseDatetimetz(date_modified[0])
				result = time.mktime(datetime.timetuple())
				self.__dict__[attrname] = result  # migrate
				self._p_changed = True
				return result
			except KeyError: # pragma: no cover
				pass

		return 0

	def _set(self, value):
		self.__dict__[attrname] = value

	return property(get, _set)

@interface.implementer(interfaces.IQAssessedQuestion,
					   nti_interfaces.ICreated,
					   nti_interfaces.ILastModified,
					   ISublocations)
class QAssessedQuestion(SchemaConfigured, ContainedMixin, Persistent):
	createDirectFieldProperties(interfaces.IQAssessedQuestion)

	__external_can_create__ = False

	creator = None
	createdTime = _dctimes_property_fallback('createdTime', 'Date.Modified')
	lastModified = _dctimes_property_fallback('lastModified', 'Date.Created')
	def updateLastMod(self, t=None):
		self.lastModified = (t if t is not None and t > self.lastModified else time.time())
		return self.lastModified

	def __init__(self, *args, **kwargs):
		super(QAssessedQuestion, self).__init__(*args, **kwargs)
		self.lastModified = self.createdTime = time.time()

	def __eq__(self, other):
		try:
			return self is other or (self.questionId == other.questionId
									 and self.parts == other.parts)
		except AttributeError: # pragma: no cover
			return NotImplemented

	def __ne__(self, other):
		return not self == other

	__repr__ = make_repr()

	def __hash__(self):
		return superhash((self.questionId, tuple(self.parts)))

	sublocations = _make_sublocations()

@interface.implementer(interfaces.IQAssessedQuestionSet,
					   nti_interfaces.ICreated,
					   nti_interfaces.ILastModified)
class QAssessedQuestionSet(SchemaConfigured, ContainedMixin, Persistent):
	createDirectFieldProperties(interfaces.IQAssessedQuestionSet)
	__external_can_create__ = False

	creator = None
	createdTime = _dctimes_property_fallback('createdTime', 'Date.Modified')
	lastModified = _dctimes_property_fallback('lastModified', 'Date.Created')
	def updateLastMod(self, t=None):
		self.lastModified = (t if t is not None and t > self.lastModified else time.time())
		return self.lastModified

	def __init__(self, *args, **kwargs):
		super(QAssessedQuestionSet, self).__init__(*args, **kwargs)
		self.lastModified = self.createdTime = time.time()


	def __eq__(self, other):
		try:
			return self is other or (self.questionSetId == other.questionSetId
									 and self.questions == other.questions)
		except AttributeError: # pragma: no cover
			return NotImplemented

	def __ne__(self, other):
		return not self == other

	__repr__ = make_repr()

	def __hash__(self):
		return superhash((self.questionSetId, tuple(self.questions)))

	sublocations = _make_sublocations('questions')

def assess_question_submission(submission, registry=component):
	"""
	Assess the given question submission.

	:return: An :class:`.interfaces.IQAssessedQuestion`.
	:param submission: An :class:`.interfaces.IQuestionSubmission`.
		The ``parts`` of this submission must be the same length
		as the parts of the question being submitted. If there is no
		answer to a part, then the corresponding value in the submission
		array should be ``None`` and the auto-assessment will be 0.0.
		(In the future, if we have questions
		with required and/or optional parts, we would implement that check
		here).
	:param registry: If given, an :class:`.IComponents`. If
		not given, the current component registry will be used.
		Used to look up the question set and question by id.
	:raises LookupError: If no question can be found for the submission.
	:raises Invalid: If a submitted part has the wrong kind of input
		to be graded.
	"""

	question = registry.getUtility(interfaces.IQuestion, name=submission.questionId)
	if len(question.parts) != len(submission.parts):
		raise ValueError("Question (%s) and submission (%s) have different numbers of parts." %
						 (len(question.parts), len(submission.parts)))

	assessed_parts = PersistentList()
	for sub_part, q_part in zip(submission.parts, question.parts):
		# Grade what they submitted, if they submitted something. If they didn't
		# submit anything, it's automatically "wrong."
		try:
			grade = q_part.grade(sub_part) if sub_part is not None else 0.0
		except (LookupError,ValueError):
			# We couldn't grade the part because the submission was in the wrong
			# format. Translate this error to something more useful.
			raise InvalidValue(value=sub_part, field=interfaces.IQuestionSubmission['parts'])
		else:
			assessed_parts.append(QAssessedPart(submittedResponse=sub_part, assessedValue=grade))

	return QAssessedQuestion(questionId=submission.questionId, parts=assessed_parts)

def assess_question_set_submission(set_submission, registry=component):
	"""
	Assess the given question set submission.

	:return: An :class:`.interfaces.IQAssessedQuestionSet`.
	:param set_submission: An :class:`.interfaces.IQuestionSetSubmission`.
	:param registry: If given, an :class:`.IComponents`. If
		not given, the current component registry will be used.
		Used to look up the question set and question by id.
	:raises LookupError: If no question can be found for the submission.
	"""

	question_set = registry.getUtility(interfaces.IQuestionSet,
									   name=set_submission.questionSetId)

	questions_ntiids = {getattr(q, 'ntiid', None) for q in question_set.questions}

	# NOTE: At this point we need to decide what to do for missing values
	# We are currently not really grading them at all, which is what we
	# did for the old legacy quiz stuff

	assessed = PersistentList()
	for sub_question in set_submission.questions:
		question = registry.getUtility( interfaces.IQuestion,
										name=sub_question.questionId )
		# FIXME: Checking an 'ntiid' property that is not defined here is a hack
		# because we have an equality bug. It should go away as soon as equality is fixed
		if question in question_set.questions or getattr(question, 'ntiid', None) in questions_ntiids:
			sub_assessed = interfaces.IQAssessedQuestion(sub_question)  # Raises ComponentLookupError
			assessed.append(sub_assessed)
		else: # pragma: no cover
			logger.debug("Bad input, question (%s) not in question set (%s) (kownn: %s)",
						 question, question_set, question_set.questions)

	# NOTE: We're not really creating some sort of aggregate grade here
	return QAssessedQuestionSet(questionSetId=set_submission.questionSetId, questions=assessed)
