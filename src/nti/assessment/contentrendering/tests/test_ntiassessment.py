#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import has_key
from hamcrest import contains
from hamcrest import has_item
from hamcrest import has_entry
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_entries
from hamcrest import has_property
from hamcrest import same_instance
from hamcrest import contains_string

from datetime import datetime

from nti.externalization.externalization import to_external_object
from nti.externalization.internalization import update_from_external_object

from nti.assessment import interfaces as asm_interfaces
from nti.assessment.contentrendering.ntiassessment import naquestion, naquestionset
from nti.assessment.contentrendering.ntiassessment import naquestionfillintheblankwordbank

from nti.contentrendering.tests import buildDomFromString as _buildDomFromString

from nti.testing.matchers import is_true
from nti.externalization.tests import externalizes
from nti.testing.matchers import verifiably_provides

from nti.assessment.tests import AssessmentTestCase
from nti.assessment.tests import _simpleLatexDocument

class TestMisc(AssessmentTestCase):

	def test_generic_macros(self):
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

	def test_file_macros(self):
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

	def test_essay_macros(self):
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

	def test_essay_macro_with_blank_line_prologue(self):
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

	def test_essay_macro_with_blank_line_between_parts(self):
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

	def test_question_set_macros(self):
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

	def test_assignment_macros(self):
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

		\begin{naassignment}[not_before_date=2014-01-13,category=Quizzes,public=1]<Main Title>
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
		assert_that( asg_object, has_property('is_non_public', False))
		assert_that( asg_object, has_property('category_name', 'quizzes'))
		assert_that( asg_object, has_property( 'available_for_submission_beginning',
											   datetime( 2014, 01, 13, 6, 0)))

		ext_obj = to_external_object(asg_object)
		raw_int_obj = type(asg_object)()
		update_from_external_object(raw_int_obj, ext_obj, require_updater=True)

	def test_content_adaptation(self):
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


	def test_free_response_macros(self):
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


	def test_multiple_choice_macros(self):
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

		dom = _buildDomFromString(_simpleLatexDocument((example,)))
		assert_that(dom.getElementsByTagName('naquestion'), has_length(1))
		assert_that(dom.getElementsByTagName('naquestion')[0], is_(naquestion))

		assert_that(dom.getElementsByTagName('naqchoice'), has_length(3))
		assert_that(dom.getElementsByTagName('naqsolution'), has_length(2))

		naq = dom.getElementsByTagName('naquestion')[0]
		part_el = naq.getElementsByTagName('naqmultiplechoicepart')[0]
		solns = getattr(part_el, '_asm_solutions')()

		assert_that(solns[0], verifiably_provides(part_el.soln_interface))
		assert_that(solns[0], has_property('weight', 1.0))

		assert_that(solns[1], verifiably_provides(part_el.soln_interface))
		assert_that(solns[1], has_property('weight', 0.5))

		part = part_el.assessment_object()
		assert_that(part.solutions, is_(solns))
		assert_that(part, verifiably_provides(part_el.part_interface))
		assert_that(part.content, is_("Arbitrary content for this part goes here."))
		assert_that(part.explanation, is_("Arbitrary content explaining how the correct solution is arrived at."))
		assert_that(part, has_property('choices', has_length(3)))
		assert_that(part.choices, has_item('Arbitrary content for the choice.'))

		quest_el = dom.getElementsByTagName('naquestion')[0]
		question = quest_el.assessment_object()
		assert_that(question.content, is_('Arbitrary prefix content goes here.'))
		assert_that(question.parts, contains(part))
		assert_that(question, has_property('ntiid', 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.1'))

		assert_that(question, externalizes(has_entry('NTIID', question.ntiid)))

	def test_fill_in_the_blank_short_answer_part(self):
		example = br"""
				\begin{naquestion}
				Arbitrary prefix content goes here.
				\begin{naqfillintheblankshortanswerpart}
					Arbitrary content for this part goes here. \naqblankfield{001}[2] \naqblankfield{002}[2]
					\begin{naqregexes}
						\naqregex{001}{^yes\\s*[\,|\\s]\\s*I will} Yes, I will.
						\naqregex{002}{\\s*\\\$?\\s?945.20} 945.20
					\end{naqregexes}
					\begin{naqsolexplanation}
						Arbitrary content explaining how the correct solution is arrived at.
					\end{naqsolexplanation}
				\end{naqfillintheblankshortanswerpart}
			\end{naquestion}
			"""

		dom = _buildDomFromString(_simpleLatexDocument((example,)))
		assert_that(dom.getElementsByTagName('naquestion'), has_length(1))
		assert_that(dom.getElementsByTagName('naquestion')[0], is_(naquestion))

		assert_that(dom.getElementsByTagName('naqregexes'), has_length(1))
		assert_that(dom.getElementsByTagName('naqregex'), has_length(2))
		assert_that(dom.getElementsByTagName('naqsolution'), has_length(1))

		naq = dom.getElementsByTagName('naquestion')[0]
		part_el = naq.getElementsByTagName('naqfillintheblankshortanswerpart')[0]
		solns = getattr(part_el, '_asm_solutions')()
		
		assert_that(solns, has_length(1))
		assert_that(solns[0], has_property('value', 
										  has_entries('001', has_property('pattern', '^yes\\s*[,|\\s]\\s*I will'), 
													  '002', has_property('pattern', '\\s*\\$?\\s?945.20') )))

		assert_that(solns[0], verifiably_provides(part_el.soln_interface))
		assert_that(solns[0], has_property('weight', 1.0))

		part = part_el.assessment_object()
		assert_that(part.solutions, is_(solns))
		assert_that(part, verifiably_provides(part_el.part_interface))
		assert_that(part.content, is_("Arbitrary content for this part goes here."))
		assert_that(part.explanation, is_("Arbitrary content explaining how the correct solution is arrived at."))

		quest_el = dom.getElementsByTagName('naquestion')[0]
		question = quest_el.assessment_object()
		assert_that(question.content, is_('Arbitrary prefix content goes here.'))
		assert_that(question.parts, contains(part))
		assert_that(question, has_property('ntiid', 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.1'))

		assert_that(question, externalizes(has_entry('NTIID', question.ntiid)))

	def test_fill_in_the_blank_word_bank_part(self):
		example = br"""
			\begin{naquestion}
				Arbitrary prefix content goes here.
				\begin{naqfillintheblankwithwordbankpart}
					Arbitrary content for this part goes here.
					\begin{naqinput}
						empty fields \naqblankfield{1} \naqblankfield{2} \naqblankfield{3} go here
					\end{naqinput}
					\begin{naqwordbank}[unique=false]
						\naqwordentry{0}{montuno}{es}
						\naqwordentry{1}{tiene}{es}
						\naqwordentry{2}{borinquen}{es}
						\naqwordentry{3}{tierra}{es}
						\naqwordentry{4}{alma}{es}
					\end{naqwordbank}
					\begin{naqpaireditems}
						\naqpaireditem{1}{2}
						\naqpaireditem{2}{1}
						\naqpaireditem{3}{0}
					\end{naqpaireditems}
					\begin{naqsolexplanation}
						Arbitrary content explaining how the correct solution is arrived at.
					\end{naqsolexplanation}
				\end{naqfillintheblankwithwordbankpart}
			\end{naquestion}
			"""

		dom = _buildDomFromString( _simpleLatexDocument( (example,) ) )
		assert_that( dom.getElementsByTagName('naquestion'), has_length( 1 ) )
		assert_that(dom.getElementsByTagName('naquestion')[0], is_(naquestion))

		assert_that(dom.getElementsByTagName('naqwordbank'), has_length(1))
		assert_that(dom.getElementsByTagName('naqwordentry'), has_length(5))
		assert_that(dom.getElementsByTagName('naqsolution'), has_length(1))

		naq = dom.getElementsByTagName('naquestion')[0]
		part_el = naq.getElementsByTagName('naqfillintheblankwithwordbankpart')[0]
		solns = getattr(part_el, '_asm_solutions')()

		assert_that(solns[0], verifiably_provides(part_el.soln_interface))
		assert_that(solns[0], has_property('weight', 1.0))

		part = part_el.assessment_object()
		assert_that(part.solutions, is_(solns))
		assert_that(part, verifiably_provides(part_el.part_interface))
		assert_that(part.content, is_("Arbitrary content for this part goes here."))
		assert_that(part.explanation, is_("Arbitrary content explaining how the correct solution is arrived at."))

		quest_el = dom.getElementsByTagName('naquestion')[0]
		question = quest_el.assessment_object()
		assert_that(question.content, is_('Arbitrary prefix content goes here.'))
		assert_that(question.parts, contains(part))
		assert_that(question, has_property('ntiid', 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.1'))

		assert_that(question, externalizes(has_entry('NTIID', question.ntiid)))

	def test_fill_in_the_blank_word_bank_question(self):
		example = br"""
			\begin{naquestionfillintheblankwordbank}
				Salsa and Bleach goes here.
				\begin{naqwordbank}
					\naqwordentry{100}{shikai}{es}
					\naqwordentry{200}{bankai}{es}
					\naqwordentry{300}{captain}{es}
				\end{naqwordbank}
				\begin{naqfillintheblankwithwordbankpart}
					Arbitrary content for this part goes here.
					\begin{naqinput}
						empty fields \naqblankfield{1} \naqblankfield{2} \naqblankfield{3} go here
					\end{naqinput}
					\begin{naqwordbank}[unique=false]
						\naqwordentry{0}{montuno}{es}
						\naqwordentry{1}{tiene}{es}
						\naqwordentry{2}{borinquen}{es}
						\naqwordentry{3}{tierra}{es}
						\naqwordentry{4}{alma}{es}
					\end{naqwordbank}
					\begin{naqpaireditems}
						\naqpaireditem{1}{2}
						\naqpaireditem{2}{1}
						\naqpaireditem{3}{0}
					\end{naqpaireditems}
					\begin{naqsolexplanation}
						Arbitrary content explaining how the correct solution is arrived at.
					\end{naqsolexplanation}
				\end{naqfillintheblankwithwordbankpart}
			\end{naquestionfillintheblankwordbank}
			"""

		dom = _buildDomFromString(_simpleLatexDocument((example,)))
		assert_that(dom.getElementsByTagName('naquestionfillintheblankwordbank'), has_length(1))
		assert_that(dom.getElementsByTagName('naquestionfillintheblankwordbank')[0], is_(naquestionfillintheblankwordbank))

		assert_that(dom.getElementsByTagName('naqwordbank'), has_length(2))
		assert_that(dom.getElementsByTagName('naqwordentry'), has_length(8))

		quest_el = dom.getElementsByTagName('naquestionfillintheblankwordbank')[0]
		assessment = quest_el.assessment_object()
		assert_that(assessment.content, is_('Salsa and Bleach goes here.'))
		assert_that(assessment.parts, has_length(1))
		assert_that(assessment.wordbank, has_length(3))
		assert_that(assessment, has_property('ntiid', 'tag:nextthought.com,2011-10:testing-NAQ-temp.naq.1'))
		assert_that(assessment, externalizes(has_entry('NTIID', assessment.ntiid)))

	def test_multiple_choice_multiple_answer_macros(self):
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

	def test_matching_macros(self):
		for part_name in ("naqmatchingpart", "naqorderingpart"):
			example = br"""
				\begin{naquestion}
					\begin{xxxxxxxxx}
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
					\end{xxxxxxxxx}
				\end{naquestion}
				""".replace("xxxxxxxxx", part_name)

			dom = _buildDomFromString( _simpleLatexDocument( (example,) ) )
			assert_that( dom.getElementsByTagName('naquestion'), has_length( 1 ) )
			assert_that( dom.getElementsByTagName('naquestion')[0], is_( naquestion ) )
	
			assert_that( dom.getElementsByTagName('naqmlabel'), has_length( 3 ) )
			assert_that( dom.getElementsByTagName('naqmvalue'), has_length( 3 ) )
	
			naq = dom.getElementsByTagName('naquestion')[0]
			part_el = naq.getElementsByTagName(part_name)[0]
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
