#!/usr/bin/env python
"""
$Id$
"""
from __future__ import print_function, unicode_literals

from hamcrest import assert_that, has_entry, is_, has_property, contains, same_instance
from hamcrest import is_not
does_not = is_not
from hamcrest import not_none
from unittest import TestCase
from nti.testing.matchers import verifiably_provides
from nti.testing.matchers import validly_provides
from nti.externalization.tests import externalizes
from nose.tools import assert_raises

from zope import component
from zope.schema import interfaces as sch_interfaces
from zope.dottedname import resolve as dottedname

import nti.assessment
from nti.externalization.externalization import toExternalObject
from nti.externalization.internalization import update_from_external_object
from nti.externalization import internalization
from nti.externalization import interfaces as ext_interfaces

from .. import interfaces
from .. import assignment
from .. import question
from .. import parts


# nose module-level setup
setUpModule = lambda: nti.testing.base.module_setup( set_up_packages=(__name__,) )
tearDownModule = nti.testing.base.module_teardown

class TestAssignment(TestCase):

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
		assert_that( assignment.QAssignment(), externalizes( has_entry( 'Class', 'Assignment' ) ) )

		assert_that( assignment.QAssignment(parts=[part]),
					 validly_provides(interfaces.IQAssignment) )
