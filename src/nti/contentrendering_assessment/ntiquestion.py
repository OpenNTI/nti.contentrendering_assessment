#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from six import text_type
from six import string_types

from zope import schema
from zope import interface

from zope.cachedescriptors.method import cachedIn

from zope.cachedescriptors.property import readproperty

from persistent.list import PersistentList

from plasTeX import Base

from plasTeX.Renderers import render_children

from nti.assessment.interfaces import IQuestion
from nti.assessment.interfaces import NTIID_TYPE
from nti.assessment.interfaces import IQuestionSet
from nti.assessment.interfaces import QUESTION_SET_MIME_TYPE

from nti.assessment.question import QQuestion
from nti.assessment.question import QQuestionSet

from nti.assessment.randomized.question import QQuestionBank
from nti.assessment.randomized.question import QRandomizedQuestionSet

from nti.assessment.randomized.interfaces import IQuestionBank
from nti.assessment.randomized.interfaces import IQuestionIndexRange
from nti.assessment.randomized.interfaces import IRandomizedQuestionSet

from nti.contentprocessing._compat import text_

from nti.contentrendering import plastexids
from nti.contentrendering import interfaces as crd_interfaces

from nti.contentrendering_assessment.ntibase import naassesmentref
from nti.contentrendering_assessment.ntibase import _AbstractNAQTags
from nti.contentrendering_assessment.ntibase import _LocalContentMixin

from nti.property.property import alias


class naquestionname(Base.Command):
    unicode = u''


class naquestionsetname(Base.Command):
    unicode = u''


class naquestion(_LocalContentMixin, _AbstractNAQTags,
                 Base.Environment, plastexids.NTIIDMixin):

    args = '[individual:str]'

    blockType = True

    # Only classes with counters can be labeled, and \label sets the
    # id property, which in turn is used as part of the NTIID
    # (when no NTIID is set explicitly)
    counter = 'naquestion'

    # Depending on the presence or absence of newlines
    # (and hence real paragraphs) within our top-level,
    # we either get children elements that are <par>
    # elements, or not. If they are <par> elements, the last
    # one contains the actual naqXXXpart children we are interested in.
    # If we set this to true, then we don't have that ambiguous
    # case; however, we wind up collecting too much content
    # into the `content` of the parts so we can't
    forcePars = False

    _ntiid_suffix = 'naq.'
    _ntiid_type = NTIID_TYPE
    _ntiid_title_attr_name = 'ref'  # Use our counter to generate IDs if no ID is given
    _ntiid_allow_missing_title = True
    _ntiid_cache_map_name = '_naquestion_ntiid_map'

    def invoke(self, tex):
        _t = super(naquestion, self).invoke(tex)
        if      'individual' in self.attributes \
            and self.attributes['individual'] == 'individual=true':
            self.attributes['individual'] = 'true'
        return _t

    @property
    def _ntiid_get_local_part(self):
        result = self.attributes.get('probnum') \
              or self.attributes.get("questionnum")
        if not result:
            result = super(naquestion, self)._ntiid_get_local_part
        return result

    def _asm_videos(self):
        videos = ()
        return u''.join(videos)

    def _asm_question_parts(self):
        # See forcePars.
        # There may be a better way to make this determination.
        # naqassignment and the naquestionset don't suffer from this
        # issue because they can specifically ask for known child
        # nodes by name...we rely on convention
        def _filter(x):
            result = hasattr(x, 'tagName') and x.tagName.startswith('naq') \
                 and x.tagName.endswith('part')
            return result

        generator = (x for x in self.allChildNodes if _filter(x))
        return [x.assessment_object() for x in generator if hasattr(x, 'assessment_object')]

    def _createQuestion(self):
        result = QQuestion(content=self._asm_local_content,
                           parts=self._asm_question_parts(),
                           tags=self._asm_tags())
        return result

    @cachedIn('_v_assessment_object')
    def assessment_object(self):
        result = self._createQuestion()
        errors = schema.getValidationErrors(IQuestion, result)
        if errors:  # pragma: no cover
            raise errors[0][1]
        result.ntiid = self.ntiid  # copy the id
        return result


class naquestionref(naassesmentref):
    
    assesment = alias('question')

    @readproperty
    def question(self):
        return self.idref['label']


@interface.implementer(crd_interfaces.IEmbeddedContainer)
class naquestionset(_AbstractNAQTags, Base.List, plastexids.NTIIDMixin):
    """
    Question sets are a list of questions that should be submitted
    together. For authoring, questions are included in a question
    set by reference, and a question set can be composed of any
    other labeled questions found within the same processing unit.

    Example::

        \begin{naquestion}[individual=true]
                \label{question}
                ...
        \end{naquestion}

        \begin{naquestionset}<My Title>
                \label{set}
                \naquestionref{question}
        \end{naquestionset}
    """

    args = "[options:dict:str] <title:str:source>"

    # Only classes with counters can be labeled, and \label sets the
    # id property, which in turn is used as part of the NTIID (when no NTIID
    # is set explicitly)
    counter = 'naquestionset'

    _ntiid_suffix = 'naq.set.'
    _ntiid_type = NTIID_TYPE
    _ntiid_title_attr_name = 'ref'  # Use our counter to generate IDs if no ID is given
    _ntiid_allow_missing_title = True
    _ntiid_cache_map_name = '_naquestionset_ntiid_map'

    #: From IEmbeddedContainer
    mimeType = QUESTION_SET_MIME_TYPE

    def create_questionset(self, questions, title, **kwargs):
        result = QQuestionSet(questions=questions, title=title)
        return result

    def validate_questionset(self, questionset):
        errors = schema.getValidationErrors(IQuestionSet, questionset)
        if errors:  # pragma: no cover
            raise errors[0][1]
        return questionset

    @cachedIn('_v_assessment_object')
    def assessment_object(self):
        questions = [qref.idref['label'].assessment_object()
                     for qref in self.getElementsByTagName('naquestionref')]
        questions = PersistentList(questions)

        # Note that we may not actually have a renderer, depending on when
        # in our lifetime this is called (the renderer object mixin is deprecated
        # anyway)
        # If the title is ours, we're guaranteed it's a string. It's only in the
        # weird legacy code path that tries to inherit a title from some arbitrary
        # parent that it may not be a string
        if getattr(self, 'renderer', None) and not isinstance(self.title, string_types):
            title = text_type(u''.join(render_children(getattr(self, 'renderer'),
                                                       self.title)))
        else:
            title = text_type(getattr(self.title, 'source', self.title))

        title = title.strip() or None

        result = self.create_questionset(questions=questions, title=title)
        result.tags = self._asm_tags()  # get tags
        self.validate_questionset(result)  # validate
        result.ntiid = self.ntiid  # copy the id
        return result

    @readproperty
    def question_count(self):
        return text_(str(len(self.getElementsByTagName('naquestionref'))))

    @readproperty
    def title(self):
        """
        Provide an abstraction of the two ways to get a question set's title
        """
        title = self.attributes.get('title') or None
        if title is None:
            # SAJ: This code path is bad and needs to go away
            title_el = self.parentNode
            while not hasattr(title_el, 'title'):
                title_el = title_el.parentNode
            title = title_el.title
        assert title is not None
        return title


class narandomizedquestionset(naquestionset):
    """
    Example::
        \begin{naquestion}[individual=true]
                \label{question}
                ...
        \end{naquestion}

        \begin{narandomizedquestionset}<My Title>
                \label{set}
                \naquestionref{question}
        \end{narandomizedquestionset}
    """

    def create_questionset(self, questions, title, **kwargs):
        result = QRandomizedQuestionSet(questions=questions, title=title)
        return result

    def validate_questionset(self, questionset):
        errors = schema.getValidationErrors(IRandomizedQuestionSet, 
											questionset)
        if errors:  # pragma: no cover
            raise errors[0][1]
        return questionset


class naqindexranges(Base.List):
    pass


class naqindexrange(Base.List.item):

    args = 'start:int end:int draw:int'

    def digest(self, tokens):
        res = super(naqindexrange, self).digest(tokens)
        start = self.attributes.get('start')
        end = self.attributes.get('end')
        assert start >= 0 and end >= 0 and start <= end

        draw = self.attributes.get('draw', 1)
        assert draw <= (end - start + 1)

        return res

    def _after_render(self, rendered):
        self._asm_local_content = rendered


class naquestionbank(naquestionset):
    """
    Example::

        \begin{naquestion}[individual=true]
                \label{question}
                ...
        \end{naquestion}

        \begin{naquestionbank}[draw=2]<My Title>
                \label{set}
                \naquestionref{question}
        \end{naquestionbank}
    """

    @readproperty
    def draw(self):
        options = self.attributes.get('options') or {}
        draw = options.get('draw') or self.attributes.get('draw')
        return int(draw) if draw else None

    @readproperty
    def question_count(self):
        result = self.draw or super(naquestionbank, self).question_count
        return text_(str(result))

    def create_questionset(self, questions, title, **kwargs):
        draw = self.draw or len(questions)
        result = QQuestionBank(questions=questions,
                               title=title,
                               draw=draw)
        # set ranges
        naqindexranges = self.getElementsByTagName('naqindexranges')
        naqindexranges = naqindexranges[0] if naqindexranges else None
        if naqindexranges:
            result.ranges = getattr(naqindexranges, "ranges", None)
        return result

    def validate_questionset(self, questionset):
        errors = schema.getValidationErrors(IQuestionBank, questionset)
        if errors:  # pragma: no cover
            raise errors[0][1]
        questionset.validate()
        return questionset

    def digest(self, tokens):
        res = super(naquestionbank, self).digest(tokens)
        if self.macroMode != Base.Environment.MODE_END:
            questions = self.getElementsByTagName('naquestionref') or ()

            naqindexranges = self.getElementsByTagName('naqindexranges')
            assert not naqindexranges or len(naqindexranges) == 1

            naqindexranges = naqindexranges[0] if naqindexranges else None
            if naqindexranges is not None and questions:
                _indexranges = []
                _max_index = len(questions)
                _ranges = naqindexranges.getElementsByTagName('naqindexrange')
                for _range in _ranges or ():
                    start, end = int(_range.attributes['start']), \
                                 int(_range.attributes['end'])
                    assert start <= end, "invalid range"
                    assert end < _max_index, "index ouside of range"

                    draw = int(_range.attributes.get('draw', 1))
                    assert draw <= (end - start + 1), "Invalid draw in range"
                    _indexranges.append((start, end, draw))

                # get ranges
                _indexranges = [IQuestionIndexRange(x) for x in _indexranges]
                _indexranges.sort()

                draw = self.draw
                assert draw, "no draw attribute was specified"

                naqindexranges.ranges = _indexranges
        return res

    @cachedIn('_v_assessment_object')
    def assessment_object(self):
        result = super(naquestionbank, self).assessment_object()
        return result


class naquestionsetref(naassesmentref):
    """
    A reference to the label of a question set.
    """

    assesment = alias('questionset')

    @readproperty
    def questionset(self):
        return self.idref['label']


class narandomizedquestionsetref(naquestionsetref):
    """
    A reference to the label of a question set.
    """

    randomizedquestionset = naquestionsetref.questionset


class naquestionbankref(naquestionsetref):
    """
    A reference to the label of a question bank.
    """

    questionbank = naquestionsetref.questionset
