#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
$Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from . import interfaces
from ._util import TrivialValuedMixin

from persistent import Persistent

@interface.implementer(interfaces.IQHint)
class QHint(Persistent):
	"""
	Base class for hints.
	"""

@interface.implementer(interfaces.IQTextHint)
class QTextHint(TrivialValuedMixin, QHint):
	"""
	A text hint.
	"""

@interface.implementer(interfaces.IQHTMLHint)
class QHTMLHint(TrivialValuedMixin, QHint):
	"""
	A text hint.
	"""
