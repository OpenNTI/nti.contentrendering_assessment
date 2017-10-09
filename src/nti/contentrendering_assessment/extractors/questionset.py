#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import six

from zope import component
from zope import interface

from plasTeX.Renderers import render_children

from nti.contentrendering.interfaces import IRenderedBook

from nti.contentrendering_assessment.interfaces import ILessonQuestionSetExtractor

logger = __import__('logging').getLogger(__name__)


@component.adapter(IRenderedBook)
@interface.implementer(ILessonQuestionSetExtractor)
class _LessonQuestionSetExtractor(object):

    def __init__(self, book=None):
        pass

    def transform(self, book, savetoc=True, outpath=None):
        outpath = outpath or book.contentLocation
        outpath = os.path.expanduser(outpath)

        found_sets = False
        dom = book.toc.dom
        topic_map = self._get_topic_map(dom)
        assignment_els = book.document.getElementsByTagName('naassignment')
        for tag_name in ('naquestionset', 'naquestionbank', 'narandomizedquestionset'):
            questionset_els = book.document.getElementsByTagName(tag_name)
            if questionset_els:
                found_sets = True
                self._process_questionsets(dom, questionset_els, topic_map)

        if found_sets:
            self._process_assignments(dom, assignment_els, topic_map)
            if savetoc:
                book.toc.save()

    def _get_topic_map(self, dom):
        result = {}
        for topic_el in dom.getElementsByTagName('topic'):
            ntiid = topic_el.getAttribute('ntiid')
            if ntiid:
                result[ntiid] = topic_el
        return result

    def _process_questionsets(self, dom, els, topic_map):
        for el in els:
            if not el.parentNode:
                continue
            # Discover the nearest topic in the toc that is a 'course' node
            lesson_el = None
            parent_el = el.parentNode
            if hasattr(parent_el, 'ntiid') and parent_el.tagName.startswith('course'):
                lesson_el = topic_map.get(parent_el.ntiid)

            while lesson_el is None and parent_el.parentNode is not None:
                parent_el = parent_el.parentNode
                if      hasattr(parent_el, 'ntiid') \
                    and parent_el.tagName.startswith('course'):
                    lesson_el = topic_map.get(parent_el.ntiid)

            # SAJ: Hack to prevent question set sections from appearing on
            # old style course overviews
            title_el = el.parentNode
            while (not hasattr(title_el, 'title')):
                title_el = title_el.parentNode

            # If the title_el is a topic in the ToC of a course, suppress it.
            if      dom.childNodes[0].getAttribute('isCourse') == 'true' \
                and title_el.ntiid in topic_map.keys():
                topic_map[title_el.ntiid].setAttribute('suppressed', 'true')

            title = el.title
            if not isinstance(title, six.string_types):
                label = u''.join(render_children(el.renderer, el.title))
            else:
                label = title

            toc_el = dom.createElement('object')
            toc_el.setAttribute('label', label)
            toc_el.setAttribute('mimeType', el.mimeType)
            toc_el.setAttribute('target-ntiid', el.ntiid)
            toc_el.setAttribute('question-count', el.question_count)
            if lesson_el:
                lesson_el.appendChild(toc_el)
                lesson_el.appendChild(dom.createTextNode(u'\n'))

    # SAJ: This method is a HACK to mark the parent topic of an assignment as
    # 'suppressed'. In practice, this is only needed for 'no_submit' assignments
    # since they have no associated question set to otherwise trigger the marking.
    # This should move into its  own extractor, but for now it is here.
    def _process_assignments(self, dom, els, topic_map):
        for el in els:
            if not el.parentNode:
                continue

            __traceback_info__ = type(el), el

            category = el.attributes.get('options', {}).get('category')
            if category != 'no_submit':
                continue

            # Discover the nearest topic in the toc that is a 'course' node
            lesson_el = None
            parent_el = el.parentNode
            if hasattr(parent_el, 'ntiid') and parent_el.tagName.startswith('course'):
                lesson_el = topic_map.get(parent_el.ntiid)

            while lesson_el is None and parent_el.parentNode is not None:
                parent_el = parent_el.parentNode
                if     hasattr(parent_el, 'ntiid') \
                    and parent_el.tagName.startswith('course'):
                    lesson_el = topic_map.get(parent_el.ntiid)

            # SAJ: Hack to prevent no_submit assignment sections from appearing on
            # old style course overviews
            title_el = el.parentNode
            while not hasattr(title_el, 'title'):
                title_el = title_el.parentNode

            # If the title_el is a topic in the ToC of a course, suppress it.
            if      dom.childNodes[0].getAttribute('isCourse') == u'true' \
                and title_el.ntiid in topic_map.keys():
                topic_map[title_el.ntiid].setAttribute('suppressed', 'true')

            mimeType = 'application/vnd.nextthought.nanosubmitassignment'

            toc_el = dom.createElement('object')
            toc_el.setAttribute('label', el.title)
            toc_el.setAttribute('mimeType', mimeType)
            toc_el.setAttribute('target-ntiid', el.ntiid)
            if lesson_el:
                lesson_el.appendChild(toc_el)
                lesson_el.appendChild(dom.createTextNode(u'\n'))
