#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
External object decorators having to do with assessments.

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
		random.seed(uid)  # Seed w/ the user intid

	def shuffle_list(self, result, name):
		target = result.get(name, None)
		if target:
			random.shuffle(target)
		
@component.adapter(rand_interfaces.IQRandomizedMatchingPart)
class QRandomizedMatchingPartDecorator(QRandomizedDecorator):

	def _do_decorate_external(self, context, result):
		self.randomize()
		self.shuffle_list(result, 'labels')
		self.shuffle_list(result, 'values')
		
@component.adapter(rand_interfaces.IQRandomizedMultipleChoicePart)
class QRandomizedMultipleChoicePartDecorator(QRandomizedDecorator):

	def _do_decorate_external(self, context, result):
		self.randomize()
		self.shuffle_list(result, 'choices')
