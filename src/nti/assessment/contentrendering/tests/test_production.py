#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import not_none
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_property
from hamcrest import same_instance
from hamcrest import contains_string

import os

from nti.assessment.contentrendering.ntiassessment import naquestionset
from nti.assessment.contentrendering.ntiassessment import naquestionbank
from nti.assessment.contentrendering.ntiassessment import naquestionfillintheblankwordbank

from nti.contentrendering.tests import buildDomFromString as _buildDomFromString

from nti.assessment.contentrendering.tests import _simpleLatexDocument
from nti.assessment.contentrendering.tests import AssessmentRenderingTestCase

from nti.testing.matchers import is_true, is_false

class TestProduction(AssessmentRenderingTestCase):

	def test_biology(self):
		name = 'question_assignment_bio.tex'
		with open(os.path.join( os.path.dirname(__file__), name)) as fp:
			example = fp.read()
		
		dom = _buildDomFromString( _simpleLatexDocument( (example,) ) )
		assert_that( dom.getElementsByTagName('naquestionfillintheblankwordbank'), has_length( 1 ) )
		assert_that( dom.getElementsByTagName('naquestionfillintheblankwordbank')[0], 
					 is_(naquestionfillintheblankwordbank) )

		assert_that( dom.getElementsByTagName('naquestionbank'), has_length( 1 ) )
		assert_that( dom.getElementsByTagName('naquestionbank')[0], is_( naquestionbank ) )

		qset_object = dom.getElementsByTagName( 'naquestionbank' )[0].assessment_object()
		assert_that( qset_object, has_length( 1 ) )
		assert_that( qset_object, has_property('questions', has_length( 1 ) ))
		assert_that( qset_object, has_property('ntiid', contains_string( 'set' ) ))

		asg_object = dom.getElementsByTagName( 'naassignment' )[0].assessment_object()
		assert_that( asg_object, has_property( 'parts', has_length( 1 )))
		assert_that( asg_object, has_property( 'no_submit', is_false()))
		assert_that( asg_object, has_property( 'category_name', is_('no_submit')))
		assert_that( asg_object.parts[0], has_property( 'auto_grade', is_true()))
		assert_that( asg_object.parts[0], has_property( 'question_set', same_instance(qset_object)))
				
		question = qset_object[0]
		assert_that( question, has_length( 1 ) )
		assert_that( question, has_property('parts', has_length( 1 ) ))
		assert_that( question, has_property('wordbank', is_( none() ) ))
		
		question_part = question[0]
		assert_that( question_part, has_property('wordbank', is_( not_none() ) ))

	def test_ucol(self):
		name = 'question_assignment_ucol.tex'
		with open(os.path.join( os.path.dirname(__file__), name)) as fp:
			example = fp.read()
		
		dom = _buildDomFromString( _simpleLatexDocument( (example,) ) )
		assert_that( dom.getElementsByTagName('naquestionset'), has_length( 1 ) )
		assert_that( dom.getElementsByTagName('naquestionset')[0], is_( naquestionset ) )

		qset_object = dom.getElementsByTagName( 'naquestionset' )[0].assessment_object()
		asg_object = dom.getElementsByTagName( 'naassignment' )[0].assessment_object()
		assert_that( asg_object, has_property( 'category_name', is_('no_submit')))
		assert_that( asg_object, has_property( 'no_submit', is_true()))
		
		assert_that( asg_object, has_property( 'parts', has_length( 1 )))
		assert_that( asg_object.parts[0], has_property( 'question_set', same_instance(qset_object)))
		
		assert_that( qset_object, has_length( 5 ) )
		for idx in xrange(len(qset_object)):
			question = qset_object[idx]
			assert_that( question, has_length( 1 ) )
			assert_that( question, has_property('parts', has_length( 1 ) ))
			assert_that( question, has_property('wordbank', is_( not_none() ) ))
			question_part = question[0]
			assert_that( question_part, has_property('wordbank', is_( none() ) ))
