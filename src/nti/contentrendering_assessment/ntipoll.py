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

from paste.deploy.converters import asbool

from plasTeX import Base

from plasTeX.Renderers import render_children

from nti.assessment.interfaces import IQPoll
from nti.assessment.interfaces import IQSurvey

from nti.assessment.interfaces import NTIID_TYPE
from nti.assessment.interfaces import POLL_MIME_TYPE
from nti.assessment.interfaces import SURVEY_MIME_TYPE
from nti.assessment.interfaces import DISCLOSURE_TERMINATION

from nti.assessment.survey import QPoll
from nti.assessment.survey import QSurvey

from nti.contentprocessing._compat import text_

from nti.contentrendering.interfaces import IEmbeddedContainer

from nti.contentrendering.plastexids import NTIIDMixin

from nti.contentrendering_assessment.ntibase import naassesmentref
from nti.contentrendering_assessment.ntibase import _AbstractNAQTags
from nti.contentrendering_assessment.ntibase import _LocalContentMixin

from nti.contentrendering_assessment.utils import parse_assessment_datetime

from nti.property.property import alias


class napollname(Base.Command):
    unicode = u''


class nasurveyname(Base.Command):
    unicode = u''


class nainquiry(_AbstractNAQTags, NTIIDMixin):

    @property
    def _local_tzname(self):
        document = self.ownerDocument
        userdata = getattr(document, 'userdata', None) or {}
        return userdata.get('document_timezone_name')

    @property
    def options(self):
        return self.attributes.get('options') or {}

    def not_before(self, options):
        result = parse_assessment_datetime('not_before_date', options,
                                           'T00:00', self._local_tzname)
        return result

    def not_after(self, options):
        result = parse_assessment_datetime('not_after_date', options,
                                           'T23:59', self._local_tzname)
        return result

    def disclosure(self, options):
        result = options.get('disclosure') or DISCLOSURE_TERMINATION
        return result

    def is_non_public(self, options):
        result = False
        if 'public' in options and not asbool(options['public']):
            result = True
        return result


class napoll(_LocalContentMixin, Base.Environment, nainquiry):

    args = "[options:dict:str]"

    blockType = True

    counter = 'napoll'

    forcePars = False

    _ntiid_type = NTIID_TYPE

    _ntiid_suffix = 'naq.'
    _ntiid_title_attr_name = 'ref'
    _ntiid_allow_missing_title = True
    _ntiid_cache_map_name = '_napoll_ntiid_map'

    mimeType = POLL_MIME_TYPE

    def invoke(self, tex):
        res = super(napoll, self).invoke(tex)
        return res

    @property
    def _ntiid_get_local_part(self):
        result = self.attributes.get("pollnum")
        if not result:
            result = super(napoll, self)._ntiid_get_local_part
        return result

    def _asm_videos(self):
        return u''.join(())

    def _asm_poll_parts(self):

        def _filter(x):
            result = hasattr(x, 'tagName') and x.tagName.startswith('naq') \
                 and x.tagName.endswith('part') and hasattr(x, 'assessment_object')
            if result:
                x.gradable = False  # polls are not gradable
            return result

        generator = (x for x in self.allChildNodes if _filter(x))
        return [x.assessment_object() for x in generator]

    def _createPoll(self, disclosure=None, not_before=None,
                    not_after=None, is_non_public=False):
        result = QPoll(content=self._asm_local_content,
                       parts=self._asm_poll_parts(),
                       is_non_public=is_non_public,
                       tags=self._asm_tags(),
                       disclosure=disclosure or DISCLOSURE_TERMINATION,
                       available_for_submission_beginning=not_before,
                       available_for_submission_ending=not_after)
        return result

    @cachedIn('_v_assessment_object')
    def assessment_object(self):
        # parse options
        options = self.options
        disclosure = self.disclosure(options)
        not_after = self.not_after(options)
        not_before = self.not_before(options)
        is_non_public = self.is_non_public(options)
        # create poll
        result = self._createPoll(disclosure, not_before, 
								  not_after, is_non_public)
        errors = schema.getValidationErrors(IQPoll, result)
        if errors:  # pragma: no cover
            raise errors[0][1]
        result.ntiid = self.ntiid  # copy the id
        return result


class napollref(naassesmentref):

    assesment = alias('poll')

    @readproperty
    def poll(self):
        return self.idref['label']


@interface.implementer(IEmbeddedContainer)
class nasurvey(Base.List, nainquiry):
    """
    Surveys are a list of questions that should be submitted
    together. For authoring, polls are included in a survey
    by reference, and a survey can be composed of any
    other labeled poll found within the same processing unit.

    Example::
            \begin{napoll}
                    \label{poll}
                    ...
            \end{napoll}

            \begin{nasurvey}<My Title>
                    \label{survey}
                    \napollref{poll}
            \end{nasurvey}
    """

    args = "[options:dict:str] <title:str:source>"

    # Only classes with counters can be labeled, and \label sets the
    # id property, which in turn is used as part of the
    # NTIID (when no NTIID is set explicitly)
    counter = 'nasurvey'

    _ntiid_type = NTIID_TYPE
    _ntiid_suffix = 'naq.survey.'
    _ntiid_title_attr_name = 'ref'
    _ntiid_allow_missing_title = True
    _ntiid_cache_map_name = '_nasurvey_ntiid_map'

    mimeType = SURVEY_MIME_TYPE

    def create_survey(self, questions, title, disclosure=None, not_before=None,
                      not_after=None, is_non_public=False, **kwargs):
        result = QSurvey(questions=questions, title=title,
                         is_non_public=is_non_public,
                         tags=self._asm_tags(),
                         disclosure=disclosure or DISCLOSURE_TERMINATION,
                         available_for_submission_beginning=not_before,
                         available_for_submission_ending=not_after)
        return result

    def validate_survey(self, survey):
        errors = schema.getValidationErrors(IQSurvey, survey)
        if errors:  # pragma: no cover
            raise errors[0][1]
        return survey

    @cachedIn('_v_assessment_object')
    def assessment_object(self):
        # parse options
        options = self.options
        disclosure = self.disclosure(options)
        not_after = self.not_after(options)
        not_before = self.not_before(options)
        is_non_public = self.is_non_public(options)

        # parse poll questions
        questions = [qref.idref['label'].assessment_object()
                     for qref in self.getElementsByTagName('napollref')]
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

        result = self.create_survey(questions=questions,
                                    title=title,
                                    disclosure=disclosure,
                                    not_before=not_before,
                                    not_after=not_after,
                                    is_non_public=is_non_public)
        self.validate_survey(result)
        result.ntiid = self.ntiid  # copy the id
        return result

    @readproperty
    def question_count(self):
        return text_(len(self.getElementsByTagName('napollref')))

    @readproperty
    def title(self):
        """
        Provide an abstraction of the two ways to get a question set's title
        """
        title = self.attributes.get('title') or None
        if title is None:
            title_el = self.parentNode
            while not hasattr(title_el, 'title'):
                title_el = title_el.parentNode
            title = title_el.title
        assert title is not None
        return title


class nasurveyref(naassesmentref):
    """
    A reference to the label of a survey.
    """
    
    assesment = alias('survey')

    @readproperty
    def survey(self):
        return self.idref['label']
