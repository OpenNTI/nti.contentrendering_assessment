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

from ..interfaces import QUESTION_SET_MIME_TYPE

def _render_children(renderer, nodes, strip=True):
	if not isinstance(nodes, six.string_types):
		result = unicode(''.join(render_children(renderer, nodes)))
	else:
		result = nodes.decode("utf-8") if isinstance(nodes, bytes) else nodes
	return result.strip() if strip and result else result

@interface.implementer(IJSONTransformer)
class _NAQuestionSetRefJSONTransformer(object):
	
	def __init__(self, element):
		self.el = element

	def transform(self):
		title = self.el.questionset.title
		title = _render_children(self.el.questionset.renderer, title)
		output = {'label': title}
		output['MimeType'] = QUESTION_SET_MIME_TYPE
		output['Target-NTIID'] = self.el.questionset.ntiid
		output['question-count'] = self.el.questionset.question_count
		return output

@interface.implementer(IJSONTransformer)
class _NAAssignmentRefJSONTransformer(object):
	
	def __init__(self, element):
		self.el = element

	def transform(self):
		title = self.el.assignment.title
		title = _render_children(self.el.assignment.renderer, title)
		output = {'label': title, 'title': title}
		output['MimeType'] = self.el.assignment.mimeType
		output['Target-NTIID'] = self.el.assignment.ntiid
		output['NTIID'] = self.el.assignment.ntiid
		output['ContainerId'] = self.el.assignment.containerId
		return output
