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

from zc.intid import IIntIds

from zope.security.management import queryInteraction

from nti.dataserver.users import User
from nti.dataserver.interfaces import IUser

def get_current_user():
    interaction = queryInteraction()
    participations = list(getattr(interaction, 'participations', None) or ())
    participation = participations[0] if participations else None
    principal = getattr(participation, 'principal', None)
    return principal.id if principal is not None else None

def get_user(user=None):
    user = get_current_user() if user is None else user
    if user is not None and not IUser.providedBy(user):
        user = User.get_user(str(user))
    return user

def randomize(user=None):
    user = get_user(user)        
    if user is not None:
        uid = component.getUtility(IIntIds).getId(user)
        generator = random.Random(uid)
        return generator
    return None

def shuffle_list(generator, target):
    generator.shuffle(target)
    return target
