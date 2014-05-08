#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
$Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from nti.app.renderers.decorators import AbstractAuthenticatedRequestAwareDecorator

from . import randomize
from . import interfaces as rand_interfaces

class QRandomizedDecorator(AbstractAuthenticatedRequestAwareDecorator):

	def randomize(self):
		return randomize(self.remoteUser)

@component.adapter(rand_interfaces.IQRandomizedMatchingPart)
class QRandomizedMatchingPartDecorator(QRandomizedDecorator):

	def _do_decorate_external(self, context, result):
		values = list(result['values'])
		generator = self.randomize()
		generator.shuffle(result['values'])
		original = {idx:v for idx, v in enumerate(values)}
		shuffled = {v:idx for idx, v in enumerate(result['values'])}
		for solution in result['solutions']:
			value = solution['value']
			for k in list(value.keys()):
				idx = value[k]
				uidx = shuffled[original[idx]]
				value[k] = uidx
		
@component.adapter(rand_interfaces.IQRandomizedMultipleChoicePart)
class QRandomizedMultipleChoicePartDecorator(QRandomizedDecorator):

	def _do_decorate_external(self, context, result):
		generator = self.randomize()
		generator.shuffle(result['choices'])
