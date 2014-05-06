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
from ..parts import QMultipleChoicePart

@interface.implementer(interfaces.IQRandomizedQMultipleChoicePart)
class QRandomizedMultipleChoicePart(QMultipleChoicePart):
	grader_interface = interfaces.IQRandomizedMultipleChoicePartGrader

