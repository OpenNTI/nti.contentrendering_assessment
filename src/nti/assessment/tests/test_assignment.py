#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import assert_that
from hamcrest import has_entry
from hamcrest import has_entries
from hamcrest import is_not
does_not = is_not

from unittest import TestCase

from nti.testing.matchers import validly_provides
from nti.testing.matchers import verifiably_provides

from nti.externalization.tests import externalizes

import nti.testing.base

from .. import interfaces
from .. import assignment
from .. import question
from .. import parts

from . import AssessmentTestCase

class TestAssignment(AssessmentTestCase):

	def test_externalizes(self):
		assert_that( assignment.QAssignmentPart(), verifiably_provides( interfaces.IQAssignmentPart ) )
		# But missing a question set
		assert_that( assignment.QAssignmentPart(), does_not( validly_provides( interfaces.IQAssignmentPart ) ) )
		assert_that( assignment.QAssignmentPart(), externalizes( has_entry( 'Class', 'AssignmentPart' ) ) )

		part = assignment.QAssignmentPart(
			question_set=question.QQuestionSet(
				questions=[question.QQuestion(
					parts=[parts.QMathPart()])]) )
		assert_that( part, validly_provides( interfaces.IQAssignmentPart ) )

		assert_that( assignment.QAssignment(), verifiably_provides( interfaces.IQAssignment ) )
		# But it's not valid, it's missing parts
		assert_that( assignment.QAssignment(), does_not( validly_provides( interfaces.IQAssignment ) ) )
		assert_that( assignment.QAssignment(), externalizes( has_entries( 'Class', 'Assignment',
																		  'category_name', 'default') ) )

		assert_that( assignment.QAssignment(parts=[part]),
					 validly_provides(interfaces.IQAssignment) )

		assert_that( assignment.QAssignmentSubmissionPendingAssessment(),
					 verifiably_provides( interfaces.IQAssignmentSubmissionPendingAssessment ))
		assert_that( assignment.QAssignmentSubmissionPendingAssessment(),
					 externalizes( has_entry( 'Class', 'AssignmentSubmissionPendingAssessment' )))
