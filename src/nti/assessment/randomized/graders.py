#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import random

from zope import component
from zope import interface

import zope.intid.IIntIds

from pyramid.threadlocal import get_current_request

from nti.dataserver import users

from . import interfaces
from ..graders import MatchingPartGrader
from ..graders import MultipleChoiceGrader

def get_current_user():
	request = get_current_request()
	username = request.authenticated_userid if request is not None else None
	return username

def randomize(username=None):
	username = username or get_current_user()
	user = users.User.get_user(username) if username else None
	if user is not None:
		intids = component.getUtility(zope.intid.IIntIds)
		uid = intids.getId(user)
		random.seed(uid)  # Seed w/ the user intid
		return True
	return False
		
@interface.implementer(interfaces.IQRandomizedMatchingPartGrader)
class RandomizedMatchingPartGrader(MatchingPartGrader):

	def labels(self):
		result = self.part.labels
		if randomize():
			random.shuffle(result)
		return result

	def values(self):
		result = self.part.values
		if randomize():
			random.shuffle(result)
		return result

@interface.implementer(interfaces.IQRandomizedMultipleChoicePartGrader)
class RandomizedMultipleChoiceGrader(MultipleChoiceGrader):
	pass
