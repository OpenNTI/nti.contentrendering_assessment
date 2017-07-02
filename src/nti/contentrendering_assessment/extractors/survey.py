#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import os
import six

from zope import component
from zope import interface

from plasTeX.Renderers import render_children

from nti.contentrendering.interfaces import IRenderedBook

from nti.contentrendering_assessment.interfaces import ILessonSurveyExtractor


@component.adapter(IRenderedBook)
@interface.implementer(ILessonSurveyExtractor)
class _LessonSurveyExtractor(object):

    def __init__(self, book=None):
        pass

    def transform(self, book, savetoc=True, outpath=None):
        outpath = outpath or book.contentLocation
        outpath = os.path.expanduser(outpath)

        dom = book.toc.dom
        topic_map = self._get_topic_map(dom)
        survey_els = book.document.getElementsByTagName('nasurvey')
        if survey_els:
            self._process_surveys(dom, survey_els, topic_map)
        if savetoc and survey_els:
            book.toc.save()

    def _get_topic_map(self, dom):
        result = {}
        for topic_el in dom.getElementsByTagName('topic'):
            ntiid = topic_el.getAttribute('ntiid')
            if ntiid:
                result[ntiid] = topic_el
        return result

    def _parent_finder(self, element, topic_map):
        lesson_el = None
        parent_el = element.parentNode
        while lesson_el is None and parent_el is not None:
            if hasattr(parent_el, 'ntiid') and parent_el.tagName.startswith('course'):
                lesson_el = topic_map.get(parent_el.ntiid)
            parent_el = parent_el.parentNode if lesson_el is None else parent_el
        return parent_el, lesson_el

    def _process_inquiry(self, dom, element, topic_map):
        parent_el, lesson_el = self._parent_finder(element, topic_map)
        if not parent_el or not lesson_el:
            return None
        toc_el = dom.createElement('object')
        toc_el.setAttribute('mimeType', element.mimeType)
        toc_el.setAttribute('target-ntiid', element.ntiid)
        if lesson_el:
            lesson_el.appendChild(toc_el)
            lesson_el.appendChild(dom.createTextNode(u'\n'))
        return toc_el

    def _process_surveys(self, dom, els, topic_map):
        for element in els:
            toc_el = self._process_inquiry(dom, element, topic_map)
            if not toc_el:
                continue
            label = title = element.title
            if not isinstance(title, six.string_types):
                label = u''.join(render_children(element.renderer, title))

            toc_el.setAttribute('label', label)
            toc_el.setAttribute('question-count', element.question_count)

    def _process_polls(self, dom, els, topic_map):
        for element in els:
            self._process_inquiry(dom, element, topic_map,
                                  self._poll_parent_finder)
