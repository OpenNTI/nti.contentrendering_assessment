#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_property
from hamcrest import same_instance
from hamcrest import contains_string

import os

#from nti.externalization.externalization import to_external_object

from nti.assessment.contentrendering.ntiassessment import naquestionbank
from nti.assessment.contentrendering.ntiassessment import naquestionfillintheblankwordbank

from nti.contentrendering.tests import buildDomFromString as _buildDomFromString

from nti.testing.matchers import is_true

from nti.assessment.tests import AssessmentTestCase
from nti.assessment.tests import _simpleLatexDocument

class TestProduction(AssessmentTestCase):

	def test_biology(self):
		name = 'question_fillintheblankwordbank_bio.tex'
		with open(os.path.join( os.path.dirname(__file__), name)) as fp:
				example = fp.read()
		
		dom = _buildDomFromString( _simpleLatexDocument( (example,) ) )
		assert_that( dom.getElementsByTagName('naquestionfillintheblankwordbank'), has_length( 1 ) )
		assert_that( dom.getElementsByTagName('naquestionfillintheblankwordbank')[0], 
					 is_(naquestionfillintheblankwordbank) )

		assert_that( dom.getElementsByTagName('naquestionbank'), has_length( 1 ) )
		assert_that( dom.getElementsByTagName('naquestionbank')[0], is_( naquestionbank ) )

		qset_object = dom.getElementsByTagName( 'naquestionbank' )[0].assessment_object()
		assert_that( qset_object.questions, has_length( 1 ) )
		assert_that( qset_object.ntiid, contains_string( 'set' ) )

		asg_object = dom.getElementsByTagName( 'naassignment' )[0].assessment_object()
		assert_that( asg_object, has_property( 'parts', has_length( 1 )))
		assert_that( asg_object.parts[0], has_property( 'question_set', same_instance(qset_object)))
		assert_that( asg_object.parts[0], has_property( 'auto_grade', is_true()))
# 		assert_that( asg_object.parts[0], has_property( 'content', 'Some content.'))
# 		assert_that( asg_object.parts[0], has_property( 'title', 'Part Title'))
# 		assert_that( asg_object, has_property('content', "Assignment content."))
# 		assert_that( asg_object.ntiid, contains_string('assignment'))
# 		assert_that( asg_object, has_property('title', 'Main Title'))
# 		assert_that( asg_object, has_property('is_non_public', False))
# 		assert_that( asg_object, has_property('category_name', 'quizzes'))
# 		assert_that( asg_object, has_property( 'available_for_submission_beginning',
# 											   datetime( 2014, 01, 13, 6, 0)))

