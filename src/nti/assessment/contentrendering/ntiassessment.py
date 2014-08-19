#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
A macro package to support the writing of assessments inline with
the rest of content.

These are rendered into HTML as ``<object>`` tags with an NTIID
that matches an object to resolve from the dataserver. The HTML inside the object may or may
not be usable for basic viewing; client applications will use the Question object
from the dataserver to guide the ultimate rendering.

Example::

	\begin{naquestion}[individual=true]
		Arbitrary prefix content goes here. This may be rendered to the document.

		Questions consist of sequential parts, often just one part. The parts
		do not have to be homogeneous.
		\begin{naqsymmathpart}
		   Arbitrary content for this part goes here. This may be rendered to the document.

		   A part has one or more possible solutions. The solutions are of the same type,
		   determined implicitly by the part type.
		   \begin{naqsolutions}
			   \naqsolution[weight]<unit1, unit2> A possible solution. The weight, defaulting to one,
				   	is how "correct" this solution is. Some parts may have more compact
					representations of solutions.

					The units are only valid on math parts. If given, it may be an empty list  to specify
					that units are forbidden, or a list of optional units that may be included as part of the
					answer.
			\end{naqsolutions}
			\begin{naqhints}
				\naqhint Arbitrary content giving a hint for how to arrive at the correct
					solution.
			\end{naqhints}
			\begin{naqsolexplanation}
				Arbitrary content explaining how the correct solution is arrived at.
			\end{naqsolexplanation}
		\end{naqsymmathpart}
	\end{naquestion}

The TeX macro objects that correspond to \"top-level\" assessment objects
(those defined in :mod:`nti.assessment.interfaces`) will implement a method
called ``assessment_object``. This method can be called *after* the rendering
process is complete to gain the desired object. This object can then be
externalized or otherwise processed; this object is not itself part of
the TeX DOM.

.. $Id$
"""
# All of these have too many public methods
# pylint: disable=R0904

# "not callable" for the default values of None
# pylint: disable=E1102

# access to protected members -> _asm_local_content defined in this module
# pylint: disable=W0212

# "Method __delitem__ is abstract in Node and not overridden"
# pylint: disable=W0223

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import os

from zope import schema
from zope import interface
from zope.cachedescriptors.method import cachedIn
from zope.cachedescriptors.property import readproperty
from zope.mimetype.interfaces import mimeTypeConstraint

from plasTeX import Base
from plasTeX.Base import Crossref
from plasTeX.interfaces import IOptionAwarePythonPackage

from paste.deploy.converters import asbool

from nti.contentrendering import plastexids
from nti.contentrendering import interfaces as crd_interfaces
from nti.contentrendering.plastexpackages.ntilatexmacros import ntiincludevideo

from nti.externalization.datetime import datetime_from_string

from .. import parts
from .. import assignment
from .. import interfaces as as_interfaces

from ..randomized import parts as randomized_parts
from ..randomized import interfaces as rand_interfaces

from .ntibase import _AbstractNAQPart
from .ntibase import _LocalContentMixin

###
# Solutions
###

# Handle custom counter names
class naquestionsetname(Base.Command):
	unicode = ''

class naquestionname(Base.Command):
	unicode = ''

class naqsolutionnumname(Base.Command):
	unicode = ''

class naqsolutions(Base.List):

	counters = ['naqsolutionnum']
	args = '[ init:int ]'

	def invoke( self, tex ):
		# TODO: Why is this being done?
		res = super(naqsolutions, self).invoke( tex )

		if 'init' in self.attributes and self.attributes['init']:
			self.ownerDocument.context.counters[self.counters[0]].setcounter(self.attributes['init'])
		elif self.macroMode != Base.Environment.MODE_END:
			self.ownerDocument.context.counters[self.counters[0]].setcounter(0)

		return res

	def digest( self, tokens ):
		# After digesting loop back over the children moving nodes before
		# the first item into the first item
		# TODO: Why is this being done?
		res = super(naqsolutions, self).digest(tokens)
		if self.macroMode != Base.Environment.MODE_END:
			nodesToMove = []

			for node in self:

				if isinstance(node, Base.List.item):
					nodesToMove.reverse()
					for nodeToMove in nodesToMove:
						self.removeChild(nodeToMove)
						node.insert(0, nodeToMove)
					break

				nodesToMove.append(node)

		return res

_LocalContentMixin._asm_ignorable_renderables += (naqsolutions,)

class naqsolution(Base.List.item):

	args = '[weight:float] <units>'

	# We use <> for the units list because () looks like a geometric
	# point, and there are valid answers like that.
	# We also do NOT use the :list conversion, because if the units list
	# has something like an (escaped) % in it, plasTeX fails to tokenize the list
	# Instead, we work with the TexFragment object ourself

	def invoke( self, tex ):
		# TODO: Why is this being done? Does the counter matter?
		self.counter = naqsolutions.counters[0]
		self.position = self.ownerDocument.context.counters[self.counter].value + 1
		#ignore the list implementation
		return Base.Command.invoke(self,tex)

	def units_to_text_list(self):
		"""Find the units, if any, and return a list of their text values"""
		units = self.attributes.get( 'units' )
		if units:
			# Remove trailing delimiter and surrounding whitespace. For consecutive
			# text parts, we have to split ourself
			result = []
			for x in units:
				# We could get elements (Macro/Command) or strings (plastex.dom.Text)
				if getattr( x, 'tagName', None ) == 'math':
					raise ValueError( "Math cannot be roundtripped in units. Try unicode symbols" )
				x = unicode(x).rstrip( ',' ).strip()
				result.extend( x.split( ',' ) )
			return result

	def units_to_html(self):
		units = self.units_to_text_list()
		if units:
			return ','.join( units )

_LocalContentMixin._asm_ignorable_renderables += (naqsolution,)

###
# Explanations
###

class naqsolexplanation(_LocalContentMixin, Base.Environment):
	pass

_LocalContentMixin._asm_ignorable_renderables += (naqsolexplanation,)

###
# Parts
###

# NOTE: Part Node's MUST be named 'naq'XXX'part'

class naqnumericmathpart(_AbstractNAQPart):
	"""
	Solutions are treated as numbers for the purposes of grading.
	"""

	part_factory = parts.QNumericMathPart
	part_interface = as_interfaces.IQNumericMathPart
	soln_interface = as_interfaces.IQNumericMathSolution

class naqsymmathpart(_AbstractNAQPart):
	"""
	Solutions are treated symbolicaly for the purposes of grading.
	"""

	part_factory = parts.QSymbolicMathPart
	part_interface = as_interfaces.IQSymbolicMathPart
	soln_interface = as_interfaces.IQLatexSymbolicMathSolution

class naqfreeresponsepart(_AbstractNAQPart):
	part_factory = parts.QFreeResponsePart
	part_interface = as_interfaces.IQFreeResponsePart
	soln_interface = as_interfaces.IQFreeResponseSolution

class naqmodeledcontentpart(_AbstractNAQPart):
	"""
	This is a base part, and while it matches our internal
	implementation, it is not actually meant for authoring.
	External intent is better expressed with :class:`naqessaypart`
	"""
	soln_interface = None
	part_factory = parts.QModeledContentPart
	part_interface = as_interfaces.IQModeledContentPart

class naqessaypart(naqmodeledcontentpart):
	r"""
	A part having a body that is intended to be large (multi-paragraphs)
	potentially even containing whiteboards. This part CANNOT
	be auto-graded and has no solution.

	Example::

		\begin{naquestion}[individual=true]
			Arbitrary content goes here.
			\begin{naqessaypart}
			Arbitrary content goes here.
			\begin{naqhints}
				\naqhint Some hint
			\end{naqhints}
			\end{naqessaypart}
		\end{naquestion}
	"""

class naqmultiplechoicepart(_AbstractNAQPart):
	r"""
	A multiple-choice part (usually used as the sole part to a question).
	It must have a child listing the possible choices; the solutions are collapsed
	into this child; at least one of them must have a weight equal to 1::

		\begin{naquestion}
			Arbitrary prefix content goes here.
			\begin{naqmultiplechoicepart}
			   Arbitrary content for this part goes here.
			   \begin{naqchoices}
			   		\naqchoice Arbitrary content for the choice.
					\naqchoice[1] Arbitrary content for this choice; this is the right choice.
					\naqchoice[0.5] This choice is half correct.
				\end{naqchoices}
				\begin{naqsolexplanation}
					Arbitrary content explaining how the correct solution is arrived at.
				\end{naqsolexplanation}
			\end{naqmultiplechoicepart}
		\end{naquestion}
	"""

	part_factory = parts.QMultipleChoicePart
	part_interface = as_interfaces.IQMultipleChoicePart
	soln_interface = as_interfaces.IQMultipleChoiceSolution

	#forcePars = True

	def _asm_choices(self):
		return [x._asm_local_content for x in self.getElementsByTagName( 'naqchoice' )]

	def _asm_object_kwargs(self):
		return { 'choices': self._asm_choices() }

	def digest( self, tokens ):
		res = super(naqmultiplechoicepart,self).digest( tokens )
		# Validate the document structure: we have a naqchoices child with
		# at least two of its own children, and at least one weight == 1. There is no explicit solution
		_naqchoices = self.getElementsByTagName( 'naqchoices' )
		assert len(_naqchoices) == 1
		_naqchoices = _naqchoices[0]
		assert len(_naqchoices) > 1, "Must have more than one choice"
		assert any( (_naqchoice.attributes['weight'] == 1.0 for _naqchoice in _naqchoices) )
		assert len(self.getElementsByTagName( 'naqsolutions' )) == 0

		# Tranform the implicit solutions into explicit 0-based solutions
		_naqsolns = self.ownerDocument.createElement( 'naqsolutions' )
		_naqsolns.macroMode = self.MODE_BEGIN
		for i, _naqchoice in enumerate(_naqchoices):
			if _naqchoice.attributes['weight']:
				_naqsoln = self.ownerDocument.createElement( 'naqsolution' )
				_naqsoln.attributes['weight'] = _naqchoice.attributes['weight']
				# Also put the attribute into the argument source, for presentation
				_naqsoln.argSource = '[%s]' % _naqsoln.attributes['weight']
				_naqsoln.appendChild( self.ownerDocument.createTextNode( str(i) ) )
				_naqsolns.appendChild( _naqsoln )
		self.insertAfter( _naqsolns, _naqchoices )
		return res

	def invoke(self, tex):
		token = super(naqmultiplechoicepart, self).invoke(tex)
		if self.randomize:
			self.part_factory = randomized_parts.QRandomizedMultipleChoicePart
			self.part_interface = rand_interfaces.IQRandomizedMultipleChoicePart
		return token

class naqmultiplechoicemultipleanswerpart(_AbstractNAQPart):
	r"""
	A multiple-choice / multiple-answer part (usually used as the sole part to a question).
	It must have a child listing the possible choices; the solutions are collapsed
	into this child; at least one of them must have a weight equal to 1::.  Further the all
	solutions with a weight of 1:: are required to be submitted to receive credit for the
	question

		\begin{naquestion}
			Arbitrary prefix content goes here.
			\begin{naqmultiplechoicemultipleanswerpart}
			        Arbitrary content for this part goes here.
				\begin{naqchoices}
			   		\naqchoice Arbitrary content for the choices.
					\naqchoice[1] This is one part of a right choice.
					\naqchoice[1] This is another part of a right choice.
	                        \end{naqchoices}
				\begin{naqsolexplanation}
					Arbitrary content explaining how the correct solution is arrived at.
				\end{naqsolexplanation}
			\end{naqmultiplechoicemultipleanswerpart}
		\end{naquestion}
	"""

	part_factory = parts.QMultipleChoiceMultipleAnswerPart
	part_interface = as_interfaces.IQMultipleChoiceMultipleAnswerPart
	soln_interface = as_interfaces.IQMultipleChoiceMultipleAnswerSolution

	part_randomized_factory = randomized_parts.QRandomizedMultipleChoiceMultipleAnswerPart
	part_randomized_interface = rand_interfaces.IQRandomizedMultipleChoiceMultipleAnswerPart
			
	def _asm_choices(self):
		return [x._asm_local_content for x in self.getElementsByTagName( 'naqchoice' )]

	def _asm_object_kwargs(self):
		return { 'choices': self._asm_choices() }

	def _asm_solutions(self):
		solutions = []
		# By definition, there can only be one solution element.
		solution_el = self.getElementsByTagName( 'naqsolution' )[0]
		solution = self.soln_interface( solution_el.answer )
		weight = solution_el.attributes['weight']
		if weight is not None:
			solution.weight = weight
		solutions.append(solution)
		return solutions

	def digest( self, tokens ):
		res = super(naqmultiplechoicemultipleanswerpart, self).digest(tokens)
		# Validate the document structure: we have a naqchoices child
		# with at least two of its own children, and at least one
		# weight == 1.  There is no explicit solution
		_naqchoices = self.getElementsByTagName( 'naqchoices' )
		assert len(_naqchoices) == 1

		_naqchoices = _naqchoices[0]
		assert len(_naqchoices) > 1, "Must have more than one choice"
		assert any( (_naqchoice.attributes['weight'] == 1.0 for _naqchoice in _naqchoices) )
		assert len(self.getElementsByTagName( 'naqsolutions' )) == 0

		# Tranform the implicit solutions into a list of 0-based indices.
		_naqsolns = self.ownerDocument.createElement( 'naqsolutions' )
		_naqsolns.macroMode = _naqsolns.MODE_BEGIN
		_naqsoln = self.ownerDocument.createElement( 'naqsolution' )
		_naqsoln.attributes['weight'] = 1.0
		_naqsoln.argSource = '[1.0]'
		_naqsoln.answer = []
		for i, _naqchoice in enumerate(_naqchoices):
			if _naqchoice.attributes['weight'] and _naqchoice.attributes['weight'] == 1:
				_naqsoln.answer.append( i )
		_naqsolns.appendChild( _naqsoln )
		self.insertAfter( _naqsolns, _naqchoices )
		return res

	def invoke(self, tex):
		token = super(naqmultiplechoicemultipleanswerpart, self).invoke(tex)
		if self.randomize:
			self.part_factory = self.part_randomized_factory
			self.part_interface = self.part_randomized_interface
		return token

class naqfilepart(_AbstractNAQPart):
	r"""
	A part specifying that the user must upload a file::

	   \begin{naquestion}
	       Arbitrary prefix content.
		   \begin{naqfilepart}(application/pdf,text/*,.txt)[1024]
		      Arbitrary part content.
		   \end{naqfilepart}
		\end{naquestion}

	An (effectively required) argument in parenthesis is a list of
	mimetypes and file extensions to allow; to allow arbitrary types
	use ``*/*,*`` (the former allows all mime types, the latter allows
	all extensions). As another example, to allow PDF files with any
	extension, use ``application/pdf,*`` or to allow anything that might
	be a PDF, try ``*/*,.pdf``. A good list for documents might be
	``*/*,.txt,.doc,.docx,.pdf``

	The optional argument in square brackets is the max size of the
	file in kilobytes; the example above thus specifies a 1MB cap.
	"""

	args = "(types:list:str)[size:int]"

	part_interface = as_interfaces.IQFilePart
	part_factory = parts.QFilePart
	soln_interface = None

	_max_file_size = None
	_allowed_mime_types = ()
	_allowed_extensions = ()

	@property
	def allowed_mime_types(self):
		return ','.join(self._allowed_mime_types) if self._allowed_mime_types else None

	def _asm_solutions(self):
		"Solutions currently unsupported"
		return ()

	def _asm_object_kwargs(self):
		kw = {}
		for k in 'allowed_extensions', 'allowed_mime_types', 'max_file_size':
			mine = getattr(self, '_' + k)
			if mine:
				kw[k] = mine
		return kw

	def digest( self, tokens ):
		res = super(naqfilepart,self).digest(tokens)

		if self.attributes.get('size'):
			self._max_file_size = self.attributes['size'] * 1024 # KB to bytes
		if self.attributes.get('types'):
			for mime_or_ext in self.attributes['types']:
				if mimeTypeConstraint(mime_or_ext):
					self._allowed_mime_types += (mime_or_ext,)
				elif mime_or_ext.startswith('.') or mime_or_ext == '*':
					self._allowed_extensions += (mime_or_ext,)
				else: # pragma: no cover
					raise ValueError("Type is not MIME, extension, or wild", mime_or_ext )
		return res

class naqmatchingpart(_AbstractNAQPart):
	r"""
	A matching part (usually used as the sole part to a question).
	It must have two children, one listing the possible labels, with the
	correct solution's index in brackets, and the other listing the possible
	values::

		\begin{naquestion}
			Arbitrary prefix content goes here.
			\begin{naqmatchingpart}
			   Arbitrary content for this part goes here.
			   \begin{naqmlabels}
			   		\naqmlabel[2] What is three times two?
					\naqmlabel[0] What is four times three?
					\naqmlabel[1] What is five times two thousand?
				\end{naqmlabels}
				\begin{naqmvalues}
					\naqmvalue Twelve
					\naqmvalue Ten thousand
					\naqmvalue Six
				\end{naqmvalues}
				\begin{naqsolexplanation}
					Arbitrary content explaining how the correct solution is arrived at.
				\end{naqsolexplanation}
			\end{naqmatchingpart}
		\end{naquestion}
	"""

	part_factory = parts.QMatchingPart
	part_interface = as_interfaces.IQMatchingPart
	soln_interface = as_interfaces.IQMatchingSolution

	# randomized
	
	randomized_part_factory = randomized_parts.QRandomizedMatchingPart
	randomized_part_interface = rand_interfaces.IQRandomizedMatchingPart
			
	#forcePars = True

	def _asm_labels(self):
		return [x._asm_local_content for x in self.getElementsByTagName( 'naqmlabel' )]

	def _asm_values(self):
		return [x._asm_local_content for x in self.getElementsByTagName( 'naqmvalue' )]

	def _asm_object_kwargs(self):
		return { 'labels': self._asm_labels(),
				 'values': self._asm_values() }

	def _asm_solutions(self):
		solutions = []
		solution_els = self.getElementsByTagName('naqsolution')
		for solution_el in solution_els:
			solution = self.soln_interface( solution_el.answer )
			weight = solution_el.attributes['weight']
			if weight is not None:
				solution.weight = weight
			solutions.append( solution )
		return solutions

	def digest( self, tokens ):
		res = super(naqmatchingpart,self).digest( tokens )
		# Validate the document structure: we have a naqlabels child with
		# at least two of its own children, an naqvalues child of equal length
		# and a proper matching between the two
		if self.macroMode != Base.Environment.MODE_END:
			_naqmlabels = self.getElementsByTagName('naqmlabels')
			assert len(_naqmlabels) == 1
			_naqmlabels = _naqmlabels[0]
			assert len(_naqmlabels) > 1, "Must have more than one label; instead got: " + \
										 str([x for x in _naqmlabels])

			_naqmvalues = self.getElementsByTagName('naqmvalues')
			assert len(_naqmvalues) == 1
			_naqmvalues = _naqmvalues[0]
			assert len(_naqmvalues) == len(_naqmlabels), "Must have exactly one value per label"

			for i in range(len(_naqmlabels)):
				assert any( (_naqmlabel.attributes['answer'] == i for _naqmlabel in _naqmlabels) )
			assert len(self.getElementsByTagName('naqsolutions')) == 0

			# Tranform the implicit solutions into an array
			answer = {}
			_naqsolns = self.ownerDocument.createElement('naqsolutions')
			_naqsolns.macroMode = _naqsolns.MODE_BEGIN
			for i, _naqmlabel in enumerate(_naqmlabels):
				answer[i] = _naqmlabel.attributes['answer']
			_naqsoln = self.ownerDocument.createElement('naqsolution')
			_naqsoln.attributes['weight'] = 1.0

			# Also put the attribute into the argument source, for presentation
			_naqsoln.argSource = '[%s]' % _naqsoln.attributes['weight']
			_naqsoln.answer = answer
			_naqsolns.appendChild( _naqsoln )
			self.insertAfter( _naqsolns, _naqmvalues)
		return res

	def invoke(self, tex):
		token = super(naqmatchingpart, self).invoke(tex)
		if self.randomize:
			self.part_factory = self.randomized_part_factory
			self.part_interface = self.randomized_part_interface
		return token

class naqorderingpart(naqmatchingpart):
	r"""
	\begin{naquestion}
		Arbitrary prefix content goes here.
		\begin{naqorderingpart}
		   ...
		\end{naqorderingpart}
	\end{naquestion}
	"""
	part_factory = parts.QOrderingPart
	part_interface = as_interfaces.IQOrderingPart
	soln_interface = as_interfaces.IQOrderingSolution
	
	randomized_part_factory = randomized_parts.QRandomizedOrderingPart
	randomized_part_interface = rand_interfaces.IQRandomizedOrderingPart

_LocalContentMixin._asm_ignorable_renderables += (_AbstractNAQPart,)

from .ntibase import naqvalue

class naqchoices(Base.List):
	pass

class naqmlabels(Base.List):
	pass

class naqmvalues(Base.List):
	pass

class naqchoice(naqvalue):
	args = "[weight:float]"

class naqmlabel(naqvalue):
	args = "[answer:int]"

class naqmvalue(naqvalue):
	pass

class naqordereditem(naqvalue):
	args = 'id:str'

class naqordereditems(Base.List):
	pass

class naqhints(Base.List):
	pass

class naqhint(_LocalContentMixin, Base.List.item):

	def _after_render(self, rendered):
		self._asm_local_content = rendered

_LocalContentMixin._asm_ignorable_renderables += (naqchoices,
												  naqmlabels,
												  naqmvalues,
												  naqvalue,
												  naqchoice,
												  naqmlabel,
												  naqmvalue,
												  naqhints,
												  naqhint,
												  naqordereditems,
												  naqordereditem)

class naqvideo(ntiincludevideo):
	blockType = True

###
# Question
###

# make them available in this module

from nti.assessment.contentrendering.ntiquestion import naquestion 
from nti.assessment.contentrendering.ntiquestion import naqindexrange
from nti.assessment.contentrendering.ntiquestion import naquestionref 
from nti.assessment.contentrendering.ntiquestion import naquestionset
from nti.assessment.contentrendering.ntiquestion import naqindexranges
from nti.assessment.contentrendering.ntiquestion import naquestionbank
from nti.assessment.contentrendering.ntiquestion import naquestionsetref
from nti.assessment.contentrendering.ntiquestion import naquestionbankref
from nti.assessment.contentrendering.ntiquestion import narandomizedquestionset
from nti.assessment.contentrendering.ntiquestion import narandomizedquestionsetref

# avoid warning
naquestion = naquestion
naquestionref = naquestionref
naquestionset = naquestionset
naqindexranges = naqindexranges
naquestionbank = naquestionbank
naquestionsetref = naquestionsetref
naquestionbankref = naquestionbankref
narandomizedquestionset = narandomizedquestionset
narandomizedquestionsetref = narandomizedquestionsetref

###
# Alibra
###

from nti.assessment.contentrendering.ntialibra import naqinput
from nti.assessment.contentrendering.ntialibra import naqregex
from nti.assessment.contentrendering.ntialibra import naqregexes
from nti.assessment.contentrendering.ntialibra import naqregexref
from nti.assessment.contentrendering.ntialibra import naqwordbank
from nti.assessment.contentrendering.ntialibra import naqwordentry
from nti.assessment.contentrendering.ntialibra import naqblankfield
from nti.assessment.contentrendering.ntialibra import naqpaireditem
from nti.assessment.contentrendering.ntialibra import naqpaireditems
from nti.assessment.contentrendering.ntialibra import naqwordbankref
from nti.assessment.contentrendering.ntialibra import _WordBankMixIn
from nti.assessment.contentrendering.ntialibra import naquestionfillintheblankwordbank
from nti.assessment.contentrendering.ntialibra import naqfillintheblankshortanswerpart
from nti.assessment.contentrendering.ntialibra import naqfillintheblankwithwordbankpart

naqregexref = naqregexref
naqblankfield = naqblankfield
naqwordbankref = naqwordbankref
naquestionfillintheblankwordbank = naquestionfillintheblankwordbank

_LocalContentMixin._asm_ignorable_renderables += (_WordBankMixIn,
												  naqinput,
												  naqregex,
												  naqregexes,
												  naqwordentry,
												  naqwordbank,
												  naqindexrange,
												  naqpaireditem,
												  naqpaireditems,
												  naqindexranges,
												  naqfillintheblankwithwordbankpart,
												  naqfillintheblankshortanswerpart)

###
# Assignments
###

class naassignmentpart(_LocalContentMixin,
					   Base.Environment):
	r"""
	One part of an assignment. These are always nested inside
	an :class:`naassignment` environment.

	Example::
		\begin{naquestionset}
			\label{set}
			\naquestionref{question}
		\end{naquestionset}

		\begin{naasignmentpart}[auto_grade=true]{set}
			Local content
		\end{naassignmentpart}

	"""

	args = "[options:dict:str] <title:str:source> question_set:idref"

	@cachedIn('_v_assessment_object')
	def assessment_object(self):
		question_set = self.idref['question_set'].assessment_object()
		return assignment.QAssignmentPart( content=self._asm_local_content,
										   question_set=question_set,
										   auto_grade=asbool(self.attributes.get('options',{}).get('auto_grade')),
										   title=self.attributes.get('title'))

class naassignmentname(Base.Command):
	unicode = ''

@interface.implementer(crd_interfaces.IEmbeddedContainer)
class naassignment(_LocalContentMixin,
				   Base.Environment,
				   plastexids.NTIIDMixin):
	r"""
	Assignments specify some options such as availability dates,
	some local content, and finish up nesting the parts
	of the assignment as ``naassignmentpart`` elements.

	Example::

		\begin{naassignment}[not_before_date=2014-01-13,category=homework,public=true]<Homework>
			\label{assignment}
			Some introductory content.

			\begin{naasignmentpart}[auto_grade=true]{set}<Easy Part>
				Local content
			\end{naassignmentpart}
		\end{naquestionset}

	"""

	args = "[options:dict:str] <title:str:source>"

	# Only classes with counters can be labeled, and \label sets the
	# id property, which in turn is used as part of the NTIID (when no
	# NTIID is set explicitly)
	counter = 'naassignment'
	_ntiid_cache_map_name = '_naassignment_ntiid_map'
	_ntiid_allow_missing_title = True
	_ntiid_suffix = 'naq.asg.'
	_ntiid_title_attr_name = 'ref' # Use our counter to generate IDs if no ID is given
	_ntiid_type = as_interfaces.NTIID_TYPE

	#: From IEmbeddedContainer
	mimeType = u'application/vnd.nextthought.assessment.assignment'
	
	@cachedIn('_v_assessment_object')
	def assessment_object(self):
		# FIXME: We want these to be relative, not absolute, so they
		# can be made absolute based on when the course begins.
		# How to represent that? Probably need some schema transformation
		# step in nti.externalization? Or some auixilliary data fields?
		options = self.attributes.get('options') or ()
		def _parse(key, default_time):
			if key in options:
				val = options[key]
				if 'T' not in val:
					val += default_time

				# Now parse it, assuming that any missing timezone should be treated
				# as local timezone
				dt = datetime_from_string(
							val,
							assume_local=True,
							local_tzname=self.ownerDocument.userdata.get('document_timezone_name'))
				return dt

		# If they give no timestamp, make it midnight
		not_before = _parse('not_before_date', 'T00:00')
		# For after, if they gave us no time, make it just before
		# midnight. Together, this has the effect of intuitively defining
		# the range of dates as "the first instant of before to the last minute of after"
		not_after = _parse('not_after_date', 'T23:59')

		# Public/ForCredit.
		# It's opt-in for authoring and opt-out for code
		is_non_public = True
		if 'public' in options and asbool(options['public']):
			is_non_public = False

		result = assignment.QAssignment(
						content=self._asm_local_content,
						available_for_submission_beginning=not_before,
						available_for_submission_ending=not_after,
						parts=[part.assessment_object() for part in
							   self.getElementsByTagName('naassignmentpart')],
						title=self.attributes.get('title'),
						is_non_public=is_non_public)
		if 'category' in options:
			result.category_name = \
				as_interfaces.IQAssignment['category_name'].fromUnicode( options['category'] )

		errors = schema.getValidationErrors( as_interfaces.IQAssignment, result )
		if errors: # pragma: no cover
			raise errors[0][1]

		result.ntiid = self.ntiid
		return result

	@readproperty
	def containerId(self):
		parentNode = self.parentNode
		while (not hasattr(parentNode, 'filename')) or (parentNode.filename is None):
			parentNode = parentNode.parentNode
		return parentNode.ntiid

class naassignmentref(Crossref.ref):
	r"""
	A reference to the label of a question set.
	"""

	@readproperty
	def assignment(self):
		return self.idref['label']

###
# ProcessOptions
###

def ProcessOptions( options, document ):
	# We are not setting up any global state here,
	# only making changes to the document, so its
	# fine that this runs each time we are imported
	document.context.newcounter('naquestion')
	document.context.newcounter('naassignment')
	document.context.newcounter('naquestionset')
	document.context.newcounter('naqsolutionnum')
	document.context.newcounter('naquestionbank')
	document.context.newcounter('narandomizedquestionset')
	document.context.newcounter('naquestionfillintheblankwordbank')

#: The directory in which to find our templates.
#: Used by plasTeX because we implement IPythonPackage
template_directory = os.path.abspath(os.path.dirname(__file__))

#: The directory containing our style files
texinputs_directory = os.path.abspath(os.path.dirname(__file__))

interface.moduleProvides(IOptionAwarePythonPackage)
