#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
$Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import random
import zope.intid

from zope import component

from nti.app.renderers.decorators import AbstractAuthenticatedRequestAwareDecorator

from . import interfaces as rand_interfaces

class QRandomizedDecorator(AbstractAuthenticatedRequestAwareDecorator):

	def randomize(self):
		intids = component.getUtility(zope.intid.IIntIds)
		uid = intids.getId(self.remoteUser)
		generator = random.Random(uid)
		return generator

@component.adapter(rand_interfaces.IQRandomizedMatchingPart)
class QRandomizedMatchingPartDecorator(QRandomizedDecorator):

	def _do_decorate_external(self, context, result):
		generator = self.randomize()
		generator.shuffle(result['values'])
		
@component.adapter(rand_interfaces.IQRandomizedMultipleChoicePart)
class QRandomizedMultipleChoicePartDecorator(QRandomizedDecorator):

	def _do_decorate_external(self, context, result):
		generator = self.randomize()
		generator.shuffle(result['choices'])
