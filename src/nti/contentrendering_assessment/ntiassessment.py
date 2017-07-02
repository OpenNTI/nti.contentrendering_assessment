#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
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

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import os

from zope import interface

from zope.mimetype.interfaces import mimeTypeConstraint

from plasTeX import Base

from plasTeX.interfaces import IOptionAwarePythonPackage

from nti.assessment.interfaces import IQFilePart
from nti.assessment.interfaces import IQMatchingPart
from nti.assessment.interfaces import IQOrderingPart
from nti.assessment.interfaces import IQConnectingPart
from nti.assessment.interfaces import IQNumericMathPart
from nti.assessment.interfaces import IQFreeResponsePart
from nti.assessment.interfaces import IQMatchingSolution
from nti.assessment.interfaces import IQOrderingSolution
from nti.assessment.interfaces import IQSymbolicMathPart
from nti.assessment.interfaces import IQConnectingSolution
from nti.assessment.interfaces import IQModeledContentPart
from nti.assessment.interfaces import IQMultipleChoicePart
from nti.assessment.interfaces import IQNonGradableFilePart
from nti.assessment.interfaces import IQNumericMathSolution
from nti.assessment.interfaces import IQFreeResponseSolution
from nti.assessment.interfaces import IQMultipleChoiceSolution
from nti.assessment.interfaces import IQNonGradableMatchingPart
from nti.assessment.interfaces import IQNonGradableOrderingPart
from nti.assessment.interfaces import IQLatexSymbolicMathSolution
from nti.assessment.interfaces import IQNonGradableConnectingPart
from nti.assessment.interfaces import IQNonGradableFreeResponsePart
from nti.assessment.interfaces import IQNonGradableModeledContentPart
from nti.assessment.interfaces import IQNonGradableMultipleChoicePart
from nti.assessment.interfaces import IQMultipleChoiceMultipleAnswerPart
from nti.assessment.interfaces import IQMultipleChoiceMultipleAnswerSolution
from nti.assessment.interfaces import IQNonGradableMultipleChoiceMultipleAnswerPart

from nti.assessment.parts import QFilePart
from nti.assessment.parts import QMatchingPart
from nti.assessment.parts import QOrderingPart
from nti.assessment.parts import QConnectingPart
from nti.assessment.parts import QNumericMathPart
from nti.assessment.parts import QFreeResponsePart
from nti.assessment.parts import QSymbolicMathPart
from nti.assessment.parts import QModeledContentPart
from nti.assessment.parts import QMultipleChoicePart
from nti.assessment.parts import QNonGradableFilePart
from nti.assessment.parts import QNonGradableMatchingPart
from nti.assessment.parts import QNonGradableOrderingPart
from nti.assessment.parts import QNonGradableConnectingPart
from nti.assessment.parts import QNonGradableFreeResponsePart
from nti.assessment.parts import QNonGradableModeledContentPart
from nti.assessment.parts import QNonGradableMultipleChoicePart
from nti.assessment.parts import QMultipleChoiceMultipleAnswerPart
from nti.assessment.parts import QNonGradableMultipleChoiceMultipleAnswerPart

from nti.contentrendering.plastexpackages.ntilatexmacros import ntiincludevideo

from nti.contentrendering_assessment.ntibase import _AbstractNAQPart
from nti.contentrendering_assessment.ntibase import _LocalContentMixin

# Tags

from nti.contentrendering_assessment.ntibase import naqtag
from nti.contentrendering_assessment.ntibase import naqtags

naqtag = naqtag
naqtags = naqtags

# Solutions

from nti.contentrendering_assessment.ntisolution import naqsolution
from nti.contentrendering_assessment.ntisolution import naqsolutions
from nti.contentrendering_assessment.ntisolution import naqsolexplanation
from nti.contentrendering_assessment.ntisolution import naqsolutionnumname

naqsolution = naqsolution
naqsolutions = naqsolutions
naqsolexplanation = naqsolexplanation
naqsolutionnumname = naqsolutionnumname

_LocalContentMixin._asm_ignorable_renderables += (naqsolutions,
                                                  naqsolution,
                                                  naqsolexplanation)

# Parts

# NOTE: Part Node's MUST be named 'naq'XXX'part'


class naqnumericmathpart(_AbstractNAQPart):
    """
    Solutions are treated as numbers for the purposes of grading.
    """

    part_factory = QNumericMathPart
    part_interface = IQNumericMathPart
    soln_interface = IQNumericMathSolution


class naqsymmathpart(_AbstractNAQPart):
    """
    Solutions are treated symbolicaly for the purposes of grading.
    """

    part_factory = QSymbolicMathPart
    part_interface = IQSymbolicMathPart
    soln_interface = IQLatexSymbolicMathSolution


class naqfreeresponsepart(_AbstractNAQPart):

    part_factory = QFreeResponsePart
    part_interface = IQFreeResponsePart
    soln_interface = IQFreeResponseSolution

    nongradable_part_factory = QNonGradableFreeResponsePart
    nongradable_part_interface = IQNonGradableFreeResponsePart


class naqmodeledcontentpart(_AbstractNAQPart):
    """
    This is a base part, and while it matches our internal
    implementation, it is not actually meant for authoring.
    External intent is better expressed with :class:`naqessaypart`
    """
    soln_interface = None

    part_factory = QModeledContentPart
    part_interface = IQModeledContentPart

    nongradable_part_factory = QNonGradableModeledContentPart
    nongradable_part_interface = IQNonGradableModeledContentPart


class naqessaypart(naqmodeledcontentpart):
    """
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
    """
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

    part_factory = QMultipleChoicePart
    part_interface = IQMultipleChoicePart
    soln_interface = IQMultipleChoiceSolution

    nongradable_part_factory = QNonGradableMultipleChoicePart
    nongradable_part_interface = IQNonGradableMultipleChoicePart

    def _asm_choices(self):
        return [x._asm_local_content for x in self.getElementsByTagName('naqchoice')]

    def _asm_object_kwargs(self):
        result = {'choices': self._asm_choices()}
        if self._asm_is_gradable:
            result['randomized'] = self.randomize
        return result

    def digest(self, tokens):
        res = super(naqmultiplechoicepart, self).digest(tokens)
        # Validate the document structure: we have a naqchoices child with
        # at least two of its own children, and at least one weight == 1. There
        # is no explicit solution
        _naqchoices = self.getElementsByTagName('naqchoices')
        assert len(_naqchoices) == 1

        _naqchoices = _naqchoices[0]
        assert len(_naqchoices) > 1, "Must have more than one choice"

        if self._asm_is_gradable:
            assert any(x.attributes['weight'] == 1.0 for x in _naqchoices)
            assert len(self.getElementsByTagName('naqsolutions')) == 0

            # Tranform the implicit solutions into explicit 0-based solutions
            _naqsolns = self.ownerDocument.createElement('naqsolutions')
            _naqsolns.macroMode = self.MODE_BEGIN
            for i, _naqchoice in enumerate(_naqchoices):
                if _naqchoice.attributes['weight']:
                    _naqsoln = self.ownerDocument.createElement('naqsolution')
                    _naqsoln.attributes['weight'] = _naqchoice.attributes['weight']
                    # Also put the attribute into the argument source, for
                    # presentation
                    _naqsoln.argSource = u'[%s]' % _naqsoln.attributes['weight']
                    _text_node = self.ownerDocument.createTextNode(str(i))
                    _naqsoln.appendChild(_text_node)
                    _naqsolns.appendChild(_naqsoln)
            self.insertAfter(_naqsolns, _naqchoices)
        return res

    def invoke(self, tex):
        token = super(naqmultiplechoicepart, self).invoke(tex)
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

    part_factory = QMultipleChoiceMultipleAnswerPart
    part_interface = IQMultipleChoiceMultipleAnswerPart
    soln_interface = IQMultipleChoiceMultipleAnswerSolution

    nongradable_part_factory = QNonGradableMultipleChoiceMultipleAnswerPart
    nongradable_part_interface = IQNonGradableMultipleChoiceMultipleAnswerPart

    def _asm_choices(self):
        return [x._asm_local_content for x in self.getElementsByTagName('naqchoice')]

    def _asm_object_kwargs(self):
        result = {'choices': self._asm_choices()}
        if self._asm_is_gradable:
            result['randomized'] = self.randomize
        return result

    def _asm_solutions(self):
        solutions = []
        # By definition, there can only be one solution element.
        solution_el = self.getElementsByTagName('naqsolution')[0]
        solution = self.soln_interface(solution_el.answer)
        weight = solution_el.attributes['weight']
        if weight is not None:
            solution.weight = weight
        solutions.append(solution)
        return solutions

    def digest(self, tokens):
        res = super(naqmultiplechoicemultipleanswerpart, self).digest(tokens)

        # Validate the document structure: we have a naqchoices child
        # with at least two of its own children, and at least one
        # weight == 1.  There is no explicit solution
        _naqchoices = self.getElementsByTagName('naqchoices')
        assert len(_naqchoices) == 1

        _naqchoices = _naqchoices[0]
        assert len(_naqchoices) > 1, "Must have more than one choice"
        assert len(self.getElementsByTagName('naqsolutions')) == 0

        if self._asm_is_gradable:
            assert any(x.attributes['weight'] == 1.0 for x in _naqchoices)

            # Tranform the implicit solutions into a list of 0-based indices.
            _naqsolns = self.ownerDocument.createElement('naqsolutions')
            _naqsolns.macroMode = _naqsolns.MODE_BEGIN
            _naqsoln = self.ownerDocument.createElement('naqsolution')
            _naqsoln.attributes['weight'] = 1.0
            _naqsoln.argSource = u'[1.0]'
            _naqsoln.answer = []
            for i, _naqchoice in enumerate(_naqchoices):
                if _naqchoice.attributes['weight'] and _naqchoice.attributes['weight'] == 1:
                    _naqsoln.answer.append(i)
            _naqsolns.appendChild(_naqsoln)
            self.insertAfter(_naqsolns, _naqchoices)
        return res

    def invoke(self, tex):
        token = super(naqmultiplechoicemultipleanswerpart, self).invoke(tex)
        return token


class naqfilepart(_AbstractNAQPart):
    """
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

    soln_interface = None

    part_factory = QFilePart
    part_interface = IQFilePart

    nongradable_part_factory = QNonGradableFilePart
    nongradable_part_interface = IQNonGradableFilePart

    _max_file_size = None
    _allowed_mime_types = ()
    _allowed_extensions = ()

    @property
    def allowed_mime_types(self):
        return u','.join(self._allowed_mime_types) if self._allowed_mime_types else None

    def _asm_solutions(self):
        """
        Solutions currently unsupported
        """
        return ()

    def _asm_object_kwargs(self):
        kw = {}
        for k in 'allowed_extensions', 'allowed_mime_types', 'max_file_size':
            mine = getattr(self, '_' + k)
            if mine:
                kw[k] = mine
        return kw

    def digest(self, tokens):
        res = super(naqfilepart, self).digest(tokens)
        if self.attributes.get('size'):
            self._max_file_size = self.attributes['size'] * 1024  # KB to bytes
        if self.attributes.get('types'):
            for mime_or_ext in self.attributes['types']:
                if mimeTypeConstraint(mime_or_ext):
                    self._allowed_mime_types += (mime_or_ext,)
                elif mime_or_ext.startswith('.') or mime_or_ext == '*':
                    self._allowed_extensions += (mime_or_ext,)
                else:  # pragma: no cover
                    raise ValueError("Type is not MIME, extension, or wild",
                                     mime_or_ext)
        return res


class naqconnectingpart(_AbstractNAQPart):

    part_factory = QConnectingPart
    part_interface = IQConnectingPart
    soln_interface = IQConnectingSolution

    nongradable_part_factory = QNonGradableConnectingPart
    nongradable_part_interface = IQNonGradableConnectingPart

    def _asm_labels(self):
        return [x._asm_local_content for x in self.getElementsByTagName('naqmlabel')]

    def _asm_values(self):
        return [x._asm_local_content for x in self.getElementsByTagName('naqmvalue')]

    def _asm_object_kwargs(self):
        result = {'labels': self._asm_labels(),
                  'values': self._asm_values()}
        if self._asm_is_gradable:
            result['randomized'] = self.randomize
        return result

    def _asm_solutions(self):
        solutions = []
        solution_els = self.getElementsByTagName('naqsolution')
        for solution_el in solution_els:
            solution = self.soln_interface(solution_el.answer)
            weight = solution_el.attributes['weight']
            if weight is not None:
                solution.weight = weight
            solutions.append(solution)
        return solutions

    def digest(self, tokens):
        res = super(naqconnectingpart, self).digest(tokens)

        # Validate the document structure: we have a naqlabels child with
        # at least two of its own children, an naqvalues child of equal length
        # and a proper matching between the two
        if self.macroMode != Base.Environment.MODE_END:
            _naqmlabels = self.getElementsByTagName('naqmlabels')
            assert len(_naqmlabels) == 1
            _naqmlabels = _naqmlabels[0]
            assert len(_naqmlabels) > 1, \
                   "Must have more than one label; instead got: " + \
                   str([x for x in _naqmlabels])

            _naqmvalues = self.getElementsByTagName('naqmvalues')
            assert len(_naqmvalues) == 1

            _naqmvalues = _naqmvalues[0]
            assert len(_naqmvalues) == len(_naqmlabels), \
            	   "Must have exactly one value per label"

            for i in range(len(_naqmlabels)):
                assert any(x.attributes['answer'] == i for x in _naqmlabels)
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
            _naqsolns.appendChild(_naqsoln)
            self.insertAfter(_naqsolns, _naqmvalues)

        return res

    def invoke(self, tex):
        token = super(naqconnectingpart, self).invoke(tex)
        return token


class naqmatchingpart(naqconnectingpart):
    """
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

    part_factory = QMatchingPart
    part_interface = IQMatchingPart
    soln_interface = IQMatchingSolution

    nongradable_part_factory = QNonGradableMatchingPart
    nongradable_part_interface = IQNonGradableMatchingPart


class naqorderingpart(naqconnectingpart):
    r"""
    \begin{naquestion}
        Arbitrary prefix content goes here.
        \begin{naqorderingpart}
           ...
        \end{naqorderingpart}
    \end{naquestion}
    """
    part_factory = QOrderingPart
    part_interface = IQOrderingPart
    soln_interface = IQOrderingSolution

    nongradable_part_factory = QNonGradableOrderingPart
    nongradable_part_interface = IQNonGradableOrderingPart


_LocalContentMixin._asm_ignorable_renderables += (_AbstractNAQPart,)

from nti.contentrendering_assessment.ntibase import naqvalue


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


# Question


from nti.contentrendering_assessment.ntiquestion import naquestion
from nti.contentrendering_assessment.ntiquestion import naqindexrange
from nti.contentrendering_assessment.ntiquestion import naquestionref
from nti.contentrendering_assessment.ntiquestion import naquestionset
from nti.contentrendering_assessment.ntiquestion import naqindexranges
from nti.contentrendering_assessment.ntiquestion import naquestionbank
from nti.contentrendering_assessment.ntiquestion import naquestionname
from nti.contentrendering_assessment.ntiquestion import naquestionsetref
from nti.contentrendering_assessment.ntiquestion import naquestionbankref
from nti.contentrendering_assessment.ntiquestion import naquestionsetname
from nti.contentrendering_assessment.ntiquestion import narandomizedquestionset
from nti.contentrendering_assessment.ntiquestion import narandomizedquestionsetref

naquestion = naquestion
naquestionref = naquestionref
naquestionset = naquestionset
naquestionname = naquestionname
naqindexranges = naqindexranges
naquestionbank = naquestionbank
naquestionsetref = naquestionsetref
naquestionbankref = naquestionbankref
naquestionsetname = naquestionsetname
narandomizedquestionset = narandomizedquestionset
narandomizedquestionsetref = narandomizedquestionsetref

# Alibra

from nti.contentrendering_assessment.ntialibra import naqinput
from nti.contentrendering_assessment.ntialibra import naqregex
from nti.contentrendering_assessment.ntialibra import naqregexes
from nti.contentrendering_assessment.ntialibra import naqregexref
from nti.contentrendering_assessment.ntialibra import naqwordbank
from nti.contentrendering_assessment.ntialibra import naqwordentry
from nti.contentrendering_assessment.ntialibra import naqblankfield
from nti.contentrendering_assessment.ntialibra import naqpaireditem
from nti.contentrendering_assessment.ntialibra import naqpaireditems
from nti.contentrendering_assessment.ntialibra import naqwordbankref
from nti.contentrendering_assessment.ntialibra import _WordBankMixIn
from nti.contentrendering_assessment.ntialibra import naquestionfillintheblankwordbank
from nti.contentrendering_assessment.ntialibra import naqfillintheblankshortanswerpart
from nti.contentrendering_assessment.ntialibra import naqfillintheblankwithwordbankpart

naqregexref = naqregexref
naqblankfield = naqblankfield
naqwordbankref = naqwordbankref
naquestionfillintheblankwordbank = naquestionfillintheblankwordbank
naqfillintheblankshortanswerpart = naqfillintheblankshortanswerpart
naqfillintheblankwithwordbankpart = naqfillintheblankwithwordbankpart

_LocalContentMixin._asm_ignorable_renderables += (_WordBankMixIn,
                                                  naqinput,
                                                  naqregex,
                                                  naqregexes,
                                                  naqwordentry,
                                                  naqwordbank,
                                                  naqindexrange,
                                                  naqpaireditem,
                                                  naqpaireditems,
                                                  naqindexranges)

# Assignments

from nti.contentrendering_assessment.ntiassignment import naassignment
from nti.contentrendering_assessment.ntiassignment import naassignmentref
from nti.contentrendering_assessment.ntiassignment import naassignmentpart
from nti.contentrendering_assessment.ntiassignment import naassignmentname

naassignment = naassignment
naassignmentref = naassignmentref
naassignmentpart = naassignmentpart
naassignmentname = naassignmentname

# Polls

from nti.contentrendering_assessment.ntipoll import napoll
from nti.contentrendering_assessment.ntipoll import nasurvey
from nti.contentrendering_assessment.ntipoll import napollref
from nti.contentrendering_assessment.ntipoll import napollname
from nti.contentrendering_assessment.ntipoll import nasurveyref
from nti.contentrendering_assessment.ntipoll import nasurveyname

napoll = napoll
nasurvey = nasurvey
napollref = napollref
napollname = napollname
nasurveyref = nasurveyref
nasurveyname = nasurveyname

# ProcessOptions


def ProcessOptions(options, document):
    # We are not setting up any global state here,
    # only making changes to the document, so its
    # fine that this runs each time we are imported
    document.context.newcounter('napoll')
    document.context.newcounter('naquestion')
    document.context.newcounter('naassignment')
    document.context.newcounter('nasurvey')
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
