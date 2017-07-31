#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import schema
from zope import interface

from zope.cachedescriptors.method import cachedIn

from zope.cachedescriptors.property import readproperty

from plasTeX import Base

from paste.deploy.converters import asbool

from nti.assessment.assignment import QAssignment
from nti.assessment.assignment import QAssignmentPart
from nti.assessment.assignment import QTimedAssignment

from nti.assessment.interfaces import NTIID_TYPE
from nti.assessment.interfaces import IQAssignment

from nti.contentrendering import plastexids

from nti.contentrendering.interfaces import IEmbeddedContainer

from nti.contentrendering_assessment.ntibase import naassesment
from nti.contentrendering_assessment.ntibase import naassesmentref
from nti.contentrendering_assessment.ntibase import _AbstractNAQTags
from nti.contentrendering_assessment.ntibase import _LocalContentMixin

from nti.contentrendering_assessment.utils import parse_assessment_datetime
from nti.contentrendering_assessment.utils import secs_converter as _secs_converter

from nti.property.property import alias


class naassignmentpart(naassesment,
                       _LocalContentMixin,
                       Base.Environment):
    """
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

    def _set_assessment_object(self, value):
        pass

    @cachedIn(naassesment.cached_attribute)
    def assessment_object(self):
        question_set = self.idref['question_set'].assessment_object()
        auto_grade = self.attributes.get('options', {}).get('auto_grade')
        return QAssignmentPart(content=self._asm_local_content,
                               question_set=question_set,
                               auto_grade=asbool(auto_grade),
                               title=self.attributes.get('title'))


class naassignmentname(Base.Command):
    unicode = u''


@interface.implementer(IEmbeddedContainer)
class naassignment(naassesment,
                   _LocalContentMixin,
                   _AbstractNAQTags,
                   Base.Environment,
                   plastexids.NTIIDMixin):
    r"""
    Assignments specify some options such as availability dates,
    some local content, and finish up nesting the parts
    of the assignment as ``naassignmentpart`` elements.

    Example::
        \begin{naassignment}[not_before_date=2014-01-13,category=homework,public=true,no_submit=true]<Homework>
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

    _ntiid_suffix = 'naq.asg.'
    _ntiid_type = NTIID_TYPE
    _ntiid_title_attr_name = 'ref'  # Use our counter to generate IDs if no ID is given
    _ntiid_allow_missing_title = True
    _ntiid_cache_map_name = '_naassignment_ntiid_map'

    #: From IEmbeddedContainer
    mimeType = 'application/vnd.nextthought.assessment.assignment'

    @property
    def _local_tzname(self):
        document = self.ownerDocument
        userdata = getattr(document, 'userdata', None) or {}
        return userdata.get('document_timezone_name')

    @cachedIn(naassesment.cached_attribute)
    def assessment_object(self):
        local_tzname = self._local_tzname
        options = self.attributes.get('options') or ()

        # If they give no timestamp, make it midnight
        not_before = parse_assessment_datetime('not_before_date', options,
                                               'T00:00', local_tzname)

        # For after, if they gave us no time, make it just before
        # midnight. Together, this has the effect of intuitively defining
        # the range of dates as "the first instant of before to the last minute
        # of after"
        not_after = parse_assessment_datetime('not_after_date', options,
                                              'T23:59', local_tzname)

        # Public/ForCredit.
        # It's opt-in for authoring and opt-out for code
        is_non_public = True
        if 'public' in options and asbool(options['public']):
            is_non_public = False

        factory = QAssignment
        maximum_time_allowed = None
        if 'maximum_time_allowed' in options:
            factory = QTimedAssignment
            opt_val = options['maximum_time_allowed']
            maximum_time_allowed = _secs_converter(opt_val)

        parts = [part.assessment_object() for part in
                 self.getElementsByTagName('naassignmentpart')]

        result = factory(content=self._asm_local_content,
                         available_for_submission_beginning=not_before,
                         available_for_submission_ending=not_after,
                         parts=parts,
                         tags=self._asm_tags(),
                         title=self.attributes.get('title'),
                         is_non_public=is_non_public)
        if maximum_time_allowed is not None:
            result.maximum_time_allowed = maximum_time_allowed

        if 'category' in options:
            value = options['category']
            result.category_name = IQAssignment['category_name'].fromUnicode(value)

        if 'no_submit' in options:
            value = options['no_submit']
            result.no_submit = IQAssignment['no_submit'].fromUnicode(value)

        if not result.category_name and result.no_submit:
            result.category_name = u'no_submit'

        errors = schema.getValidationErrors(IQAssignment, result)
        if errors:  # pragma: no cover
            raise errors[0][1]
        result.ntiid = self.ntiid
        return result

    @readproperty
    def containerId(self):
        parentNode = self.parentNode
        while (not hasattr(parentNode, 'filename')) or (parentNode.filename is None):
            parentNode = parentNode.parentNode
        return parentNode.ntiid


class naassignmentref(naassesmentref):
    """
    A reference to the label of a assignment.
    """

    assesment = alias('assignment')

    @readproperty
    def assignment(self):
        return self.idref['label']
