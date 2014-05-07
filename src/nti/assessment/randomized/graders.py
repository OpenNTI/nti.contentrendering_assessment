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

import zc.intid

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
		intids = component.getUtility(zc.intid.IIntIds)
		uid = intids.getId(user)
		generator = random.Random()
		generator.seed(uid)  # Seed w/ the user intid
		return generator
	return None
		
def shuffle_list(generator, target):
	generator.shuffle(target)
	return target

@interface.implementer(interfaces.IQRandomizedMatchingPartGrader)
class RandomizedMatchingPartGrader(MatchingPartGrader):

	def _to_response_dict(self, the_dict):
		the_dict = MatchingPartGrader._to_int_dict(self, the_dict)
		generator = randomize()
		if generator is not None:
			values = list(self.part.values)
			original = {v:idx for idx, v in enumerate(values)}
			shuffled = {idx:v for idx, v in enumerate(shuffle_list(generator, values))}
			for k in list(the_dict.keys()):
				idx = the_dict[k]
				uidx = original.get(shuffled.get(idx), idx)
				the_dict[k] = uidx
		return the_dict

	response_converter = _to_response_dict

@interface.implementer(interfaces.IQRandomizedMultipleChoicePartGrader)
class RandomizedMultipleChoiceGrader(MultipleChoiceGrader):
	pass
