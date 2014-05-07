#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from . import interfaces
from ..graders import MatchingPartGrader
from ..graders import MultipleChoiceGrader

@interface.implementer(interfaces.IQRandomizedMatchingPartGrader)
class RandomizedMatchingPartGrader(MatchingPartGrader):
	pass

@interface.implementer(interfaces.IQRandomizedMultipleChoicePartGrader)
class RandomizedMultipleChoiceGrader(MultipleChoiceGrader):
	pass
