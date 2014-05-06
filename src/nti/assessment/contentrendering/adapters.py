# -*- coding: utf-8 -*-
"""
adapters for externalizing some assessment objects

.. $Id: $
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from plasTeX.Renderers import render_children

from nti.contentrendering import interfaces as crd_interfaces


@interface.implementer(crd_interfaces.IJSONTransformer)
class _NAQuestionSetRefJSONTransformer(object):

	def __init__(self, element):
		self.el = element

	def transform(self):
		output = {}
		output['label'] = unicode(''.join(render_children( self.el.questionset.renderer, self.el.questionset.title )))
		output['MimeType'] = self.el.questionset.mimeType
		output['question-count'] = self.el.questionset.question_count
		output['Target-NTIID'] = self.el.questionset.ntiid
		return output


