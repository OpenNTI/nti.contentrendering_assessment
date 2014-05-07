#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import assert_that
from hamcrest import has_entry
from hamcrest import is_
from hamcrest import has_property
from hamcrest import contains
from hamcrest import same_instance
from hamcrest import has_key
from hamcrest import not_none
from hamcrest import has_entries

from unittest import TestCase

import nti.testing.base
from nti.testing.matchers import verifiably_provides
from nti.testing.matchers import validly_provides
from nti.externalization.tests import externalizes
from nose.tools import assert_raises

from zope.schema import interfaces as sch_interfaces

from nti.externalization import internalization
from nti.externalization.externalization import toExternalObject
from nti.externalization.internalization import update_from_external_object

from .. import interfaces
from .. import submission

from . import AssessmentTestCase

class TestQuestionSubmission(AssessmentTestCase):

	def test_externalizes(self):
		assert_that( submission.QuestionSubmission(), verifiably_provides( interfaces.IQuestionSubmission ) )
		assert_that( submission.QuestionSubmission(), externalizes( has_entry( 'Class', 'QuestionSubmission' ) ) )
		assert_that( internalization.find_factory_for( toExternalObject( submission.QuestionSubmission() ) ),
					 has_property( '_callable', is_( same_instance( submission.QuestionSubmission ) ) ) )


		# Now verify the same for the mimetype-only version
		assert_that( submission.QuestionSubmission(), externalizes( has_key( 'MimeType' ) ) )
		ext_obj_no_class = toExternalObject( submission.QuestionSubmission() )
		ext_obj_no_class.pop( 'Class' )

		assert_that( internalization.find_factory_for( ext_obj_no_class ),
					 is_( not_none() ) )


		# No coersion of parts happens yet at this level
		submiss = submission.QuestionSubmission()
		with assert_raises(sch_interfaces.RequiredMissing):
			update_from_external_object( submiss, {"parts": ["The text response"]}, require_updater=True )

		update_from_external_object( submiss, {'questionId': 'foo', "parts": ["The text response"]}, require_updater=True )
		assert_that( submiss, has_property( "parts", contains( "The text response" ) ) )

class TestQuestionSetSubmission(AssessmentTestCase):

	def test_externalizes(self):
		assert_that( submission.QuestionSetSubmission(), verifiably_provides( interfaces.IQuestionSetSubmission ) )
		assert_that( submission.QuestionSetSubmission(), externalizes( has_entry( 'Class', 'QuestionSetSubmission' ) ) )

		qss = submission.QuestionSetSubmission()
		with assert_raises(sch_interfaces.RequiredMissing):
			update_from_external_object( qss, {}, require_updater=True )

		# Wrong type for objects in questions
		with assert_raises(sch_interfaces.WrongContainedType):
			update_from_external_object( qss, {'questionSetId': 'foo',
											   "questions": ["The text response"]}, require_updater=True )

		# Validation is recursive
		with assert_raises( sch_interfaces.WrongContainedType) as wct:
			update_from_external_object( qss, {'questionSetId': 'foo',
											   "questions": [submission.QuestionSubmission()]}, require_updater=True )

		assert_that( wct.exception.args[0][0], is_( sch_interfaces.WrongContainedType ) )

		update_from_external_object( qss, {'questionSetId': 'foo',
										   "questions": [submission.QuestionSubmission(questionId='foo', parts=[])]}, require_updater=True )

		assert_that( qss, has_property( 'questions', contains( is_( submission.QuestionSubmission ) ) ) )

class TestAssignmentSubmission(AssessmentTestCase):

	def test_externalizes(self):
		assert_that( submission.AssignmentSubmission(), verifiably_provides( interfaces.IQAssignmentSubmission ) )
		assert_that( submission.AssignmentSubmission(), externalizes( has_entries( 'Class', 'AssignmentSubmission',
																				   'MimeType', 'application/vnd.nextthought.assessment.assignmentsubmission') ) )

		asub = submission.AssignmentSubmission()
		# Recursive validation
		with assert_raises(sch_interfaces.WrongContainedType) as wct:
			update_from_external_object( asub,
										 {'parts': [submission.QuestionSetSubmission()]},
										 require_updater=True )
		assert_that( wct.exception.args[0][0][0][0][1], is_( sch_interfaces.RequiredMissing ) )


		update_from_external_object( asub,
									 {'parts': [submission.QuestionSetSubmission(questionSetId='foo', questions=())],
									  'assignmentId': 'baz'},
									 require_updater=True )

		assert_that( asub, has_property( 'parts', contains( is_( submission.QuestionSetSubmission ) ) ) )

		assert_that( asub, validly_provides( interfaces.IQAssignmentSubmission ))
