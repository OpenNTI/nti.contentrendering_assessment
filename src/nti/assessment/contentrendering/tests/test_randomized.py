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

import unittest

from nti.assessment.randomized import interfaces as rand_interfaces
from nti.assessment.contentrendering.ntiassessment import naquestion

from nti.testing.matchers import verifiably_provides

from nti.assessment.contentrendering.tests import _simpleLatexDocument
from nti.assessment.contentrendering.tests import SharedConfiguringTestLayer

from nti.contentrendering.tests import buildDomFromString as _buildDomFromString

class TestRandomized(unittest.TestCase):

	layer = SharedConfiguringTestLayer

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
		assert_that(part_el.part_interface, is_(rand_interfaces.IQRandomizedMultipleChoicePart))
