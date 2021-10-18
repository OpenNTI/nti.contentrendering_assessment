#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import has_entry
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_entries
from hamcrest import contains_string
from hamcrest import is_not as does_not

import io
import os
import time
import simplejson as json

from datetime import datetime
from datetime import timedelta

from zope import component
from zope import interface

from zope.traversing.api import traverse

from nti.assessment.interfaces import DEFAULT_MAX_SIZE_BYTES

from nti.contentrendering import nti_render
from nti.contentrendering import transforms

from nti.contentrendering.interfaces import IRenderedBook

from nti.contentrendering.resources import ResourceRenderer

from nti.contentrendering.resources.ResourceDB import ResourceDB

from nti.contentrendering_assessment.interfaces import IAssessmentExtractor

from nti.contentrendering.tests import RenderContext

from nti.contentrendering_assessment.tests import _simpleLatexDocument
from nti.contentrendering_assessment.tests import AssessmentRenderingTestCase


@interface.implementer(IRenderedBook)
class _MockRenderedBook(object):
    document = None
    contentLocation = None


def remove_keys(data, *keys):
    if isinstance(data, dict):
        for x, y in tuple(data.items()): # mutating
            if x in keys:
                data.pop(x, None)
            else:
                remove_keys(y, *keys)
    elif isinstance(data, list):
        for x in data: # mutating
            remove_keys(x, *keys)


class TestRenderables(AssessmentRenderingTestCase):

    def _do_test_render(self, label, ntiid, filename='index.html', units='',
                        units_html=None, input_encoding=None):

        example = r"""
        \begin{naquestion}[individual=true]%s
            Arbitrary content goes here.
            \begin{naqsymmathpart}
            Arbitrary content goes here.
            \begin{naqsolutions}
                \naqsolution %s Some solution
            \end{naqsolutions}
            \end{naqsymmathpart}
        \end{naquestion}
        """ % (label,units)

        if units: # Units are rendered only in the solution, which is not rendered in the question anymore
            example = r"""
            \begin{naqsolutions}
                \naqsolution %s Some solution
            \end{naqsolutions}
            """ % (units,)

        with RenderContext(_simpleLatexDocument( (example,) ), output_encoding='utf-8',
                           input_encoding=input_encoding) as ctx:
            dom  = ctx.dom
            dom.getElementsByTagName( 'document' )[0].filenameoverride = 'index'
            render = ResourceRenderer.createResourceRenderer('XHTML', None)
            render.importDirectory( os.path.join( os.path.dirname(__file__), '..' ) )
            render.render( dom )

            with io.open(os.path.join(ctx.docdir, filename), 'rU', encoding='utf-8' ) as f:
                index = f.read()

            if not units:
                content = """<object type="application/vnd.nextthought.naquestion" data-ntiid="%(ntiid)s" data="%(ntiid)s""" % { 'ntiid': ntiid }
                content2 = """<param name="ntiid" value="%(ntiid)s" """ % { 'ntiid': ntiid }

                assert_that( index, contains_string( content ) )
                assert_that( index, contains_string( content2 ) )

            if units:
                units_html = units_html or units[1:-1]
                assert_that( index, contains_string( 'data-nti-units="' + units_html + '"' ) )
            else:
                assert_that( index, does_not( contains_string( 'data-nti-units' ) ) )

    def test_render_id(self):
        self._do_test_render( r'\label{testquestion}', 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.testquestion')

    def test_render_counter(self):
        self._do_test_render( '', 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.1' )

    def test_render_units( self ):
        self._do_test_render( '', 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.1',
                              units='<unit1,unit2>')

    def test_render_units_with_percent( self ):
        self._do_test_render( '', 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.1',
                              units=r'<unit1,\%>',
                              units_html="unit1,%")

    def test_render_units_with_unicode( self ):
        self._do_test_render('', 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.1',
                             units=r'<m²>',
                             input_encoding='utf-8' )# m squared, u'\xb2'

    def test_render_units_with_latex_math_not_allowed( self ):
        with self.assertRaises(ValueError):
            self._do_test_render( '', 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.1', units=r'<$m^2$>')

    def test_assessment_index(self):
        example = r"""
            \chapter{Chapter One}

            We have a paragraph.

            \section{Section One}

            \begin{naquestion}[individual=true]\label{testquestion}
                Arbitrary content goes here.
                \begin{naqsymmathpart}
                Arbitrary content goes here.
                \begin{naqsolutions}
                    \naqsolution<unit1,unit2> Some solution
                \end{naqsolutions}
                \begin{naqhints}
                    \naqhint Some hint
                \end{naqhints}
                \end{naqsymmathpart}
            \end{naquestion}

            \begin{naquestionset}\label{testset}
                \naquestionref{testquestion}
            \end{naquestionset}
            """

        with RenderContext(_simpleLatexDocument( (example,) )) as ctx:
            dom  = ctx.dom
            dom.getElementsByTagName( 'document' )[0].filenameoverride = 'index'
            render = ResourceRenderer.createResourceRenderer( 'XHTML', None )
            render.importDirectory( os.path.join( os.path.dirname(__file__), '..' ) )
            render.render( dom )

            rendered_book = _MockRenderedBook()
            rendered_book.document = dom
            rendered_book.contentLocation = ctx.docdir

            extractor = component.getAdapter(rendered_book, IAssessmentExtractor)
            extractor.transform( rendered_book )

            jsons = open(os.path.join( ctx.docdir, 'assessment_index.json' ), 'rU' ).read()
            obj = json.loads( jsons )

            exp_value = {'Items': {'tag:nextthought.com,2011-10:testing-HTML-temp.0': {'AssessmentItems': {},
                   'Items': {'tag:nextthought.com,2011-10:testing-HTML-temp.chapter_one': {'AssessmentItems': {},
                     'Items': {'tag:nextthought.com,2011-10:testing-HTML-temp.section_one': {'AssessmentItems': {'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.set.testset': {'Class': 'QuestionSet',
                        'title': 'Section One', # FIXME: We're inheriting this all the way up, which makes no sense
                        'MimeType': 'application/vnd.nextthought.naquestionset',
                         'NTIID': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.set.testset',
                         'ntiid': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.set.testset',
                         'questions': [{'Class': 'Question',
                           'MimeType': 'application/vnd.nextthought.naquestion',
                           'NTIID': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.testquestion',
                           'ntiid': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.testquestion',
                           'content': '<a name="testquestion"></a> Arbitrary content goes here.',
                           'parts': [{'Class': 'SymbolicMathPart',
                             'MimeType': 'application/vnd.nextthought.assessment.symbolicmathpart',
                             "NTIID": "tag:nextthought.com,2011-10:testing-NAQPart-temp.naq.testquestion.0",
                             'allowed_units': ['unit1', 'unit2', ''],
                             'content': 'Arbitrary content goes here.',
                             'explanation': '',
                             'hints': [{'Class': 'HTMLHint',
                               'MimeType': 'application/vnd.nextthought.assessment.htmlhint',
                               'value': 'Some hint'}], # XXX We used to render hints but we no longer are. Why?
                             'randomized': False,
                             'solutions': [{'Class': 'LatexSymbolicMathSolution',
                               'MimeType': 'application/vnd.nextthought.assessment.latexsymbolicmathsolution',
                               'value': 'Some solution',
                               'weight': 1.0,
                               'allowed_units': ['unit1','unit2','']}],
                             'weight': 1.0,}]}]},
                        'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.testquestion': {'Class': 'Question',
                         'MimeType': 'application/vnd.nextthought.naquestion',
                         'NTIID': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.testquestion',
                         'ntiid': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.testquestion',
                         'content': '<a name="testquestion"></a> Arbitrary content goes here.',
                         'parts': [{'Class': 'SymbolicMathPart',
                           'MimeType': 'application/vnd.nextthought.assessment.symbolicmathpart',
                           "NTIID": "tag:nextthought.com,2011-10:testing-NAQPart-temp.naq.testquestion.0",
                           'allowed_units': ['unit1', 'unit2', ''],
                           'content': 'Arbitrary content goes here.',
                           'explanation': '',
                           'hints': [{'Class': 'HTMLHint',
                             'MimeType': 'application/vnd.nextthought.assessment.htmlhint',
                             'value': 'Some hint'}],
                           'randomized': False,
                           'solutions': [{'Class': 'LatexSymbolicMathSolution',
                             'MimeType': 'application/vnd.nextthought.assessment.latexsymbolicmathsolution',
                             'value': 'Some solution',
                             'weight': 1.0,
                             'allowed_units': ['unit1','unit2','']}],
                            'weight': 1.0,}]}},
                       'NTIID': 'tag:nextthought.com,2011-10:testing-HTML-temp.section_one',
                       'filename': 'tag_nextthought_com_2011-10_testing-HTML-temp_section_one.html',
                       'href': 'tag_nextthought_com_2011-10_testing-HTML-temp_section_one.html'}},
                     'NTIID': 'tag:nextthought.com,2011-10:testing-HTML-temp.chapter_one',
                     'filename': 'tag_nextthought_com_2011-10_testing-HTML-temp_chapter_one.html',
                     'href': 'tag_nextthought_com_2011-10_testing-HTML-temp_chapter_one.html'}},
                   'NTIID': 'tag:nextthought.com,2011-10:testing-HTML-temp.0',
                   'filename': 'index.html',
                   'href': 'index.html'}},
                 'href': 'index.html'}
            remove_keys(obj, 'ID', 'Signatures', 'CreatedTime', 'Last Modified',
                        'version', 'tags', 'publishLastModified')
            assert_that( obj, is_( exp_value ) )

    def test_assessment_index_with_file_part(self):

        example = r"""
        \chapter{Chapter One}

        We have a paragraph.

        \section{Section One}

        \begin{naquestion}[individual=true]\label{testquestion}
            Arbitrary content goes here.
            \begin{naqfilepart}(application/pdf)
            Arbitrary content goes here.
            \end{naqfilepart}
        \end{naquestion}

        """

        with RenderContext(_simpleLatexDocument( (example,) )) as ctx:
            dom  = ctx.dom
            dom.getElementsByTagName( 'document' )[0].filenameoverride = 'index'
            render = ResourceRenderer.createResourceRenderer( 'XHTML', None )
            render.importDirectory( os.path.join( os.path.dirname(__file__), '..' ) )
            render.render( dom )

            rendered_book = _MockRenderedBook()
            rendered_book.document = dom
            rendered_book.contentLocation = ctx.docdir

            extractor = component.getAdapter(rendered_book, IAssessmentExtractor)
            extractor.transform( rendered_book )

            jsons = open(os.path.join( ctx.docdir, 'assessment_index.json' ), 'rU' ).read()
            obj = json.loads( jsons )

            question = {'Class': 'Question',
                        "ID": "tag:nextthought.com,2011-10:testing-NAQ-temp.naq.testquestion",
                        'MimeType': 'application/vnd.nextthought.naquestion',
                        'NTIID': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.testquestion',
                        'ntiid': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.testquestion',
                        'content': '<a name="testquestion"></a> Arbitrary content goes here.',
                        'parts': [{'Class': 'FilePart',
                                   'MimeType': 'application/vnd.nextthought.assessment.filepart',
                                   "NTIID": "tag:nextthought.com,2011-10:testing-NAQPart-temp.naq.testquestion.0",
                                   'allowed_extensions': [],
                                   'allowed_mime_types': ['application/pdf'],
                                   'content': 'Arbitrary content goes here.',
                                   'explanation': u'',
                                   'hints': [],
                                   'max_file_size': DEFAULT_MAX_SIZE_BYTES,
                                   'randomized': False,
                                   'solutions': [],
                                   'weight': 1.0,}]}

            exp_value = {'Items': {'tag:nextthought.com,2011-10:testing-HTML-temp.0':
                                   {'AssessmentItems': {},
                                    'Items': {'tag:nextthought.com,2011-10:testing-HTML-temp.chapter_one':
                                              {'AssessmentItems': {},
                                               'Items': {'tag:nextthought.com,2011-10:testing-HTML-temp.section_one':
                                                         {'AssessmentItems': {'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.testquestion': question},
                                                          'NTIID': 'tag:nextthought.com,2011-10:testing-HTML-temp.section_one',
                                                          'filename': 'tag_nextthought_com_2011-10_testing-HTML-temp_section_one.html',
                                                          'href': 'tag_nextthought_com_2011-10_testing-HTML-temp_section_one.html'}
                                                          },
                                                          'NTIID': 'tag:nextthought.com,2011-10:testing-HTML-temp.chapter_one',
                                                          'filename': 'tag_nextthought_com_2011-10_testing-HTML-temp_chapter_one.html',
                                                          'href': 'tag_nextthought_com_2011-10_testing-HTML-temp_chapter_one.html'}
                                                          },
                                          'NTIID': 'tag:nextthought.com,2011-10:testing-HTML-temp.0',
                                          'filename': 'index.html',
                                          'href': 'index.html'}
                                          },
                            'href': 'index.html'}
            remove_keys(obj, 'CreatedTime', 'Last Modified', 'version',
                        'tags', 'publishLastModified')
            assert_that(obj, is_(exp_value))

    def test_assessment_index_with_assignment(self):

        example = r"""
        \chapter{Chapter One}

        We have a paragraph.

        \section{Section One}

        \begin{naquestion}[individual=true]\label{testquestion}
            Arbitrary content goes here.
            \begin{naqfilepart}(application/pdf)
            Arbitrary content goes here.
            \end{naqfilepart}
        \end{naquestion}

        \begin{naquestionset}<Set Title With \% and \$>
        \label{set}
        \naquestionref{testquestion}
        \end{naquestionset}


        \begin{naassignment}[not_before_date=2014-01-13,maximum_time_allowed=60]<Main Title>
        \label{assignment}
        Assignment content.
        \begin{naassignmentpart}[auto_grade=true]<Part Title>{set}
            Some content.
        \end{naassignmentpart}
        \end{naassignment}

        """

        with RenderContext(_simpleLatexDocument( (example,) )) as ctx:
            dom  = ctx.dom
            dom.getElementsByTagName( 'document' )[0].filenameoverride = 'index'
            render = ResourceRenderer.createResourceRenderer( 'XHTML', None )
            render.importDirectory( os.path.join( os.path.dirname(__file__), '..' ) )
            render.render( dom )

            rendered_book = _MockRenderedBook()
            rendered_book.document = dom
            rendered_book.contentLocation = ctx.docdir

            extractor = component.getAdapter(rendered_book, IAssessmentExtractor)
            extractor.transform( rendered_book )

            jsons = open(os.path.join( ctx.docdir, 'assessment_index.json' ), 'rU' ).read()
            jsons = jsons.decode('utf-8')
            obj = json.loads( jsons )

            question = {'Class': 'Question',
                        'MimeType': 'application/vnd.nextthought.naquestion',
                        'NTIID': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.testquestion',
                        'ntiid': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.testquestion',
                        'content': '<a name="testquestion"></a> Arbitrary content goes here.',
                        'parts': [{'Class': 'FilePart',
                                   'MimeType': 'application/vnd.nextthought.assessment.filepart',
                                   "NTIID": "tag:nextthought.com,2011-10:testing-NAQPart-temp.naq.testquestion.0",
                                   'allowed_extensions': [],
                                   'allowed_mime_types': ['application/pdf'],
                                   'content': 'Arbitrary content goes here.',
                                   'explanation': u'',
                                   'hints': [],
                                   'max_file_size': DEFAULT_MAX_SIZE_BYTES,
                                   'randomized': False,
                                   'solutions': [],
                                   'weight': 1.0}]}

            beg_date = datetime(2014, 01, 13, 0, 0)
            beg_date = beg_date + timedelta(seconds=time.timezone)
            beg_date = beg_date.isoformat() + 'Z'
            exp_value = {'Items':
                         {'tag:nextthought.com,2011-10:testing-HTML-temp.0':
                          {'AssessmentItems': {},
                           'Items': {'tag:nextthought.com,2011-10:testing-HTML-temp.chapter_one':
                                     {'AssessmentItems': {},
                                      'Items': {'tag:nextthought.com,2011-10:testing-HTML-temp.section_one':
                                                {'AssessmentItems': {'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.asg.assignment':
                                                                     {'Class': 'TimedAssignment',
                                                                      'is_non_public': True,
                                                                      'category_name': 'default',
                                                                      'CategoryName': "default",
                                                                      "Creator": "zope.security.management.system_user",
                                                                      # XXX: JAM: Obviously this is wrong. Hopefully nobody uses it.
                                                                      'content': u'\\label{assignment} Assignment content. \\begin{naassignmentpart}[auto_grade=true]<Part Title>{set} Some content. \\end{naassignmentpart}',
                                                                      'maximum_time_allowed': 60,
                                                                      'no_submit': False,
                                                                      'NoSubmit': False,
                                                                      'MimeType': 'application/vnd.nextthought.assessment.timedassignment',
                                                                      'NTIID': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.asg.assignment',
                                                                      'ntiid': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.asg.assignment',
                                                                      'available_for_submission_beginning': beg_date,
                                                                      'available_for_submission_ending': None,
                                                                      'parts': [{'Class': 'AssignmentPart',
                                                                                 'MimeType': 'application/vnd.nextthought.assessment.assignmentpart',
                                                                                 "NTIID": "tag:nextthought.com,2011-10:testing-NAQPart-temp.naq.asg.assignment.0",
                                                                                 'auto_grade': True,
                                                                                 'content': 'Some content.',
                                                                                 'question_set': {'Class': 'QuestionSet',
                                                                                                  'title': 'Set Title With % and $',
                                                                                                  'MimeType': 'application/vnd.nextthought.naquestionset',
                                                                                                  'NTIID': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.set.set',
                                                                                                  'ntiid': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.set.set',
                                                                                                  'questions': [question]},
                                                                                 'title': 'Part Title'}],
                                                                      'title': 'Main Title'},
                                                                     'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.set.set': {'Class': 'QuestionSet',
                                                                                                                                  'title': 'Set Title With % and $',
                                                                                                                                  'MimeType': 'application/vnd.nextthought.naquestionset',
                                                                                                                                  'NTIID': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.set.set',
                                                                                                                                  'ntiid': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.set.set',
                                                                                                                                  'questions': [question]},
                                                                     'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.testquestion': question},
                                                 'NTIID': 'tag:nextthought.com,2011-10:testing-HTML-temp.section_one',
                                                 'filename': 'tag_nextthought_com_2011-10_testing-HTML-temp_section_one.html',
                                                 'href': 'tag_nextthought_com_2011-10_testing-HTML-temp_section_one.html'}},
                                      'NTIID': 'tag:nextthought.com,2011-10:testing-HTML-temp.chapter_one',
                                      'filename': 'tag_nextthought_com_2011-10_testing-HTML-temp_chapter_one.html',
                                      'href': 'tag_nextthought_com_2011-10_testing-HTML-temp_chapter_one.html'}},
                           'NTIID': 'tag:nextthought.com,2011-10:testing-HTML-temp.0',
                           'filename': 'index.html',
                           'href': 'index.html'}},
                         'href': 'index.html'}

            remove_keys(obj, 'ID', 'CreatedTime', 'Last Modified',
                        'publishBeginning', 'publishEnding', 'version', 'tags',
                        'publishLastModified')
            obj = json.dumps(obj, indent=4, sort_keys=True)
            exp_value = json.dumps(exp_value, indent=4, sort_keys=True)
            assert_that(obj, is_(exp_value))

    def test_cs_encapsulation_brianna(self):
        example = r"""
                \section{Turingscraft: Encapsulation (10 points)}

                Complete the Turingscraft exercises on encapsulation (first exercise, 20725)
                \href{https://codelab3.turingscraft.com/codelab/jsp/codelink/codelink.jsp?sac=OKLA-16038-VXTF-22&exssn=00000-20725}{here}.

                \begin{naassignment}[category=no_submit,not_after_date=2014-12-01,public=true]<Turingscraft: Encapsulation (10 points)>
                        \label{assignment:Turingscraft_C__Encapsulation}
                \end{naassignment}
                """
        text = _simpleLatexDocument( (example,))

        # Our default rendering process with default output encodings
        with RenderContext(text) as ctx:
            transforms.performTransforms(ctx.dom)
            rdb = ResourceDB( ctx.dom )
            rdb.generateResourceSets()

            jobname = ctx.dom.userdata['jobname']
            nti_render.process_document(ctx.dom, jobname, out_format='xhtml')

            fname = os.path.join(ctx.docdir, 'tag_nextthought_com_2011-10_testing-HTML-temp_0.html')
            with open(fname, 'r') as f:
                contents = f.read()

            link = '<link href="tag:nextthought.com,2011-10:testing-HTML-temp.turingscraft:_encapsulation_(10_points)" rel="next" title="Turingscraft: Encapsulation (10 points)" />'
            assert_that( contents, contains_string(link) )

            # ....was 'tag_nextthought_com_2011-10_testing-HTML-temp_assignment_Turingscraft_C__Encapsulation.html'
            filename = u'tag_nextthought_com_2011-10_testing-HTML-temp_turingscraft__encapsulation__10_points_.html'
            fname = os.path.join(ctx.docdir, filename)
            with open(fname, 'r') as f:
                contents = f.read()

            assert_that( contents,
                         contains_string('<span class="naassignment hidden"></span>') )

            assert_that( contents,
                         contains_string('<div class="chapter title">Turingscraft: Encapsulation (10 points)</div>') )

            assert_that( contents,
                         does_not(contains_string('V </p> </div>') ))

    def test_fill_in_the_blank_short_answer_part(self):
        example = r"""
                \begin{naquestion}
                Arbitrary prefix content goes here.
                \begin{naqfillintheblankshortanswerpart}
                    Arbitrary content for this part goes here. \naqblankfield{001}[2]
                    \begin{naqregexes}
                        \naqregex{001}{\\s*\\\$?\\s?945.20} \$945.20
                    \end{naqregexes}
                    \begin{naqsolexplanation}
                        Arbitrary content explaining how the correct solution is arrived at.
                    \end{naqsolexplanation}
                \end{naqfillintheblankshortanswerpart}
            \end{naquestion}
            """

        with RenderContext(_simpleLatexDocument( (example,) )) as ctx:
            dom  = ctx.dom
            dom.getElementsByTagName( 'document' )[0].filenameoverride = 'index'
            render = ResourceRenderer.createResourceRenderer( 'XHTML', None )
            dom.renderer = render
            render.importDirectory( os.path.join( os.path.dirname(__file__), '..' ) )
            render.render( dom )

            rendered_book = _MockRenderedBook()
            rendered_book.document = dom
            rendered_book.contentLocation = ctx.docdir

            extractor = component.getAdapter(rendered_book, IAssessmentExtractor)
            extractor.transform( rendered_book )

            jsons = open(os.path.join(ctx.docdir, 'assessment_index.json' ), 'rU' ).read()
            jsons = jsons.decode('utf-8')
            obj = json.loads( jsons )

            parts_key = 'Items/tag:nextthought.com,2011-10:testing-HTML-temp.0/AssessmentItems/tag:nextthought.com,2011-10:testing-NAQ-temp.naq.1/parts'
            parts = traverse(obj, parts_key, default=None)
            assert_that(parts, is_not(none()))
            assert_that(parts, has_length(1))

            solutions = traverse(parts[0], 'solutions', default=None)
            assert_that(solutions, is_not(none()))
            assert_that(solutions, has_length(1))

            assert_that(solutions[0], has_entry('value',
                                                has_entry('001', has_entries(u'pattern', u'\\s*\\$?\\s?945.20',
                                                                             u'solution', u'$945.20'))))

    def test_question_bank(self):
        path = os.path.join(os.path.dirname(__file__), 'questionbank_ranges.tex')
        with open(path, "r") as f:
            source = f.read()

        with RenderContext(_simpleLatexDocument( (source,) )) as ctx:
            dom  = ctx.dom
            dom.getElementsByTagName( 'document' )[0].filenameoverride = 'index'
            render = ResourceRenderer.createResourceRenderer( 'XHTML', None )
            dom.renderer = render
            render.importDirectory( os.path.join( os.path.dirname(__file__), '..' ) )
            render.render( dom )

            rendered_book = _MockRenderedBook()
            rendered_book.document = dom
            rendered_book.contentLocation = ctx.docdir

            extractor = component.getAdapter(rendered_book, IAssessmentExtractor)
            extractor.transform( rendered_book )

            jsons = open(os.path.join(ctx.docdir, 'assessment_index.json' ), 'rU' ).read()
            jsons = jsons.decode('utf-8')
            obj = json.loads( jsons )

            key = 'Items/tag:nextthought.com,2011-10:testing-HTML-temp.0/AssessmentItems/tag:nextthought.com,2011-10:testing-NAQ-temp.naq.set.qset:GEOG_Unit4_quiz'
            quiz = traverse(obj, key, default=None)
            assert_that(quiz, has_entry('questions', has_length(9)))
            assert_that(quiz, has_entry('draw', is_(4)))
            assert_that(quiz, has_entry('ranges', has_length(2)))
