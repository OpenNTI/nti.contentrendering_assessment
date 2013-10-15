#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
$Id$
"""
from __future__ import unicode_literals, print_function, absolute_import
__docformat__ = "restructuredtext en"

from zope import interface
from zope import schema
from zope.mimetype.interfaces import mimeTypeConstraint

from nti.utils import schema as dmschema

NTIID_TYPE = 'NAQ'

TypedIterable = dmschema.IndexedIterable

from nti.contentfragments.schema import LatexFragmentTextLine as _LatexTextLine
from nti.contentfragments.schema import HTMLContentFragment as _HTMLContentFragment
from nti.contentfragments.schema import TextUnicodeContentFragment as _ContentFragment

class IQHint(interface.Interface):
	"""
	Information intended to help a student complete a question.

	This may have such attributes as 'difficulty' or 'assistance level'.

	It my be inline or be a link (reference) to other content.
	"""
	# TODO: Model this better

class IQTextHint(IQHint):
	"""
	A hint represented as text.
	"""
	value = _ContentFragment( title="The hint text" )

class IQHTMLHint(IQHint):
	"""
	A hint represented as html.
	"""
	value = _HTMLContentFragment( title="The hint html" )

class IQSolution(interface.Interface):

	weight = schema.Float( title="The relative correctness of this solution, from 0 to 1",
						   description="""If a question has multiple possible solutions, some may
						   be more right than others. This is captured by the weight field. If there is only
						   one right answer, then it has a weight of 1.0.
						   """,
						   min=0.0,
						   max=1.0,
						   default=1.0 )

# It seems like the concepts of domain and range may come into play here,
# somewhere

class IQPart(interface.Interface):
	"""
	One generally unnumbered (or only locally numbered) portion of a :class:`Question`
	which requires a response.
	"""

	content = _ContentFragment( title="The content to present to the user for this portion, if any." )
	hints = TypedIterable( title="Any hints that pertain to this part",
						   value_type=dmschema.Object(IQHint, title="A hint for the part") )
	solutions = TypedIterable( title="Acceptable solutions for this question part in no particular order.",
								description="All solutions must be of the same type, and there must be at least one.",
								value_type=dmschema.Object(IQSolution, title="A solution for this part")	)
	explanation = _ContentFragment( title="An explanation of how the solution is arrived at.",
									default='' )

	def grade( response ):
		"""
		Determine the correctness of the given response. Usually this will do its work
		by delegating to a registered :class:`IQPartGrader`.

		:param response: An :class:`IResponse` object representing the student's input for this
			part of the question.
		:return: A value that can be interpreted as a boolean, indicating correct (``True``) or incorrect
			(``False``) response. A return value of ``None`` indicates no opinion. If solution weights are
			taken into account, this will be a floating point number between 0.0 (incorrect) and 1.0 (perfect).
		"""

class IQMathPart(IQPart):
	"""
	A question part whose answer lies in the math domain.
	"""

class IQPartGrader(interface.Interface):
	"""
	An object that knows how to grade solutions, given a response. Should be registered
	as a multi-adapter on the question part, solution, and response types.
	"""

	def __call__( ):
		"""
		Implement the contract of :meth:`IQPart.grade`.
		"""

class IQSingleValuedSolution(IQSolution):
	"""
	A solution consisting of a single value.
	"""
	value = interface.Attribute( "The correct value" )


class IQMultiValuedSolution(IQSolution):
	"""
	A solution consisting of a set of values.
	"""
	value = schema.List( title="The correct answer selections",
			     description="The correct answer as a tuple of items which are a zero-based index into the choices list.",
			     min_length=0,
			     value_type=schema.TextLine( title="The value" ) )

class IQMathSolution(IQSolution):
	"""
	A solution in the math domain. Generally intended to be abstract and
	specialized.
	"""

	allowed_units = TypedIterable( title="Strings naming unit suffixes",
								 description="""
									Numbers or expressions may have units. Sometimes the correct
									answer depends on the correct unit being applied; sometimes the unit is optional,
									and sometimes there must not be a unit (it is a dimensionless quantity).

									If this attribute is ``None`` (the default) no special handling of units
									is attempted.

									If this attribute is an empty sequence, no units are accepted.

									If this attribute consists of one or more strings, those are units to accept.
									Include the empty string (last) to make units optional.""",
								min_length=0,
								required=False,
								value_type=schema.TextLine( title="The unit" ) )

class IQNumericMathSolution(IQMathSolution,IQSingleValuedSolution):
	"""
	A solution whose correct answer is numeric in nature, and
	should be graded according to numeric equivalence.
	"""

	value = schema.Float( title="The correct numeric answer; really an arbitrary number" )

class IQSymbolicMathSolution(IQMathSolution):
	"""
	A solution whose correct answer should be interpreted symbolically.
	For example, "12π" (twelve pi, not 37.6...) or "√2" (the square root of two, not
	1.4...).

	This is intended to be further subclassed to support specific types of
	symbolic interpretation.
	"""

class IQSymbolicMathPart(IQMathPart):
	"""
	A part whose solutions are symbolic math.
	"""

class IQNumericMathPart(IQMathPart):
	"""
	A part whose solutions are numeric math.
	"""

class IQLatexSymbolicMathSolution(IQSymbolicMathSolution,IQSingleValuedSolution):
	"""
	A solution whose correct answer should be interpreted
	as symbols, parsed from latex.
	"""

	value = _LatexTextLine( title="The LaTeX form of the correct answer.",
							min_length=1 )

class IResponseToSymbolicMathConverter(interface.Interface):
	"""
	An object that knows how to produce a symbolic (parsed) version
	of a response. Should be registered as a multi-adapter on the
	solution and response type.
	"""

	def convert( response ):
		"""
		Produce and return a symbolic version of the response.
		"""

class IQSymbolicMathGrader(IQPartGrader):
	"""
	Specialized grader for symbolic math expressions.
	"""

class IQMultipleChoiceSolution(IQSolution,IQSingleValuedSolution):
	"""
	A solution whose correct answer is drawn from a fixed list
	of possibilities. The student is expected to choose from
	the options presented. These will typically be used in isolation as a single part.
	"""

	value = interface.Attribute( "The correct answer as the zero-based index into the choices list." )

class IQMultipleChoicePart(IQPart):
	"""
	A question part that asks the student to choose between a fixed set
	of alternatives.
	"""

	choices = schema.List( title="The choice strings to present to the user.",
						   min_length=1,
						   description="""Presentation order may matter, hence the list. But for grading purposes,
						   the order does not matter and simple existence within the set is sufficient.""",
						   value_type=_ContentFragment( title="A rendered value" ) )
	solutions = TypedIterable( title="The multiple-choice solutions",
							   min_length=1,
							   value_type=dmschema.Object( IQMultipleChoiceSolution, title="Multiple choice solution" ) )

class IQMultipleChoicePartGrader(IQPartGrader):
	"""
	Specialized interface for grading multiple choice questions.
	"""


class IQMultipleChoiceMultipleAnswerSolution(IQSolution,IQMultiValuedSolution):
	"""
	A solution whose correct answer is drawn from a fixed list
	of possibilities. The student is expected to choose from
	the options presented. These will typically be used in isolation as a single part.
	"""

	value = schema.List( title="The correct answer selections",
			     description="The correct answer as a tuple of items which are a zero-based index into the choices list.",
			     min_length=1,
			     value_type=schema.Int( title="The value",
						    min=0) )


class IQMultipleChoiceMultipleAnswerPart(IQMultipleChoicePart):
	"""
	A question part that asks the student to choose between a fixed set
	of alternatives.
	"""

	solutions = TypedIterable( title="The multiple-choice solutions",
				   min_length=1,
				   value_type=dmschema.Object( IQMultipleChoiceMultipleAnswerSolution, title="Multiple choice / multiple answer solution" ) )


class IQMultipleChoiceMultipleAnswerPartGrader(IQPartGrader):
	"""
	Specialized interface for grading multiple choice questions.
	"""


class IQFreeResponseSolution(IQSolution,IQSingleValuedSolution):
	"""
	A solution whose correct answer is simple text.
	"""

	value = schema.Text( title="The correct text response", min_length=1 )

class IQFreeResponsePart(IQPart):
	"""
	A part whose correct answer is simple text.
	"""

class IQMatchingSolution(IQSolution):
	"""
	Matching solutions are the correct mapping from keys to values.
	Generally this will be a mapping of integer locations, but it may also be
	a mapping of actual keys and values. The response is an IDictResponse of ints or key/values.
	"""

	value = schema.Dict( title="The correct mapping." )

class IQMatchingPart(IQPart):
	"""
	A question part that asks the student to connect items from one column (labels) with
	items in another column (values) forming a one-to-one and onto mapping.

	The possibilities are represented as two equal-length lists because order of presentation does matter,
	and to permit easy grading:	responses are submitted as mapping from label position to value position.
	"""

	labels = schema.List( title="The list of labels",
						  min_length=2,
						  value_type=_ContentFragment( title="A label-column value" ) )
	values = schema.List( title="The list of values",
						  min_length=2,
						  value_type=_ContentFragment( title="A value-column value" ) )
	solutions = TypedIterable( title="The matching solution",
							   min_length=1,
							   value_type=dmschema.Object( IQMatchingSolution, title="Matching solution" ) )

class IQMatchingPartGrader(IQPartGrader):
	"""
	A grader for matching questions.
	"""

class IQFilePart(IQPart):
	"""
	A part that requires the student to upload a file
	from their own computer. Note that this part cannot be
	automatically graded, it can merely be routed to a
	responsible party for grading manually.

	In this interface you specify MIME types and/or
	filename extensions that can be used as input. If the incoming
	data matches any of the types or extensions, it will be allowed.
	To allow anything (unwise), include "*/*" in the ``allowed_mime_types``
	or include "*" in the ``allowed_extensions``.
	"""

	allowed_mime_types = TypedIterable( title="Mime types that are accepted for upload",
										min_length=1,
										value_type=schema.Text(title="An allowed mimetype",
															   constraint=mimeTypeConstraint) )
	allowed_extensions = TypedIterable( title="Extensions like '.doc' that are accepted for upload",
										min_length=0,
										value_type=schema.Text(title="An allowed extension") )

	def is_mime_type_allowed( mime_type ):
		"""
		Return whether or not the given mime type, which must match
		the mime type constraint, is one of the allowed types of this
		part, taking into account wildcards.
		"""

class IQuestion(interface.Interface):
	"""
	A question consists of one or more parts (typically one) that require answers.
	It may have prefacing text. It may have other metadata, such as what
	concepts it relates to (e.g., Common Core Standards numbers); such concepts
	will be domain specific.
	"""

	content = schema.Text( title="The content to present to the user, if any." )
	parts = schema.List( title="The ordered parts of the question.",
						 min_length=1,
						 value_type=dmschema.Object( IQPart, title="A question part" ) )

class IQuestionSet(interface.Interface):
	"""
	An ordered group of related questions generally intended to be
	completed as a unit (aka, a Quiz or worksheet).
	"""

	questions = TypedIterable( title="The ordered questions in the set.",
							   min_length=1,
							   value_type=dmschema.Object( IQuestion, title="The questions" ) )

class IQResponse(interface.Interface):
	"""
	A response submitted by the student.
	"""

class IQTextResponse(IQResponse):
	"""
	A response submitted as text.
	"""

	value = schema.Text( title="The response text" )

class IQListResponse(IQResponse):
	"""
	A response submitted as a list.
	"""

	value = schema.List( title="The response list",
			     min_length=1,
			     value_type=schema.TextLine(title="The value") )

class IQDictResponse(IQResponse):
	"""
	A response submitted as a mapping between keys and values.
	"""
	value = schema.Dict( title="The response dictionary",
						 key_type=schema.TextLine( title="The key" ),
						 value_type=schema.TextLine(title="The value") )

IQMathSolution.setTaggedValue( 'response_type', IQTextResponse )
IQFreeResponseSolution.setTaggedValue( 'response_type', IQTextResponse )
IQMultipleChoiceSolution.setTaggedValue( 'response_type', IQTextResponse )
IQMultipleChoiceMultipleAnswerSolution.setTaggedValue( 'response_type', IQListResponse )
IQMatchingSolution.setTaggedValue( 'response_type', IQDictResponse )

def convert_response_for_solution(solution, response):
	"""
	Given a solution and a response, attempt to adapt
	the response to the type needed by the grader.
	Uses the `response_type` tagged value on the interfaces implemented
	by the grader.
	"""
	if not IQSolution.providedBy( solution ):
		# Well, nothing to be done, no info given
		return response

	for iface in interface.providedBy( solution ).flattened():
		response_type = iface.queryTaggedValue( 'response_type' )
		if response_type:
			result = response_type( response, alternate=None ) # adapt or return if already present
			if result is not None:
				response = result
				break

	return response

###
# Objects having to do with the assessment process itself.
# There is a three part lifecycle: The source object,
# the submission, and finally the assessed value. The three
# parts have similar structure.
###

class IQuestionSubmission(interface.Interface):
	"""
	A student's submission in response to a question.

	These will typically be transient objects.
	"""

	questionId = schema.TextLine( title="Identifier of the question being responded to." )
	parts = TypedIterable( title="Ordered submissions, one for each part of the question.",
						   description="""The length must match the length of the questions. Each object must be
						   adaptable into the proper :class:`IQResponse` object (e.g., a string or dict).""" )


class IQAssessedPart(interface.Interface):
	"""
	The assessed value of a single part.

	These will generally be persistent values that are echoed back to clients.
	"""
	# TODO: Matching to question?

	submittedResponse = dmschema.Object( IQResponse,
									   title="The response as the student submitted it.")
	assessedValue = schema.Float( title="The relative correctness of the submitted response, from 0.0 (entirely wrong) to 1.0 (perfectly correct)",
								  min=0.0,
								  max=1.0,
								  default=0.0 )

class IQAssessedQuestion(interface.Interface):
	"""
	The assessed value of a student's submission for a single question.

	These will typically be persistent values, echoed back to clients.
	"""

	questionId = schema.TextLine( title="Identifier of the question being responded to." )
	parts = TypedIterable( title="Ordered assessed values, one for each part of the question.",
						   value_type=dmschema.Object( IQAssessedPart, title="The assessment of a part." ) )


class IQuestionSetSubmission(interface.Interface):
	"""
	A student's submission in response to an entire question set.

	These will generally be transient objects.
	"""

	questionSetId = schema.TextLine( title="Identifier of the question set being responded to." )
	questions = TypedIterable( title="Submissions, one for each question in the set.",
							   description="""Order is not important. Depending on the question set,
							   missing answers may or may not be allowed; the set may refuse to grade, or simply consider them wrong.""",
							   value_type=dmschema.Object( IQuestionSubmission, title="The submission for a particular question.") )

class IQAssessedQuestionSet(interface.Interface):
	"""
	The assessed value of a student's submission to an entire question set.

	These will usually be persistent values that are also echoed back to clients.
	"""

	questionSetId = schema.TextLine( title="Identifier of the question set being responded to." )
	questions = TypedIterable( title="Assessed questions, one for each question in the set.",
							   value_type=dmschema.Object( IQAssessedQuestion, title="The assessed value for a particular question.") )

class IQuestionMap(interface.common.mapping.IReadMapping):
	"""
	Something to look questions/question sets up by their IDs.
	"""
