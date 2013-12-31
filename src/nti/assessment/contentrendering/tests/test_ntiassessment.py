#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" """
from __future__ import print_function, unicode_literals
import os
from hamcrest import assert_that
from hamcrest import is_
from hamcrest import has_length
from hamcrest import contains_string
from hamcrest import same_instance
from hamcrest import has_property
from hamcrest import contains
from hamcrest import has_item
from hamcrest import has_key
from hamcrest import has_entry
from hamcrest import is_not as does_not
import unittest

import anyjson as json
from datetime import datetime

from ..ntiassessment import naquestion, naquestionset
from ..interfaces import IAssessmentExtractor
from nti.contentrendering.tests import buildDomFromString as _buildDomFromString
from nti.contentrendering.tests import simpleLatexDocumentText
from nti.contentrendering.tests import RenderContext

import nti.testing.base
from nti.testing.matchers import is_true
from nti.externalization.tests import externalizes
from nti.testing.matchers import verifiably_provides

import nti.contentrendering
from ... import interfaces as asm_interfaces

import nti.externalization
from nti.externalization.externalization import to_external_object
from nti.externalization.internalization import update_from_external_object

def _simpleLatexDocument(maths):
	return simpleLatexDocumentText( preludes=(br'\usepackage{ntiassessment}',),
									bodies=maths )

# Nose module-level setup and teardown
setUpModule = lambda: nti.testing.base.module_setup( set_up_packages=(nti.contentrendering,'nti.assessment',nti.externalization) )
tearDownModule = nti.testing.base.module_teardown

def test_generic_macros():
	example = br"""
	\begin{naquestion}[individual=true]
		Arbitrary content goes here.
		\begin{naqsymmathpart}
		Arbitrary content goes here.
		\begin{naqsolutions}
			\naqsolution $420$
			\naqsolution $\frac{5}{8}$
			\naqsolution $\left(3x+2\right)\left(2x+3\right)$
			\naqsolution $\surd2$
			\naqsolution $\frac{\surd\left(8x+5\right)\left(12x+12\right)}{\approx152318}+1204$
		\end{naqsolutions}
		\begin{naqhints}
			\naqhint Some hint
		\end{naqhints}
		\end{naqsymmathpart}
	\end{naquestion}
	"""

	dom = _buildDomFromString( _simpleLatexDocument( (example,) ) )
	assert_that( dom.getElementsByTagName('naquestion'), has_length( 1 ) )
	assert_that( dom.getElementsByTagName('naquestion')[0], is_( naquestion ) )

	naq = dom.getElementsByTagName('naquestion')[0]
	part_el = naq.getElementsByTagName( 'naqsymmathpart' )[0]
	values 	=  ['420',
				r'\frac{5}{8}',
				'\\left(3x+2\\right)\\left(2x+3\\right)',
				'\\surd 2',
				'\\frac{\\surd \\left(8x+5\\right)\\left(12x+12\\right)}{\\approx 152318}+1204']
	for index,item in enumerate(getattr( part_el, '_asm_solutions' )()):
		assert_that( item, verifiably_provides( part_el.soln_interface ) )
		assert_that( item, has_property( 'weight', 1.0 ) )
		assert_that( item, has_property( 'value', values[index] ) )

	part = part_el.assessment_object()
	assert_that( part, verifiably_provides( part_el.part_interface ) )
	assert_that( part.content, is_( "Arbitrary content goes here." ) )
	assert_that( part.hints, has_length( 1 ) )
	assert_that( part.hints, contains( verifiably_provides( asm_interfaces.IQHint ) ) )

def test_file_macros():
	example = br"""
	\begin{naquestion}[individual=true]
		Arbitrary content goes here.
		\begin{naqfilepart}(application/pdf,text/*,.txt,*,*/*)[1024]
		Arbitrary content goes here.
		\begin{naqhints}
			\naqhint Some hint
		\end{naqhints}
		\end{naqfilepart}
	\end{naquestion}
	"""

	dom = _buildDomFromString( _simpleLatexDocument( (example,) ) )

	naq = dom.getElementsByTagName('naquestion')[0]
	part_el = naq.getElementsByTagName( 'naqfilepart' )[0]

	part = part_el.assessment_object()
	assert_that( part, verifiably_provides( part_el.part_interface ) )
	assert_that( part.content, is_( "Arbitrary content goes here." ) )

	assert_that( part.allowed_extensions, contains( '.txt', '*' ) )
	assert_that( part.allowed_mime_types, contains( 'application/pdf', 'text/*', '*/*' ) )

	# TODO: Hints seem broken?
	#assert_that( part.hints, has_length( 1 ) )
	#assert_that( part.hints, contains( verifiably_provides( asm_interfaces.IQHint ) ) )

def test_essay_macros():
	example = br"""
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

	dom = _buildDomFromString( _simpleLatexDocument( (example,) ) )

	naq = dom.getElementsByTagName('naquestion')[0]
	part_el = naq.getElementsByTagName( 'naqessaypart' )[0]

	part = part_el.assessment_object()
	assert_that( part, verifiably_provides( part_el.part_interface ) )
	assert_that( part.content, is_( "Arbitrary content goes here." ) )

	assert_that( part.hints, has_length( 1 ) )
	assert_that( part.hints, contains( verifiably_provides( asm_interfaces.IQHint ) ) )

def test_essay_macro_with_blank_line_prologue():
	example = br"""
	\begin{naquestion}[individual=true]
		\label{the.label}
		Arbitrary content goes here,

		and there's a blank line, and another before the part:
		\begin{naqessaypart}
		Arbitrary content goes here.
		\begin{naqhints}
			\naqhint Some hint
		\end{naqhints}
		\end{naqessaypart}
	\end{naquestion}

	"""

	dom = _buildDomFromString( _simpleLatexDocument( (example,) ) )

	naq = dom.getElementsByTagName('naquestion')[0]
	naq = naq.assessment_object()


	# It's not rendered
	assert_that( naq.content, is_(''))

def test_essay_macro_with_blank_line_between_parts():
	example = br"""
	\begin{naquestion}[individual=true]
		\label{the.label}
		Arbitrary content goes here,

		and there's a blank line, and another before the part:
		\begin{naqessaypart}
		Arbitrary content goes here.
		\begin{naqhints}
			\naqhint Some hint
		\end{naqhints}
		\end{naqessaypart}


		\begin{naqfilepart}(application/pdf,text/*,.txt,*,*/*)[1024]
		Arbitrary content goes here.
		\begin{naqhints}
			\naqhint Some hint
		\end{naqhints}
		\end{naqfilepart}

	\end{naquestion}

	"""

	dom = _buildDomFromString( _simpleLatexDocument( (example,) ) )

	naq = dom.getElementsByTagName('naquestion')[0]
	naq = naq.assessment_object()
	assert_that( naq.parts, has_length(2) )

def test_question_set_macros():
	example = br"""
	\begin{naquestion}[individual=true]
		\label{question}
		Arbitrary content goes here.
		\begin{naqsymmathpart}
		Arbitrary content goes here.
		\begin{naqsolutions}
			\naqsolution $420$
			\naqsolution $\frac{5}{8}$
			\naqsolution $\left(3x+2\right)\left(2x+3\right)$
			\naqsolution $\surd2$
			\naqsolution $\frac{\surd\left(8x+5\right)\left(12x+12\right)}{\approx152318}+1204$
		\end{naqsolutions}
		\begin{naqhints}
			\naqhint Some hint
		\end{naqhints}
		\end{naqsymmathpart}
	\end{naquestion}

	\begin{naquestionset}
		\label{set}
		\naquestionref{question}
	\end{naquestionset}

	"""

	dom = _buildDomFromString( _simpleLatexDocument( (example,) ) )
	assert_that( dom.getElementsByTagName('naquestion'), has_length( 1 ) )
	assert_that( dom.getElementsByTagName('naquestion')[0], is_( naquestion ) )

	assert_that( dom.getElementsByTagName('naquestionset'), has_length( 1 ) )
	assert_that( dom.getElementsByTagName('naquestionset')[0], is_( naquestionset ) )

	qset_object = dom.getElementsByTagName( 'naquestionset' )[0].assessment_object()
	assert_that( qset_object.questions, has_length( 1 ) )
	assert_that( qset_object.ntiid, contains_string( 'set' ) )

def test_assignment_macros():
	example = br"""
	\begin{naquestion}[individual=true]
		\label{question}
		Arbitrary content goes here.
		\begin{naqsymmathpart}
		Arbitrary content goes here.
		\begin{naqsolutions}
			\naqsolution $420$
			\naqsolution $\frac{5}{8}$
			\naqsolution $\left(3x+2\right)\left(2x+3\right)$
			\naqsolution $\surd2$
			\naqsolution $\frac{\surd\left(8x+5\right)\left(12x+12\right)}{\approx152318}+1204$
		\end{naqsolutions}
		\begin{naqhints}
			\naqhint Some hint
		\end{naqhints}
		\end{naqsymmathpart}
	\end{naquestion}

	\begin{naquestionset}
		\label{set}
		\naquestionref{question}
	\end{naquestionset}

	\begin{naassignment}[not_before_date=2014-01-13,category=Quizzes]<Main Title>
		\label{assignment}
		Assignment content.
		\begin{naassignmentpart}[auto_grade=true]<Part Title>{set}
			Some content.
		\end{naassignmentpart}
	\end{naassignment}

	"""

	dom = _buildDomFromString( _simpleLatexDocument( (example,) ) )
	assert_that( dom.getElementsByTagName('naquestion'), has_length( 1 ) )
	assert_that( dom.getElementsByTagName('naquestion')[0], is_( naquestion ) )

	assert_that( dom.getElementsByTagName('naquestionset'), has_length( 1 ) )
	assert_that( dom.getElementsByTagName('naquestionset')[0], is_( naquestionset ) )

	qset_object = dom.getElementsByTagName( 'naquestionset' )[0].assessment_object()
	assert_that( qset_object.questions, has_length( 1 ) )
	assert_that( qset_object.ntiid, contains_string( 'set' ) )

	asg_object = dom.getElementsByTagName( 'naassignment' )[0].assessment_object()
	assert_that( asg_object, has_property( 'parts', has_length( 1 )))
	assert_that( asg_object.parts[0], has_property( 'question_set', same_instance(qset_object)))
	assert_that( asg_object.parts[0], has_property( 'auto_grade', is_true()))
	assert_that( asg_object.parts[0], has_property( 'content', 'Some content.'))
	assert_that( asg_object.parts[0], has_property( 'title', 'Part Title'))
	assert_that( asg_object, has_property('content', "Assignment content."))
	assert_that( asg_object.ntiid, contains_string('assignment'))
	assert_that( asg_object, has_property('title', 'Main Title'))
	assert_that( asg_object, has_property('category_name', 'quizzes'))
	assert_that( asg_object, has_property( 'available_for_submission_beginning',
										   datetime( 2014, 01, 13, 0, 0)))

	ext_obj = to_external_object(asg_object)
	raw_int_obj = type(asg_object)()
	update_from_external_object(raw_int_obj, ext_obj, require_updater=True)

def test_content_adaptation():
	doc = br"""
	\begin{naquestion}[individual=true]
		\begin{naqsymmathpart}
		%s
		\begin{naqsolutions}
			\naqsolution Hello
		\end{naqsolutions}
		\end{naqsymmathpart}
	\end{naquestion}
	"""
	def assert_content(content, output):
		dom = _buildDomFromString( _simpleLatexDocument( (doc % content,) ) )
		naq = dom.getElementsByTagName('naquestion')[0]
		part_el = naq.getElementsByTagName( 'naqsymmathpart' )[0]
		part = part_el.assessment_object()
		assert_that( part, verifiably_provides( part_el.part_interface ) )
		assert_that( part.content, is_( output ) )

	assert_content("Arbitrary content goes here.","Arbitrary content goes here.")
	assert_content( br"Equation: $123 \times 456$.","Equation: ." ) # Fails currently
	assert_content( br"Complex object \begin{tabular}{cc} \\ 1 & 2 \\3 & 4\\ \end{tabular}",
					br"Complex object" ) # Fails currently
	assert_content( br"Figure \begin{figure}[htbp]\begin{center}\includegraphics[width=100px]{images/wu1_square=3=by=x-2.pdf}\end{center}\end{figure}", br"Figure" ) # Fails currently


def test_free_response_macros():
	example = br"""
	\begin{naquestion}[individual=true]
		Arbitrary content goes here.
		\begin{naqfreeresponsepart}
		Arbitrary content goes here.
		\begin{naqsolutions}
			\naqsolution This is a solution.
				It may require multiple lines.

				It may span paragraphs.
			\naqsolution This is another solution.
			\naqsolution In some cases, \textit{it} may be complicated: $i$.

		\end{naqsolutions}
		\begin{naqhints}
			\naqhint Some hint
		\end{naqhints}
		\end{naqfreeresponsepart}
	\end{naquestion}
	"""

	dom = _buildDomFromString( _simpleLatexDocument( (example,) ) )
	assert_that( dom.getElementsByTagName('naquestion'), has_length( 1 ) )
	assert_that( dom.getElementsByTagName('naquestion')[0], is_( naquestion ) )
	naq = dom.getElementsByTagName('naquestion')[0]
	part_el = naq.getElementsByTagName( 'naqfreeresponsepart' )[0]

	part = part_el.assessment_object()
	assert_that( part, verifiably_provides( part_el.part_interface ) )
	assert_that( part.content, is_( "Arbitrary content goes here." ) )
	assert_that( part.solutions[0], has_property( "value", "This is a solution. It may require multiple lines. It may span paragraphs." ) )






def test_multiple_choice_macros():
	example = br"""
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

	dom = _buildDomFromString( _simpleLatexDocument( (example,) ) )
	assert_that( dom.getElementsByTagName('naquestion'), has_length( 1 ) )
	assert_that( dom.getElementsByTagName('naquestion')[0], is_( naquestion ) )

	assert_that( dom.getElementsByTagName('naqchoice'), has_length( 3 ) )
	assert_that( dom.getElementsByTagName('naqsolution'), has_length( 2 ) )


	naq = dom.getElementsByTagName('naquestion')[0]
	part_el = naq.getElementsByTagName( 'naqmultiplechoicepart' )[0]
	solns = getattr( part_el, '_asm_solutions' )()


	assert_that( solns[0], verifiably_provides( part_el.soln_interface ) )
	assert_that( solns[0], has_property( 'weight', 1.0 ) )

	assert_that( solns[1], verifiably_provides( part_el.soln_interface ) )
	assert_that( solns[1], has_property( 'weight', 0.5 ) )

	part = part_el.assessment_object()
	assert_that( part.solutions, is_( solns ) )
	assert_that( part, verifiably_provides( part_el.part_interface ) )
	assert_that( part.content, is_( "Arbitrary content for this part goes here." ) )
	assert_that( part.explanation, is_( "Arbitrary content explaining how the correct solution is arrived at." ) )
	assert_that( part, has_property( 'choices', has_length( 3 ) ) )
	assert_that( part.choices, has_item( 'Arbitrary content for the choice.' ) )


	quest_el = dom.getElementsByTagName('naquestion')[0]
	question = quest_el.assessment_object()
	assert_that( question.content, is_( 'Arbitrary prefix content goes here.' ) )
	assert_that( question.parts, contains( part ) )
	assert_that( question, has_property( 'ntiid', 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.1' ) )

	assert_that( question, externalizes( has_entry( 'NTIID', question.ntiid ) ) )

def test_multiple_choice_multiple_answer_macros():
	example = br"""
			\begin{naquestion}
			Arbitrary prefix content goes here.
			\begin{naqmultiplechoicemultipleanswerpart}
			   Arbitrary content for this part goes here.
			   \begin{naqchoices}
			   		\naqchoice Arbitrary content for the choice.
					\naqchoice[1] This is part of the right answer.
					\naqchoice[1] This is the other part of the right answer.
				\end{naqchoices}
				\begin{naqsolexplanation}
					Arbitrary content explaining how the correct solution is arrived at.
				\end{naqsolexplanation}
			\end{naqmultiplechoicemultipleanswerpart}
		\end{naquestion}
		"""

	dom = _buildDomFromString( _simpleLatexDocument( (example,) ) )
	assert_that( dom.getElementsByTagName('naquestion'), has_length( 1 ) )
	assert_that( dom.getElementsByTagName('naquestion')[0], is_( naquestion ) )

	assert_that( dom.getElementsByTagName('naqchoice'), has_length( 3 ) )
	assert_that( dom.getElementsByTagName('naqsolution'), has_length( 1 ) )

	for _naqchoice in dom.getElementsByTagName('naqchoice'):
		assert_that( dict(_naqchoice.attributes), has_key('weight'))


	naq = dom.getElementsByTagName('naquestion')[0]
	part_el = naq.getElementsByTagName( 'naqmultiplechoicemultipleanswerpart' )[0]
	solns = getattr( part_el, '_asm_solutions' )()


	assert_that( solns[0], verifiably_provides( part_el.soln_interface ) )
	assert_that( solns[0], has_property( 'weight', 1.0 ) )


	part = part_el.assessment_object()
	assert_that( part.solutions, is_( solns ) )
	assert_that( part, verifiably_provides( part_el.part_interface ) )
	assert_that( part.content, is_( "Arbitrary content for this part goes here." ) )
	assert_that( part.explanation, is_( "Arbitrary content explaining how the correct solution is arrived at." ) )
	assert_that( part, has_property( 'choices', has_length( 3 ) ) )
	assert_that( part.choices, has_item( 'Arbitrary content for the choice.' ) )


	quest_el = dom.getElementsByTagName('naquestion')[0]
	question = quest_el.assessment_object()
	assert_that( question.content, is_( 'Arbitrary prefix content goes here.' ) )
	assert_that( question.parts, contains( part ) )
	assert_that( question, has_property( 'ntiid', 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.1' ) )

	assert_that( question, externalizes( has_entry( 'NTIID', question.ntiid ) ) )

def test_matching_macros():
	example = br"""
		\begin{naquestion}
			\begin{naqmatchingpart}
			In Rome, women used hair color to indicate their class in society. Match the correct shade with its corresponding class:
				\begin{tabular}{cc}
					Noblewomen & Black \\
					Middle-class & Red \\
					Poor women & Blond \\
				\end{tabular}
				\begin{naqmlabels}
					\naqmlabel[2] Noblewomen
					\naqmlabel[0] Middle-class
					\naqmlabel[1] Poor women
				\end{naqmlabels}
				\begin{naqmvalues}
				   \naqmvalue Black
				   \naqmvalue Red
				   \naqmvalue Blond
				\end{naqmvalues}
			\end{naqmatchingpart}
		\end{naquestion}
		"""

	dom = _buildDomFromString( _simpleLatexDocument( (example,) ) )
	assert_that( dom.getElementsByTagName('naquestion'), has_length( 1 ) )
	assert_that( dom.getElementsByTagName('naquestion')[0], is_( naquestion ) )

	assert_that( dom.getElementsByTagName('naqmlabel'), has_length( 3 ) )
	assert_that( dom.getElementsByTagName('naqmvalue'), has_length( 3 ) )


	naq = dom.getElementsByTagName('naquestion')[0]
	part_el = naq.getElementsByTagName( 'naqmatchingpart' )[0]
	soln = getattr( part_el, '_asm_solutions' )()[0]


	assert_that( soln, verifiably_provides( part_el.soln_interface ) )
	assert_that( soln, has_property( 'value', {0: 2, 1: 0, 2: 1} ) )
	assert_that( soln, has_property( 'weight', 1.0 ) )

	part = part_el.assessment_object()
	assert_that( part, verifiably_provides( part_el.part_interface ) )
	assert_that( part, has_property( 'labels', has_length( 3 ) ) )
	assert_that( part.labels, has_item( 'Noblewomen' ) )
	assert_that( part, has_property( 'values', has_length( 3 ) ) )
	assert_that( part.values, has_item( 'Black' ) )


from zope import component
from zope import interface
from nti.contentrendering import interfaces as cdr_interfaces
from nti.contentrendering.resources import ResourceRenderer
import io

@interface.implementer(cdr_interfaces.IRenderedBook)
class _MockRenderedBook(object):
	document = None
	contentLocation = None


class TestRenderableSymMathPart(unittest.TestCase):

	def _do_test_render( self, label, ntiid, filename='index.html', units='', units_html=None, input_encoding=None ):

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

		with RenderContext(_simpleLatexDocument( (example,) ), output_encoding='utf-8', input_encoding=input_encoding) as ctx:
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
		"The label for the question becomes part of its NTIID."
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
						'title': None,
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

		\begin{naquestionset}<Set Title>
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
																	  'category_name': 'default',
																	  'MimeType': 'application/vnd.nextthought.assessment.assignment',
																	  'NTIID': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.asg.assignment',
																	  'available_for_submission_beginning': '2014-01-13T00:00:00',
																	  'available_for_submission_ending': None,
																	  'content': 'Assignment content.',
																	  'parts': [{'Class': 'AssignmentPart',
																				 'MimeType': 'application/vnd.nextthought.assessment.assignmentpart',
																				 'auto_grade': True,
																				 'content': 'Some content.',
																				 'question_set': {'Class': 'QuestionSet',
																								  'title': 'Set Title',
																								  'MimeType': 'application/vnd.nextthought.naquestionset',
																								  'NTIID': 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.set.set',
																								  'questions': [question]},
																				 'title': 'Part Title'}],
																	  'title': 'Main Title'},
																	 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.set.set': {'Class': 'QuestionSet',
																																  'title': 'Set Title',
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
