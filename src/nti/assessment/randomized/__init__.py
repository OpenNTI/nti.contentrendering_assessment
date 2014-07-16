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

from zope.security.management import queryInteraction

from nti.dataserver import users
from nti.dataserver import interfaces as nti_interfaces

def get_current_user():
    interaction = queryInteraction()
    participations = list(getattr(interaction, 'participations', None) or ())
    participation = participations[0] if participations else None
    principal = getattr(participation, 'principal', None)
    return principal.id if principal is not None else None

def get_user(user=None):
    user = get_current_user() if user is None else user
    if user is not None and not nti_interfaces.IUser.providedBy(user):
        user = users.User.get_user(str(user))
    return user

def randomize(user=None):
    user = get_user(user)        
    if user is not None:
        intids = component.getUtility(zc.intid.IIntIds)
        uid = intids.getId(user)
        generator = random.Random(uid)
        return generator
    return None

def shuffle_list(generator, target):
    generator.shuffle(target)
    return target
