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

import zc.intid

from pyramid.threadlocal import get_current_request

from nti.dataserver import users

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
        generator = random.Random(uid)
        return generator
    return None

def shuffle_list(generator, target):
    generator.shuffle(target)
    return target
