#!/usr/bin/env python
"""
$Id$
"""
from __future__ import print_function, unicode_literals

from hamcrest import assert_that
from hamcrest import has_entry
from hamcrest import is_
from hamcrest import has_property
from hamcrest import contains
from hamcrest import none
from hamcrest import is_not
from hamcrest import has_length
from hamcrest import has_item
from unittest import TestCase
from nti.testing.matchers import is_false
from nti.testing.matchers import validly_provides, verifiably_provides
import nti.testing.base
from nti.externalization.tests import externalizes

from zope import interface
from zope import component
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.dublincore.annotatableadapter import ZDCAnnotatableAdapter

from nti.externalization.externalization import toExternalObject
from nti.externalization import internalization
from nti.externalization.internalization import update_from_external_object

import datetime
import time

from .. import interfaces
from nti.dataserver import interfaces as nti_interfaces
from .. import parts
from .. import response
from .. import submission
from .. import assessed
from .. import solution as solutions
from ..question import QQuestion, QQuestionSet


#pylint: disable=R0904


# nose module-level setup
setUpModule = lambda: nti.testing.base.module_setup( set_up_packages=(__name__,'zope.annotation') )
tearDownModule = nti.testing.base.module_teardown

def _check_old_dublin_core( qaq ):
	"we can read old dublin core metadata"

	del qaq.__dict__['lastModified']
	del qaq.__dict__['createdTime']

	assert_that( qaq.lastModified, is_( 0 ) )
	assert_that( qaq.createdTime, is_( 0 ) )


	interface.alsoProvides( qaq, IAttributeAnnotatable )

	zdc = ZDCAnnotatableAdapter( qaq )

	now = datetime.datetime.now()

	zdc.created = now
	zdc.modified = now

	assert_that( qaq.lastModified, is_( time.mktime( now.timetuple() ) ) )
	assert_that( qaq.createdTime, is_( time.mktime( now.timetuple() ) ) )


class TestAssessedPart(TestCase):


	def test_externalizes(self):
		assert_that( assessed.QAssessedPart(), verifiably_provides( interfaces.IQAssessedPart ) )
		assert_that( assessed.QAssessedPart(), externalizes( has_entry( 'Class', 'AssessedPart' ) ) )
		assert_that( internalization.find_factory_for( toExternalObject( assessed.QAssessedPart() ) ),
					 is_( none() ) )


		# These cannot be created externally, so we're not worried about
		# what happens when they are updated...this test just serves to document
		# the behaviour. In the past, updating from external objects transformed
		# the value into an IQResponse...but the actual assessment code itself assigned
		# the raw string/int value. Responses would be ideal, but that could break existing
		# client code. The two behaviours are now unified
		part = assessed.QAssessedPart()
		update_from_external_object( part, {"submittedResponse": "The text response"}, require_updater=True )

		assert_that( part.submittedResponse, is_( "The text response" ) )

	def test_hash(self):
		part = assessed.QAssessedPart(submittedResponse=[1,2,3])
		hash(part)

class TestAssessedQuestion(TestCase):


	def test_externalizes(self):
		assert_that( assessed.QAssessedQuestion(), verifiably_provides( interfaces.IQAssessedQuestion ) )
		assert_that( assessed.QAssessedQuestion(), verifiably_provides( nti_interfaces.ILastModified ) )
		assert_that( assessed.QAssessedQuestion(), externalizes( has_entry( 'Class', 'AssessedQuestion' ) ) )
		assert_that( internalization.find_factory_for( toExternalObject( assessed.QAssessedQuestion() ) ),
					 is_( none() ) )

	def test_assess( self ):
		part = parts.QFreeResponsePart(solutions=(solutions.QFreeResponseSolution(value='correct'),))
		question = QQuestion( parts=(part,) )
		component.provideUtility( question, provides=interfaces.IQuestion,  name="1")

		sub = submission.QuestionSubmission( questionId="1", parts=('correct',) )

		result = interfaces.IQAssessedQuestion( sub )
		assert_that( result, has_property( 'questionId', "1" ) )
		assert_that( result, has_property( 'parts', contains( assessed.QAssessedPart( submittedResponse='correct', assessedValue=1.0 ) ) ) )

		_check_old_dublin_core( result )


		assert_that( result, externalizes( has_entry( 'parts',
													  has_item(
														  has_entry( 'solutions',
																	 has_item( has_entry( 'value',
																						  'correct' ))) ) ) ) )

class TestAssessedQuestionSet(TestCase):

	def test_externalizes(self):
		assert_that( assessed.QAssessedQuestionSet(), verifiably_provides( interfaces.IQAssessedQuestionSet ) )
		assert_that( assessed.QAssessedQuestionSet(), verifiably_provides( nti_interfaces.ILastModified ) )
		assert_that( assessed.QAssessedQuestionSet(), externalizes( has_entry( 'Class', 'AssessedQuestionSet' ) ) )
		assert_that( internalization.find_factory_for( toExternalObject( assessed.QAssessedQuestionSet() ) ),
					 is_( none() ) )

	def test_assess( self ):
		part = parts.QFreeResponsePart(solutions=(solutions.QFreeResponseSolution(value='correct'),))
		question = QQuestion( parts=(part,) )
		question_set = QQuestionSet( questions=(question,) )

		component.provideUtility( question,
								  provides=interfaces.IQuestion,
								  name="1" )
		component.provideUtility( question_set,
								  provides=interfaces.IQuestionSet,
								  name="2" )

		sub = submission.QuestionSubmission( questionId="1", parts=('correct',) )
		set_sub = submission.QuestionSetSubmission( questionSetId="2", questions=(sub,) )

		result = interfaces.IQAssessedQuestionSet( set_sub )

		assert_that( result, has_property( 'questionSetId', "2" ) )
		assert_that( result, has_property( 'questions',
										   contains(
											   has_property( 'parts', contains( assessed.QAssessedPart( submittedResponse='correct', assessedValue=1.0 ) ) ) ) ) )
		# consistent hashing
		assert_that( hash(result), is_(hash(result)))

		ext_obj = toExternalObject( result )
		assert_that( ext_obj, has_entry( 'questions', has_length( 1 ) ) )

		_check_old_dublin_core( result )

	def test_assess_not_same_instance_question_but_id_matches( self ):
		part = parts.QFreeResponsePart(solutions=(solutions.QFreeResponseSolution(value='correct'),))
		question = QQuestion( parts=(part,) )
		question.ntiid = 'abc'
		question_set = QQuestionSet( questions=(question,) )

		component.provideUtility( question,
								  provides=interfaces.IQuestion,
								  name='abc')
		component.provideUtility( question_set,
								  provides=interfaces.IQuestionSet,
								  name="2" )
		# New instance
		part = parts.QFreeResponsePart(solutions=(solutions.QFreeResponseSolution(value='correct2'),))
		question = QQuestion( parts=(part,) )
		question.ntiid = 'abc'

		component.provideUtility( question,
								  provides=interfaces.IQuestion,
								  name='abc')

		assert_that( question, is_not( question_set.questions[0] ) )

		sub = submission.QuestionSubmission( questionId='abc', parts=('correct2',) )
		set_sub = submission.QuestionSetSubmission( questionSetId="2", questions=(sub,) )

		result = interfaces.IQAssessedQuestionSet( set_sub )

		assert_that( result, has_property( 'questionSetId', "2" ) )
		assert_that( result, has_property( 'questions',
										   contains(
											   has_property( 'parts', contains( assessed.QAssessedPart( submittedResponse='correct2', assessedValue=1.0 ) ) ) ) ) )


		ext_obj = toExternalObject( result )
		assert_that( ext_obj, has_entry( 'questions', has_length( 1 ) ) )

	def test_assess_not_same_instance_question_but_equals( self ):
		part = parts.QFreeResponsePart(solutions=(solutions.QFreeResponseSolution(value='correct'),))
		question = QQuestion( content='foo', parts=(part,) )
		question_set = QQuestionSet( questions=(question,) )

		# New instance
		part = parts.QFreeResponsePart(solutions=(solutions.QFreeResponseSolution(value='correct'),))
		question = QQuestion( content='foo', parts=(part,) )

		assert_that( question, is_( question_set.questions[0] ) )
		# Some quick coverage things
		assert_that( hash( question ), is_( hash( question_set.questions[0] ) ) )
		hash( question_set )
		assert_that( question != question, is_false() )
		assert_that( question_set != question_set, is_false() )

		component.provideUtility( question,
								  provides=interfaces.IQuestion,
								  name="abc" )
		component.provideUtility( question_set,
								  provides=interfaces.IQuestionSet,
								  name="2")

		sub = submission.QuestionSubmission( questionId='abc', parts=('correct',) )
		set_sub = submission.QuestionSetSubmission( questionSetId="2", questions=(sub,) )

		result = interfaces.IQAssessedQuestionSet( set_sub )

		assert_that( result, has_property( 'questionSetId', "2" ) )
		assert_that( result, has_property( 'questions',
										   contains(
											   has_property( 'parts', contains( assessed.QAssessedPart( submittedResponse='correct', assessedValue=1.0 ) ) ) ) ) )


		ext_obj = toExternalObject( result )
		assert_that( ext_obj, has_entry( 'questions', has_length( 1 ) ) )
