#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from zope import component

from nti.testing.layers import GCLayerMixin
from nti.testing.layers import ZopeComponentLayer
from nti.testing.layers import ConfiguringLayerMixin

import zope.testing.cleanup


class SharedConfiguringTestLayer(ZopeComponentLayer,
                                 GCLayerMixin,
                                 ConfiguringLayerMixin):

    set_up_packages = (
        'nti.mimetype',
        'nti.assessment',
        'nti.contentrendering',
        'nti.externalization',
        'nti.contentrendering_assessment',
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


class AssessmentRenderingTestCase(unittest.TestCase):

    layer = SharedConfiguringTestLayer


from nti.contentrendering.tests import simpleLatexDocumentText


def _simpleLatexDocument(maths):
    return simpleLatexDocumentText(preludes=(r'\usepackage{ntiassessment}',),
                                   bodies=maths)
simpleLatexDocument = _simpleLatexDocument
