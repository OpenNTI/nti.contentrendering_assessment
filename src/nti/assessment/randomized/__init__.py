#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import random
import hashlib

from zope import component

from zc.intid import IIntIds

from zope.security.management import queryInteraction

from nti.dataserver.users import User
from nti.dataserver.interfaces import IUser

from .interfaces import ISha224Randomized

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

def randomize(user=None, context=None):
    user = get_user(user)        
    if user is not None:
        uid = component.getUtility(IIntIds).getId(user)
        use_sha224 = context is not None and ISha224Randomized.providedBy(context)
        if use_sha224:
            hexdigest = hashlib.sha224(bytes(uid)).hexdigest()
            generator = random.Random(long(hexdigest, 16))
        else:
            generator = random.Random(uid)
        return generator
    return None

def shuffle_list(generator, target):
    generator.shuffle(target)
    return target

def questionbank_random(context, user=None):
    generator = random.Random() if context.srand else randomize(user=user, context=context)
    return generator

def questionbank_question_chooser(context, questions=None, user=None):
    result = []
    questions = questions or context.questions
    generator = questionbank_random(context, user=user)
    if generator and questions and context.draw and context.draw < len(questions):
        ranges = context.ranges or ()
        if not ranges:
            sample_idxs = generator.sample(xrange(0, len(questions)), context.draw)
            sample_idxs.sort() # keep order
            result.extend(questions[idx] for idx in sample_idxs)
        elif context.draw == len(ranges):
            for r in ranges:
                idx = generator.randint(r.start, r.end)
                result.append(questions[idx])
                generator = questionbank_random(context, user=user)
        else:
            result.extend(questions)
    else:
        result.extend(questions)
    return result
