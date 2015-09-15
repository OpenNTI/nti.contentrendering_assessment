#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_property
from hamcrest import contains_string

from nti.assessment.interfaces import IQPoll
from nti.assessment.interfaces import IQSurvey
from nti.assessment.interfaces import IQNonGradableMatchingPart
from nti.assessment.interfaces import IQNonGradableOrderingPart
from nti.assessment.interfaces import IQNonGradableMultipleChoicePart
from nti.assessment.interfaces import IQNonGradableMultipleChoiceMultipleAnswerPart

from nti.contentrendering_assessment.ntiassessment import napoll
from nti.contentrendering_assessment.ntiassessment import nasurvey

from nti.contentrendering.tests import buildDomFromString as _buildDomFromString

from nti.contentrendering_assessment.tests import _simpleLatexDocument
from nti.contentrendering_assessment.tests import AssessmentRenderingTestCase

from nti.testing.matchers import verifiably_provides

class TestPoll(AssessmentRenderingTestCase):

	def test_matchingpart(self):
		example = br"""
			\begin{napoll}[not_before_date=2014-11-24,not_after_date=2014-12-04]
			\label{pqid.7_2_Poll.1}
				1. Sequencing. Place the following events in the order that they occurred
				\begin{naqmatchingpart}
					\begin{naqmlabels}
						\naqmlabel[1] 2
						\naqmlabel[0] 1
					\end{naqmlabels}
					\begin{naqmvalues}
						\naqmvalue "Black Thursday"
						\naqmvalue Battle of Anacostia Flats
					\end{naqmvalues}
				\end{naqmatchingpart}
			\end{napoll}
			"""
		dom = _buildDomFromString(_simpleLatexDocument((example,)))
		assert_that(dom.getElementsByTagName('napoll'), has_length(1))
		assert_that(dom.getElementsByTagName('napoll')[0], is_(napoll))

		assert_that(dom.getElementsByTagName('naqmlabel'), has_length(2))
		assert_that(dom.getElementsByTagName('naqmvalue'), has_length(2))

		naq = dom.getElementsByTagName('napoll')[0]
		part_el = naq.getElementsByTagName('naqmatchingpart')[0]

		poll = naq.assessment_object()
		assert_that(poll, verifiably_provides(IQPoll))
		assert_that(poll, has_property('available_for_submission_ending', is_not(none())))
		assert_that(poll, has_property('available_for_submission_beginning', is_not(none())))
		
		part = part_el.assessment_object()
		assert_that(part, verifiably_provides(part_el.nongradable_part_interface))
		assert_that(part_el.nongradable_part_interface, is_(IQNonGradableMatchingPart))
		
	def test_orderingpart_macros(self):
		example = br"""
			\begin{napoll}
			\label{pid.7_2_Poll.1}
				1. Sequencing. Place the following events in the order that they occurred
				\begin{naqorderingpart}
					\begin{naqmlabels}
						\naqmlabel[1] 1
						\naqmlabel[0] 2
					\end{naqmlabels}
					\begin{naqmvalues}
						\naqmvalue "Black Thursday"
						\naqmvalue Battle of Anacostia Flats
					\end{naqmvalues}
				\end{naqorderingpart}
			\end{napoll}
			"""
		dom = _buildDomFromString(_simpleLatexDocument((example,)))
		assert_that(dom.getElementsByTagName('napoll'), has_length(1))
		assert_that(dom.getElementsByTagName('napoll')[0], is_(napoll))

		assert_that(dom.getElementsByTagName('naqmlabel'), has_length(2))
		assert_that(dom.getElementsByTagName('naqmvalue'), has_length(2))

		naq = dom.getElementsByTagName('napoll')[0]
		part_el = naq.getElementsByTagName('naqorderingpart')[0]

		part = part_el.assessment_object()
		assert_that(part, verifiably_provides(part_el.nongradable_part_interface))
		assert_that(part_el.nongradable_part_interface, is_(IQNonGradableOrderingPart))
	
	def test_multiple_choice_macros(self):
		example = br"""
			\begin{napoll}
				Arbitrary prefix content goes here.
				\begin{naqmultiplechoicepart}
				   Arbitrary content for this part goes here.
				   \begin{naqchoices}
				   		\naqchoice Arbitrary content for the choice.
						\naqchoice[1] Arbitrary content for this choice; this is the right choice.
						\naqchoice[0.5] This choice is half correct.
					\end{naqchoices}
					\begin{naqsolexplanation}
						Arbitrary content explaining how the correct solution is arrived at.
					\end{naqsolexplanation}
				\end{naqmultiplechoicepart}
			\end{napoll}
			"""

		dom = _buildDomFromString(_simpleLatexDocument((example,)))
		assert_that(dom.getElementsByTagName('napoll'), has_length(1))
		assert_that(dom.getElementsByTagName('napoll')[0], is_(napoll))

		assert_that(dom.getElementsByTagName('naqchoice'), has_length(3))

		naq = dom.getElementsByTagName('napoll')[0]
		part_el = naq.getElementsByTagName('naqmultiplechoicepart')[0]

		part = part_el.assessment_object()
		assert_that(part, verifiably_provides(part_el.nongradable_part_interface))
		assert_that(part_el.nongradable_part_interface, is_(IQNonGradableMultipleChoicePart))

	def test_multiple_choice_multiple_answer_macros(self):
		example = br"""
			\begin{napoll}
				Arbitrary prefix content goes here.
				\begin{naqmultiplechoicemultipleanswerpart}
				   Arbitrary content for this part goes here.
					\begin{naqchoices}
						\naqchoice 8
						\naqchoice 9
						\naqchoice[1] 12
						\naqchoice[1] 18
						\naqchoice 21
						\naqchoice[1] 36
				  	\end{naqchoices}
				\end{naqmultiplechoicemultipleanswerpart}
			\end{napoll}
			"""

		dom = _buildDomFromString(_simpleLatexDocument((example,)))
		assert_that(dom.getElementsByTagName('napoll'), has_length(1))
		assert_that(dom.getElementsByTagName('napoll')[0], is_(napoll))

		assert_that(dom.getElementsByTagName('naqchoice'), has_length(6))

		naq = dom.getElementsByTagName('napoll')[0]
		part_el = naq.getElementsByTagName('naqmultiplechoicemultipleanswerpart')[0]

		part = part_el.assessment_object()
		assert_that(part, verifiably_provides(part_el.nongradable_part_interface))
		assert_that(part_el.nongradable_part_interface, is_(IQNonGradableMultipleChoiceMultipleAnswerPart))

	def test_survey(self):
		example = br"""
		\begin{napoll}
			\label{poll1}
			Arbitrary content goes here.
			\begin{naqessaypart}
				Arbitrary content goes here.
				\begin{naqhints}
					\naqhint Some hint
				\end{naqhints}
			\end{naqessaypart}
		\end{napoll}
 		
		\begin{nasurvey}[not_before_date=2014-11-24,not_after_date=2014-12-04]
			\label{survey}
			\napollref{poll1}
		\end{nasurvey}
		"""

		dom = _buildDomFromString( _simpleLatexDocument((example,)))
		assert_that( dom.getElementsByTagName('napoll'), has_length(1) )
		assert_that( dom.getElementsByTagName('napoll')[0], is_(napoll))

		assert_that( dom.getElementsByTagName('nasurvey'), has_length( 1 ) )
		assert_that( dom.getElementsByTagName('nasurvey')[0], is_(nasurvey))

		survey_object = dom.getElementsByTagName('nasurvey')[0].assessment_object()
		assert_that(survey_object, has_property('questions', has_length(1) ))
		assert_that(survey_object, has_property('ntiid', contains_string('survey')))
		assert_that(survey_object, has_property('available_for_submission_ending', is_not(none())))
		assert_that(survey_object, has_property('available_for_submission_beginning', is_not(none())))
		assert_that(survey_object, verifiably_provides(IQSurvey))
