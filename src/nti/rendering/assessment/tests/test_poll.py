#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import has_length
from hamcrest import assert_that

from nti.assessment.interfaces import IQPoll
from nti.assessment.interfaces import IQNonGradableMatchingPart
from nti.assessment.interfaces import IQNonGradableOrderingPart
from nti.assessment.interfaces import IQNonGradableMultipleChoicePart

from nti.rendering.assessment.ntiassessment import napoll

from nti.contentrendering.tests import buildDomFromString as _buildDomFromString

from nti.rendering.assessment.tests import _simpleLatexDocument
from nti.rendering.assessment.tests import AssessmentRenderingTestCase

from nti.testing.matchers import verifiably_provides

class TestPoll(AssessmentRenderingTestCase):

	def test_matchingpart(self):
		example = br"""
			\begin{napoll}
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
		assert_that(dom.getElementsByTagName('naqsolution'), has_length(2))

		naq = dom.getElementsByTagName('napoll')[0]
		part_el = naq.getElementsByTagName('naqmultiplechoicepart')[0]

		part = part_el.assessment_object()
		assert_that(part, verifiably_provides(part_el.nongradable_part_interface))
		assert_that(part_el.nongradable_part_interface, is_(IQNonGradableMultipleChoicePart))
# 
# 	def test_randomizedquestionset_macros(self):
# 		example = br"""
# 		\begin{naquestion}[individual=true]
# 			\label{question1}
# 			Arbitrary content goes here.
# 			\begin{naqsymmathpart}
# 			Arbitrary content goes here.
# 			\begin{naqsolutions}
# 				\naqsolution $420$
# 				\naqsolution $\frac{5}{8}$
# 				\naqsolution $\left(3x+2\right)\left(2x+3\right)$
# 				\naqsolution $\surd2$
# 				\naqsolution $\frac{\surd\left(8x+5\right)\left(12x+12\right)}{\approx152318}+1204$
# 			\end{naqsolutions}
# 			\begin{naqhints}
# 				\naqhint Some hint
# 			\end{naqhints}
# 			\end{naqsymmathpart}
# 		\end{naquestion}
# 		
# 		\begin{narandomizedquestionset}
# 			\label{set}
# 			\naquestionref{question1}
# 		\end{narandomizedquestionset}
# 
# 		"""
# 
# 		dom = _buildDomFromString( _simpleLatexDocument((example,)))
# 		assert_that( dom.getElementsByTagName('naquestion'), has_length(1) )
# 		assert_that( dom.getElementsByTagName('naquestion')[0], is_(naquestion))
# 
# 		assert_that( dom.getElementsByTagName('narandomizedquestionset'), has_length( 1 ) )
# 		assert_that( dom.getElementsByTagName('narandomizedquestionset')[0], is_(narandomizedquestionset))
# 
# 		qset_object = dom.getElementsByTagName('narandomizedquestionset')[0].assessment_object()
# 		assert_that(qset_object.questions, has_length(1) )
# 		assert_that(qset_object.ntiid, contains_string('set'))
# 		assert_that(qset_object, verifiably_provides(IRandomizedQuestionSet))
# 
# 	def test_questionbank_macros(self):
# 		example = br"""
# 		\begin{naquestion}[individual=true]
# 			\label{question1}
# 			Arbitrary content goes here.
# 			\begin{naqsymmathpart}
# 			Arbitrary content goes here.
# 			\begin{naqsolutions}
# 				\naqsolution $420$
# 				\naqsolution $\frac{5}{8}$
# 				\naqsolution $\left(3x+2\right)\left(2x+3\right)$
# 				\naqsolution $\surd2$
# 				\naqsolution $\frac{\surd\left(8x+5\right)\left(12x+12\right)}{\approx152318}+1204$
# 			\end{naqsolutions}
# 			\begin{naqhints}
# 				\naqhint Some hint
# 			\end{naqhints}
# 			\end{naqsymmathpart}
# 		\end{naquestion}
# 		
# 		\begin{naquestion}[individual=true]
# 			\label{question2}
# 			Arbitrary content goes here,
# 
# 			and there's a blank line, and another before the part:
# 			\begin{naqessaypart}
# 			Arbitrary content goes here.
# 			\begin{naqhints}
# 				\naqhint Some hint
# 			\end{naqhints}
# 			\end{naqessaypart}
# 		\end{naquestion}
# 		
# 		\begin{naquestionbank}[draw=1]
# 			\label{set}
# 			\naquestionref{question1}
# 			\naquestionref{question2}
# 			\begin{naqindexranges}
# 				\naqindexrange{0}{1}{1}
# 			\end{naqindexranges}
# 		\end{naquestionbank}
# 
# 		"""
# 
# 		dom = _buildDomFromString( _simpleLatexDocument((example,)))
# 		assert_that( dom.getElementsByTagName('naquestion'), has_length(2) )
# 		assert_that( dom.getElementsByTagName('naquestion')[0], is_(naquestion))
# 		assert_that( dom.getElementsByTagName('naquestion')[1], is_(naquestion))
# 
# 		assert_that( dom.getElementsByTagName('naquestionbank'), has_length( 1 ) )
# 		assert_that( dom.getElementsByTagName('naquestionbank')[0], is_(naquestionbank))
# 
# 		qset_object = dom.getElementsByTagName('naquestionbank')[0].assessment_object()
# 		assert_that(qset_object.questions, has_length(2) )
# 		assert_that(qset_object, has_property('draw', is_(1)))
# 		assert_that(qset_object.ntiid, contains_string('set'))
# 		assert_that(qset_object, has_property('ranges', has_length(1)))
# 		
# 		idx_range = qset_object.ranges[0]
# 		assert_that(idx_range, has_property('start', is_(0)))
# 		assert_that(idx_range, has_property('end', is_(1)))
# 		
# 		assert_that(qset_object, verifiably_provides(IQuestionBank))
# 	