#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904


from hamcrest import is_
from hamcrest import is_not
from hamcrest import not_none
from hamcrest import equal_to
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_property
from hamcrest import same_instance
does_not = is_not

import os
import json

from nti.assessment.randomized import randomize
from nti.assessment.randomized import shuffle_list
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
	def test_randomize(self):
		size = 20
		ichigo = self._create_user(username='ichigo@nti.com')
		numbers_1 = range(0, size)
		generator = randomize(ichigo)
		shuffle_list(generator, numbers_1)
		
		numbers_2 = range(0, size)
		generator = randomize(ichigo)
		shuffle_list(generator, numbers_2)
		
		assert_that(numbers_1, is_(numbers_2))
		
		aizen = self._create_user(username='aizen@nti.com')
		numbers_3 = range(0, size)
		generator = randomize(aizen)
		shuffle_list(generator, numbers_3)
		
		assert_that(numbers_1, is_not(numbers_3))
		
	@WithMockDSTrans
	def test_question_bank_1(self):

		path = os.path.join(os.path.dirname(__file__), "question_bank_1.json")
		with open(path, "r") as fp:
			ext_obj = json.load(fp)
			
		factory = internalization.find_factory_for(ext_obj)
		assert_that(factory, is_(not_none()))

		internal = factory()
		internalization.update_from_external_object(internal, ext_obj,
													require_updater=True)
		
		all_questions = list(internal.questions)
		
		user1 = self._create_user(username='user1@nti.com')
		questions = questionbank_question_chooser(internal, user=user1)
		assert_that(questions, has_length(internal.draw))
		
		user2 = self._create_user(username='user2@nti.com')
		questions2 = questionbank_question_chooser(internal, user=user2)
		assert_that(questions, is_not(equal_to(questions2)))
		
		internal.draw = 2
		internal.ranges = [IQuestionIndexRange([0,5]), IQuestionIndexRange([6, 10])]
		questions = questionbank_question_chooser(internal, user=user1)
		assert_that(questions, has_length(internal.draw))

		questions2 = questionbank_question_chooser(internal, user=user2)
		assert_that(questions, is_not(equal_to(questions2)))
		
		internal.srand = True
		questions3 = questionbank_question_chooser(internal)
		assert_that(questions, is_not(equal_to(questions3)))
		
		new_internal = internal.copy(questions=all_questions)
		assert_that(id(new_internal), is_not(id(internal)))
		assert_that(new_internal, has_property('srand', is_(True)))
		assert_that(new_internal, has_property('draw', is_(internal.draw)))
		assert_that(new_internal, has_property('srand', is_(internal.srand)))
		assert_that(new_internal, has_property('title', is_(internal.title)))
		assert_that(new_internal, has_property('questions', is_(all_questions)))

	@WithMockDSTrans
	def test_question_bank_2(self):

		path = os.path.join(os.path.dirname(__file__), "question_bank_2.json")
		with open(path, "r") as fp:
			ext_obj = json.load(fp)
			
		factory = internalization.find_factory_for(ext_obj)
		assert_that(factory, is_(not_none()))

		internal = factory()
		internalization.update_from_external_object(internal, ext_obj,
													require_updater=True)
				
		user1 = self._create_user(username='user1@nti.com')
		questions_1 = questionbank_question_chooser(internal, user=user1)
		assert_that(questions_1, has_length(internal.draw))
		
		user2 = self._create_user(username='user2@nti.com')
		questions_2 = questionbank_question_chooser(internal, user=user2)
		assert_that(questions_2, has_length(internal.draw))
		
		assert_that(questions_1[-1], is_(same_instance(questions_2[-1])))
		assert_that(questions_1[0:-1], is_not(equal_to(questions_2[0:-1])))
