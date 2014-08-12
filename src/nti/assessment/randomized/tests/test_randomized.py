#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904


from hamcrest import is_
from hamcrest import is_not
from hamcrest import not_none
from hamcrest import has_length
from hamcrest import assert_that
does_not = is_not

import os
import json

from nti.assessment.randomized import questionbank_question_chooser
from nti.assessment.randomized.interfaces import IQuestionIndexRange

from nti.dataserver.users import User

from nti.externalization import internalization

from nti.dataserver.tests.mock_dataserver import WithMockDSTrans

from nti.assessment.tests import AssessmentTestCase

class TestRandomized(AssessmentTestCase):
	
	def _create_user(self, username='nt@nti.com', password='temp001'):
		usr = User.create_user(username=username, password=password)
		return usr

	@WithMockDSTrans
	def test_question_bank(self):

		path = os.path.join(os.path.dirname(__file__), "questionbank.json")
		with open(path, "r") as fp:
			ext_obj = json.load(fp)
			
		factory = internalization.find_factory_for(ext_obj)
		assert_that(factory, is_(not_none()))

		internal = factory()
		internalization.update_from_external_object(internal, ext_obj, require_updater=True)
		
		user1 = self._create_user(username='user1@nti.com')
		questions = questionbank_question_chooser(internal, user=user1)
		assert_that(questions, has_length(internal.draw))
		
		internal.draw = 2
		internal.ranges = [IQuestionIndexRange([0,5]), IQuestionIndexRange([6, 10])]
		questions = questionbank_question_chooser(internal, user=user1)
		assert_that(questions, has_length(internal.draw))
