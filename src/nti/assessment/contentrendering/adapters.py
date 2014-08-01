# -*- coding: utf-8 -*-
"""
adapters for externalizing some assessment objects

.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six

from zope import interface

from plasTeX.Renderers import render_children

from nti.contentrendering.interfaces import IJSONTransformer

@interface.implementer(IJSONTransformer)
class _NAQuestionSetRefJSONTransformer(object):

	__slots__ = ('el',)

	def __init__(self, element):
		self.el = element

	def transform(self):
		title = self.el.questionset.title
		if not isinstance(title, six.string_types):
			title = unicode(''.join(render_children(self.el.questionset.renderer, title)))
		output = {'label': title}
		output['MimeType'] = self.el.questionset.mimeType
		output['Target-NTIID'] = self.el.questionset.ntiid
		output['question-count'] = self.el.questionset.question_count
		return output


