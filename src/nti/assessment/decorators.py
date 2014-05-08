#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Decorators for assessment objects.

.. $Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface
from zope import component

from nti.externalization import interfaces as ext_interfaces
from nti.externalization.singleton import SingletonDecorator
from nti.externalization.externalization import to_external_object

from . import interfaces

@interface.implementer(interfaces.IQPartSolutionsExternalizer)
@component.adapter(interfaces.IQPart)
class _DefaultPartSolutionsExternalizer(object):

	__slots__ = ('part',)

	def __init__(self, part):
		self.part = part

	def to_external_object(self):
		return to_external_object(self.part.solutions)

@interface.implementer(ext_interfaces.IExternalObjectDecorator)
@component.adapter(interfaces.IQAssessedQuestion)
class _QAssessedQuestionExplanationSolutionAdder(object):
	"""
	Because we don't generally want to provide solutions and explanations
	until after a student has submitted, we place them on the assessed object.

	.. note:: In the future this may be registered/unregistered on a site
		by site basis (where a Course is a site) so that instructor preferences
		on whether or not to provide solutions can be respected.
	"""

	__metaclass__ = SingletonDecorator

	def decorateExternalObject( self, context, mapping ):
		question_id = context.questionId
		question = component.queryUtility( interfaces.IQuestion,
										   name=question_id )
		if question is None:
			# In case of old answers to questions
			# that no longer exist mostly
			return

		for question_part, external_part in zip(question.parts, mapping['parts']):
			externalizer = interfaces.IQPartSolutionsExternalizer(question_part)
			external_part['solutions'] = externalizer.to_external_object()
			external_part['explanation'] = to_external_object(question_part.explanation)

@interface.implementer(ext_interfaces.IExternalObjectDecorator)
class _QAssessmentObjectIContainedAdder(object):
	"""
	When an assignment or question set comes from a content package
	and thus has a __parent__ that has an NTIID, make that NTIID
	available as the ``containerId``, just like an
	:class:`nti.dataserver.interfaces.IContained` object. This is
	meant to help provide contextual information for the UI because
	sometimes these objects (assignments especially) are requested
	in bulk without any other context.

	Obviously this only works if assignments are written in the TeX
	files at a relevant location (within the section aka lesson they
	are about)---if they are lumped together at the end, this does no
	good.

	This is perhaps a temporary measure as assessments will be moving
	into course definitions.
	"""

	__metaclass__ = SingletonDecorator

	def decorateExternalObject( self, context, mapping ):
		if not mapping.get('containerId'):
			# Be careful not to write this out at rendering time
			# with a None value, but if it does happen overwrite
			# it
			containerId = None
			containerId = getattr( context.__parent__, 'ntiid', None )
			if containerId:
				mapping['containerId'] = containerId
