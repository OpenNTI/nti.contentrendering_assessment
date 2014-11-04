#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import assert_that
from hamcrest import contains_string
from hamcrest import is_not as does_not

import io
import os
import anyjson as json

from zope import component
from zope import interface

from nti.contentrendering.interfaces import IRenderedBook
from nti.contentrendering.resources import ResourceRenderer

from nti.assessment.contentrendering.interfaces import IAssessmentExtractor

from nti.contentrendering.tests import RenderContext

from nti.assessment.tests import AssessmentTestCase
from nti.assessment.tests import _simpleLatexDocument

@interface.implementer(IRenderedBook)
class _MockRenderedBook(object):
	document = None
	contentLocation = None

class TestRenderables(AssessmentTestCase):

	def _do_test_render(self, label, ntiid, filename='index.html', units='',
						 units_html=None, input_encoding=None ):

		example = br"""
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

		with RenderContext(_simpleLatexDocument( (example,) ), output_encoding='utf-8', 
						   input_encoding=input_encoding) as ctx:
			dom  = ctx.dom
			dom.getElementsByTagName( 'document' )[0].filenameoverride = 'index'
			render = ResourceRenderer.createResourceRenderer('XHTML', None)
			render.importDirectory( os.path.join( os.path.dirname(__file__), '..' ) )
			render.render( dom )
			# TODO: Actual validation of the rendering


			index = io.open(os.path.join(ctx.docdir, filename), 'rU', encoding='utf-8' ).read()
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
		self._do_test_render( '', 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.1', units='<unit1,unit2>')

	def test_render_units_with_percent( self ):
		self._do_test_render( '', 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.1', units=r'<unit1,\%>', units_html="unit1,%")

	def test_render_units_with_unicode( self ):
		self._do_test_render('', 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.1', units=r'<m²>', input_encoding='utf-8')  # m squared, u'\xb2'

	def test_render_units_with_latex_math_not_allowed( self ):
		with self.assertRaises(ValueError):
			self._do_test_render( '', 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.1', units=r'<$m^2$>')

	def test_assessment_index(self):
		example = br"""
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
						 'questions': [{'Class': 'Question',
						   'MimeType': 'application/vnd.nextthought.naquestion',
						   'NTIID': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.testquestion',
						   'content': '<a name="testquestion"></a> Arbitrary content goes here.',
						   'parts': [{'Class': 'SymbolicMathPart',
							 'MimeType': 'application/vnd.nextthought.assessment.symbolicmathpart',
							 'content': 'Arbitrary content goes here.',
							 'explanation': '',
							 'hints': [{'Class': 'HTMLHint',
							   'MimeType': 'application/vnd.nextthought.assessment.htmlhint',
							   'value': '<a name="a1e8744a89e9bf4e115903c4322d92e1" ></a>\n\n<p class="par" id="a1e8744a89e9bf4e115903c4322d92e1">Some hint </p>'}],
							 'solutions': [{'Class': 'LatexSymbolicMathSolution',
							   'MimeType': 'application/vnd.nextthought.assessment.latexsymbolicmathsolution',
							   'value': 'Some solution',
							   'weight': 1.0,
							   'allowed_units': ['unit1','unit2','']}]}]}]},
						'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.testquestion': {'Class': 'Question',
						 'MimeType': 'application/vnd.nextthought.naquestion',
						 'NTIID': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.testquestion',
						 'content': '<a name="testquestion"></a> Arbitrary content goes here.',
						 'parts': [{'Class': 'SymbolicMathPart',
						   'MimeType': 'application/vnd.nextthought.assessment.symbolicmathpart',
						   'content': 'Arbitrary content goes here.',
						   'explanation': '',
						   'hints': [{'Class': 'HTMLHint',
							 'MimeType': 'application/vnd.nextthought.assessment.htmlhint',
							 'value': '<a name="a1e8744a89e9bf4e115903c4322d92e1" ></a>\n\n<p class="par" id="a1e8744a89e9bf4e115903c4322d92e1">Some hint </p>'}],
						   'solutions': [{'Class': 'LatexSymbolicMathSolution',
							 'MimeType': 'application/vnd.nextthought.assessment.latexsymbolicmathsolution',
							 'value': 'Some solution',
							 'weight': 1.0,
							 'allowed_units': ['unit1','unit2','']}]}]}},
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
			assert_that( obj, is_( exp_value ) )


	def test_assessment_index_with_file_part(self):

		example = br"""
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
						'MimeType': 'application/vnd.nextthought.naquestion',
						'NTIID': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.testquestion',
						'content': '<a name="testquestion"></a> Arbitrary content goes here.',
						'parts': [{'Class': 'FilePart',
								   'MimeType': 'application/vnd.nextthought.assessment.filepart',
								   'allowed_extensions': [],
								   'allowed_mime_types': ['application/pdf'],
								   'content': 'Arbitrary content goes here.',
								   'explanation': u'',
								   'hints': [],
								   'max_file_size': None,
								   'solutions': []}]}

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

			assert_that( obj, is_( exp_value ) )

	def test_assessment_index_with_assignment(self):

		example = br"""
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


		\begin{naassignment}[not_before_date=2014-01-13]<Main Title>
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
						'content': '<a name="testquestion"></a> Arbitrary content goes here.',
						'parts': [{'Class': 'FilePart',
								   'MimeType': 'application/vnd.nextthought.assessment.filepart',
								   'allowed_extensions': [],
								   'allowed_mime_types': ['application/pdf'],
								   'content': 'Arbitrary content goes here.',
								   'explanation': u'',
								   'hints': [],
								   'max_file_size': None,
								   'solutions': []}]}

			exp_value = {'Items':
						 {'tag:nextthought.com,2011-10:testing-HTML-temp.0':
						  {'AssessmentItems': {},
						   'Items': {'tag:nextthought.com,2011-10:testing-HTML-temp.chapter_one':
									 {'AssessmentItems': {},
									  'Items': {'tag:nextthought.com,2011-10:testing-HTML-temp.section_one':
												{'AssessmentItems': {'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.asg.assignment':
																	 {'Class': 'Assignment',
																	  'is_non_public': True,
																	  'category_name': 'default',
																	  'MimeType': 'application/vnd.nextthought.assessment.assignment',
																	  'NTIID': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.asg.assignment',
																	  'available_for_submission_beginning': '2014-01-13T06:00:00Z',
																	  'available_for_submission_ending': None,
																	  'content': 'Assignment content.',
																	  'parts': [{'Class': 'AssignmentPart',
																				 'MimeType': 'application/vnd.nextthought.assessment.assignmentpart',
																				 'auto_grade': True,
																				 'content': 'Some content.',
																				 'question_set': {'Class': 'QuestionSet',
																								  'title': 'Set Title With % and $',
																								  'MimeType': 'application/vnd.nextthought.naquestionset',
																								  'NTIID': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.set.set',
																								  'questions': [question]},
																				 'title': 'Part Title'}],
																	  'title': 'Main Title'},
																	 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.set.set': {'Class': 'QuestionSet',
																																  'title': 'Set Title With % and $',
																																  'MimeType': 'application/vnd.nextthought.naquestionset',
																																  'NTIID': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.set.set',
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

			assert_that( obj, is_( exp_value ) )
			
	def test_freeresponse(self):
		example = br"""
			\begin{naquestion}
			\label{qid.prelab_scientific_method.03}
				\begin{naqfreeresponsepart}
					3. \$40 + \$5
					\begin{naqsolutions}
						\naqsolution[1] \$45
					\end{naqsolutions}
				\end{naqfreeresponsepart}
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

			jsons = open(os.path.join( ctx.docdir, 'assessment_index.json' ), 'rU' ).read()
			jsons = jsons.decode('utf-8')
			json.loads( jsons )
