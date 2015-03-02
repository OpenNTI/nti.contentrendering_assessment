#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from zope import component

from nti.testing.layers import find_test
from nti.testing.layers import GCLayerMixin
from nti.testing.layers import ZopeComponentLayer
from nti.testing.layers import ConfiguringLayerMixin

import zope.testing.cleanup

class SharedConfiguringTestLayer(ZopeComponentLayer,
								 GCLayerMixin,
								 ConfiguringLayerMixin):

	set_up_packages = (
					   'nti.contentrendering',
					   'nti.assessment',
					   'nti.externalization',
					   'nti.mimetype',
					   )

	@classmethod
	def setUp(cls):
		cls.setUpPackages()

	@classmethod
	def tearDown(cls):
		cls.tearDownPackages()
		zope.testing.cleanup.cleanUp()

	@classmethod
	def testSetUp(cls):
		pass

	@classmethod
	def testTearDown(cls):
		pass

import unittest

class AssessmentTestCase(unittest.TestCase):

	layer = SharedConfiguringTestLayer

from nti.contentrendering.tests import simpleLatexDocumentText

def _simpleLatexDocument(maths):
	return simpleLatexDocumentText(preludes=(br'\usepackage{ntiassessment}',),
									bodies=maths)
simpleLatexDocument = _simpleLatexDocument

# ==========

from hamcrest.core.base_matcher import BaseMatcher

class GradeMatcher(BaseMatcher):
	def __init__(self, value, response):
		super(GradeMatcher, self).__init__()
		self.value = value
		self.response = response

	def _matches(self, solution):
		return solution.grade(self.response) == self.value

	def describe_to(self, description):
		description.append_text('solution that grades ').append_text(str(self.response)).append_text(' as ').append_text(str(self.value))

	def describe_mismatch(self, item, mismatch_description):
		mismatch_description.append_text('solution ').append_text(str(type(item))).append_text(' ').append_text(repr(item))
		if getattr(item, 'allowed_units', ()):
			mismatch_description.append_text(" units " + str(item.allowed_units))

		mismatch_description.append_text(' graded ' + repr(self.response) + ' as ' + str(not self.value))

	def __repr__(self):
		return 'solution that grades as ' + str(self.value)

def grades_correct(response):
	return GradeMatcher(True, response)
grades_right = grades_correct

def grades_wrong(response):
	return GradeMatcher(False, response)
