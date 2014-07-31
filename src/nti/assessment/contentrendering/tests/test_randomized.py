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
from hamcrest import contains_string

from nti.assessment.contentrendering.ntiassessment import naquestion
from nti.assessment.contentrendering.ntiassessment import narandomizedquestionset 

from nti.assessment.randomized.interfaces import IQRandomizedMultipleChoicePart

from nti.testing.matchers import verifiably_provides

from nti.assessment.tests import AssessmentTestCase
from nti.assessment.tests import _simpleLatexDocument

from nti.contentrendering.tests import buildDomFromString as _buildDomFromString

class TestRandomized(AssessmentTestCase):

	def test_multiple_choice_macros(self):
		example = br"""
			\begin{naquestion}
				Arbitrary prefix content goes here.
				\begin{naqmultiplechoicepart}[randomize=true]
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
			\end{naquestion}
			"""

		dom = _buildDomFromString(_simpleLatexDocument((example,)))
		assert_that(dom.getElementsByTagName('naquestion'), has_length(1))
		assert_that(dom.getElementsByTagName('naquestion')[0], is_(naquestion))

		assert_that(dom.getElementsByTagName('naqchoice'), has_length(3))
		assert_that(dom.getElementsByTagName('naqsolution'), has_length(2))

		naq = dom.getElementsByTagName('naquestion')[0]
		part_el = naq.getElementsByTagName('naqmultiplechoicepart')[0]
		assert_that(part_el, has_property('randomize', is_(True)))

		part = part_el.assessment_object()
		assert_that(part, verifiably_provides(part_el.part_interface))
		assert_that(part_el.part_interface, is_(IQRandomizedMultipleChoicePart))

	def test_randomizedquestion_set_macros(self):
		example = br"""
		\begin{naquestion}[individual=true]
			\label{question1}
			Arbitrary content goes here.
			\begin{naqsymmathpart}
			Arbitrary content goes here.
			\begin{naqsolutions}
				\naqsolution $420$
				\naqsolution $\frac{5}{8}$
				\naqsolution $\left(3x+2\right)\left(2x+3\right)$
				\naqsolution $\surd2$
				\naqsolution $\frac{\surd\left(8x+5\right)\left(12x+12\right)}{\approx152318}+1204$
			\end{naqsolutions}
			\begin{naqhints}
				\naqhint Some hint
			\end{naqhints}
			\end{naqsymmathpart}
		\end{naquestion}
		
		\begin{naquestion}[individual=true]
			\label{question2}
			Arbitrary content goes here,

			and there's a blank line, and another before the part:
			\begin{naqessaypart}
			Arbitrary content goes here.
			\begin{naqhints}
				\naqhint Some hint
			\end{naqhints}
			\end{naqessaypart}
		\end{naquestion}
		
		\begin{narandomizedquestionset}[draw=1]
			\label{set}
			\naquestionref{question1}
			\naquestionref{question2}
		\end{narandomizedquestionset}

		"""

		dom = _buildDomFromString( _simpleLatexDocument((example,)))
		assert_that( dom.getElementsByTagName('naquestion'), has_length(2) )
		assert_that( dom.getElementsByTagName('naquestion')[0], is_(naquestion))
		assert_that( dom.getElementsByTagName('naquestion')[1], is_(naquestion))

		assert_that( dom.getElementsByTagName('narandomizedquestionset'), has_length( 1 ) )
		assert_that( dom.getElementsByTagName('narandomizedquestionset')[0], is_(narandomizedquestionset))

		qset_object = dom.getElementsByTagName('narandomizedquestionset')[0].assessment_object()
		assert_that(qset_object.questions, has_length(2) )
		assert_that(qset_object, has_property('draw', is_(1)))
		assert_that(qset_object.ntiid, contains_string('set'))
