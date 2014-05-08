#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Implementations and support for question parts.

.. $Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import os.path

from zope import interface
from zope import component
from zope.container import contained
from zope.mimetype.interfaces import mimeTypeConstraint
from zope.schema.interfaces import ConstraintNotSatisfied

from persistent import Persistent

from nti.utils.schema import SchemaConfigured

from nti.contentfragments.interfaces import UnicodeContentFragment as _u

from nti.externalization.externalization import make_repr

from . import interfaces
from ._util import superhash
from .interfaces import convert_response_for_solution

@interface.implementer(interfaces.IQPart)
class QPart(SchemaConfigured,Persistent):
	"""
	Base class for parts. Its :meth:`grade` method will attempt to
	transform the input based on the interfaces this object
	implements, plus the interfaces of the solution, and then call the
	:meth:`_grade` method.
	"""

	#: The interface to which we will attempt to adapt ourself, the
	#: solution and the response when grading. Should be a
	#: class:`.IQPartGrader`. The response will have first been converted
	#: for the solution.
	grader_interface = interfaces.IQPartGrader

	#: The name of the grader we will attempt to adapt to. Defaults to the default,
	#: unnamed, adapter
	grader_name = _u('')

	#: If non-None, then we will always attempt to convert the
	#: response to this interface before attempting to grade.
	#: In this way parts that may not have a solution
	#: can always be sure that the response is at least
	#: of an appropriate type.
	response_interface = None

	hints = ()
	solutions = ()
	content = _u('')
	explanation = _u('')

	def grade( self, response ):

		if self.response_interface is not None:
			response = self.response_interface(response)

		if not self.solutions:
			# No solutions, no opinion
			return None

		result = 0.0
		for solution in self.solutions:
			# Attempt to get a proper solution
			converted = convert_response_for_solution(solution, response)
			# Graders return a true or false value. We are responsible
			# for applying weights to that
			value = self._grade(solution, converted)
			if value:
				result = self._weight(value, solution)
				break
		return result

	def _weight(self, result, solution):
		return 1.0 * solution.weight

	def _grade(self, solution, response):
		__traceback_info__ = solution, response, self.grader_name
		grader = component.getMultiAdapter((self, solution, response),
											self.grader_interface,
											name=self.grader_name)
		return grader()

	__repr__ = make_repr()

	def __eq__( self, other ):
		try:
			return self is other or (self._eq_instance(other)
									 and self.content == other.content
									 and self.hints == other.hints
									 and self.solutions == other.solutions
									 and self.explanation == other.explanation
									 and self.grader_interface == other.grader_interface
									 and self.grader_name == other.grader_name)
		except AttributeError:  # pragma: no cover
			return NotImplemented

	def _eq_instance( self, other ):
		return True

	def __ne__( self, other ):
		return not (self == other is True)

	def __hash__( self ):
		xhash = 47
		xhash ^= hash(self.content)
		xhash ^= superhash(self.hints)
		xhash ^= superhash(self.solutions)
		xhash ^= hash(self.explanation) << 5
		return xhash

@interface.implementer(interfaces.IQMathPart)
class QMathPart(QPart):

	def _eq_instance( self, other ):
		return isinstance(other, QMathPart)

@interface.implementer(interfaces.IQSymbolicMathPart)
class QSymbolicMathPart(QMathPart):

	grader_interface = interfaces.IQSymbolicMathGrader

	def _eq_instance( self, other ):
		return isinstance(other, QSymbolicMathPart)


@interface.implementer(interfaces.IQNumericMathPart)
class QNumericMathPart(QMathPart):

	def _eq_instance( self, other ):
		return isinstance(other, QNumericMathPart)

@interface.implementer(interfaces.IQMultipleChoicePart)
class QMultipleChoicePart(QPart):

	grader_interface = interfaces.IQMultipleChoicePartGrader
	choices = ()

	def __eq__( self, other ):
		try:
			return self is other or (isinstance(other, QMultipleChoicePart)
									 and super(QMultipleChoicePart, self).__eq__(other) is True
									 and self.choices == other.choices)
		except AttributeError:  # pragma: no cover
			return NotImplemented

	def __hash__(self):
		xhash = super(QMultipleChoicePart, self).__hash__()
		return xhash + superhash(self.choices)

@interface.implementer(interfaces.IQMultipleChoiceMultipleAnswerPart)
class QMultipleChoiceMultipleAnswerPart(QMultipleChoicePart):

	grader_interface = interfaces.IQMultipleChoiceMultipleAnswerPartGrader

@interface.implementer(interfaces.IQMatchingPart)
class QMatchingPart(QPart):

	grader_interface = interfaces.IQMatchingPartGrader

	labels = ()
	values = ()

	def __eq__( self, other ):
		try:
			return self is other or (isinstance(other, QMatchingPart)
									 and super(QMatchingPart, self).__eq__(other) is True
									 and self.labels == other.labels
									 and self.values == other.values)
		except AttributeError:  # pragma: no cover
			return NotImplemented

	def __hash__( self ):
		xhash = super(QMatchingPart, self).__hash__()
		return xhash + superhash( self.labels ) + superhash( self.values )

@interface.implementer(interfaces.IQFreeResponsePart)
class QFreeResponsePart(QPart):

	grader_name = 'LowerQuoteNormalizedStringEqualityGrader'

	def _eq_instance( self, other ):
		return isinstance(other, QFreeResponsePart)


@interface.implementer(interfaces.IQFilePart)
class QFilePart(QPart):

	response_interface = interfaces.IQFileResponse

	allowed_mime_types = ()
	allowed_extensions = ()
	max_file_size = None

	def _eq_instance(self,other):
		return (self.allowed_mime_types == other.allowed_mime_types
				and self.allowed_extensions == other.allowed_extensions
				and self.max_file_size == other.max_file_size)

	def grade(self, response):
		response = self.response_interface(response)
		# We first check our own constraints for submission
		# and refuse to even grade if they are not met
		if not self.is_mime_type_allowed( response.value.contentType ):
			raise ConstraintNotSatisfied(response.value.contentType, 'mimeType')
		if not self.is_filename_allowed( response.value.filename ):
			raise ConstraintNotSatisfied(response.value.filename, 'filename')
		if (self.max_file_size is not None and response.value.getSize() > self.max_file_size ):
			raise ConstraintNotSatisfied(response.value.getSize(), 'max_file_size')

		super(QFilePart,self).grade(response)

	def is_mime_type_allowed( self, mime_type ):
		if mime_type:
			mime_type = mime_type.lower() # only all lower case matches the production
		if (not mime_type # No input
			or not mimeTypeConstraint(mime_type) # Invalid
			or not self.allowed_mime_types ): # Empty list: all excluded
			return False

		major, minor = mime_type.split('/')
		if major == '*' or minor == '*':
			# Must be concrete
			return False

		for mt in self.allowed_mime_types:
			if mt == '*/*':
				# Total wildcard
				return True
			mt = mt.lower()
			if mt == mime_type:
				return True

			amajor, aminor = mt.split('/')

			# Wildcards are only reasonable in the minor part,
			# e.g., text/*.
			if aminor == minor or aminor == '*':
				if major == amajor:
					return True

	def is_filename_allowed( self, filename ):
		return (filename
				 and (os.path.splitext(filename.lower())[1] in self.allowed_extensions
					  or '*' in self.allowed_extensions))

@interface.implementer(interfaces.IQModeledContentPart)
class QModeledContentPart(QPart):

	response_interface = interfaces.IQModeledContentResponse

	def _eq_instance( self, other ):
		return isinstance(other, QModeledContentPart)

@interface.implementer(interfaces.IQFillInTheBlankShortAnswerPart)
class QFillInTheBlankShortAnswerPart(QPart):
	response_interface = interfaces.IQDictResponse
	grader_interface = interfaces.IQFillInTheBlankShortAnswerGrader

@interface.implementer(interfaces.IQFillInTheBlankWithWordBankPart)
class QFillInTheBlankWithWordBankPart(QPart, contained.Contained):

	response_interface = interfaces.IQDictResponse
	grader_interface = interfaces.IQFillInTheBlankWithWordBankGrader

	def _weight(self, result, solution):
		return result * solution.weight
