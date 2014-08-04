#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from persistent import Persistent

from nti.externalization.externalization import WithRepr

from nti.schema.schema import EqHash

from . import parts
from . import interfaces
from ._util import TrivialValuedMixin as _TrivialValuedMixin

@interface.implementer(interfaces.IQSolution)
@WithRepr
class QSolution(Persistent):
	"""
	Base class for solutions. Its :meth:`grade` method
	will attempt to transform the input based on the interfaces
	this object implements and then call the :meth:`.QPart.grade` method.
	"""

	#: Defines the factory used by the :meth:`grade` method to construct
	#: a :class:`.IQPart` object. Also, instances are only equal if this value
	#: is equal
	_part_type = parts.QPart

	weight = 1.0

	def grade( self, response ):
		"""
		Convenience method for grading solutions that can be graded independent
		of their question parts.
		"""
		return self._part_type(solutions=(self,)).grade(response)


@interface.implementer(interfaces.IQMathSolution)
class QMathSolution(QSolution):
	"""
	Base class for the math hierarchy.
	"""

	allowed_units = None # No defined unit handling

	def __init__( self, *args, **kwargs ):
		super(QMathSolution,self).__init__()
		allowed_units = args[1] if len(args) > 1 else kwargs.get( 'allowed_units' )
		if allowed_units is not None:
			self.allowed_units = allowed_units # TODO: Do we need to defensively copy?

@EqHash('_part_type', 'weight', 'value',
		superhash=True)
class _EqualityValuedMixin(_TrivialValuedMixin):
	pass

@interface.implementer(interfaces.IQNumericMathSolution)
class QNumericMathSolution(_EqualityValuedMixin,QMathSolution):
	"""
	Numeric math solution.

	.. todo:: This grading mechanism is pretty poorly handled and compares
		by exact equality.
	"""

	_part_type = parts.QNumericMathPart

@interface.implementer(interfaces.IQFreeResponseSolution)
class QFreeResponseSolution(_EqualityValuedMixin,QSolution):
	"""
	Simple free-response solution.
	"""

	_part_type = parts.QFreeResponsePart

@interface.implementer(interfaces.IQSymbolicMathSolution)
class QSymbolicMathSolution(QMathSolution):
	"""
	Symbolic math grading is redirected through
	grading components for extensibility.
	"""

	_part_type = parts.QSymbolicMathPart

@interface.implementer(interfaces.IQLatexSymbolicMathSolution)
class QLatexSymbolicMathSolution(_EqualityValuedMixin,QSymbolicMathSolution):
	"""
	The answer is defined to be in latex.
	"""

	# TODO: Verification of the value? Minor transforms like adding $$?

@interface.implementer(interfaces.IQMatchingSolution)
class QMatchingSolution(_EqualityValuedMixin,QSolution):

	_part_type = parts.QMatchingPart

@interface.implementer(interfaces.IQMultipleChoiceSolution)
class QMultipleChoiceSolution(_EqualityValuedMixin,QSolution):

	_part_type = parts.QMultipleChoicePart

@interface.implementer(interfaces.IQMultipleChoiceMultipleAnswerSolution)
class QMultipleChoiceMultipleAnswerSolution(_EqualityValuedMixin,QSolution):
	"""
	The answer is defined as a list of selections which best represent
	the correct answer.
	"""

	_part_type = parts.QMultipleChoiceMultipleAnswerPart

@interface.implementer(interfaces.IQFillInTheBlankShortAnswerSolution)
class QFillInTheBlankShortAnswerSolution(_EqualityValuedMixin, QSolution):

	_part_type = parts.QFillInTheBlankShortAnswerPart

@interface.implementer(interfaces.IQFillInTheBlankWithWordBankSolution)
class QFillInTheBlankWithWordBankSolution(_EqualityValuedMixin, QSolution):

	_part_type = parts.QFillInTheBlankWithWordBankPart
