#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import itertools

from zope import schema
from zope.cachedescriptors.method import cachedIn
from zope.cachedescriptors.property import readproperty

from plasTeX import Base

from nti.contentfragments.interfaces import LatexContentFragment
from nti.contentfragments.interfaces import ILatexContentFragment

from nti.contentrendering.plastexpackages._util import _is_renderable
from nti.contentrendering.plastexpackages._util import _asm_rendered_textcontent
from nti.contentrendering.plastexpackages._util import _htmlcontent_rendered_elements
from nti.contentrendering.plastexpackages._util import LocalContentMixin as _BaseLocalContentMixin

from ..interfaces import IQHTMLHint
from ..interfaces import IQMathSolution

def aspveint(obj):
	try:
		result = int(obj)
		assert result > 0
		return result
	except (AssertionError, TypeError, ValueError):
		raise ValueError("Bad positive integer value: %r" % obj)

def _asm_local_sourcecontent(self, ignorable_renderables=()):
	"""
	Collects the tex source of the children of self. Returns a `unicode`
	object.

	:keyword ignorable_renderables: If given, a tuple (yes, tuple)
		of classes. If a given child node is an instance of a
		class in the tuple, it will be ignored and not returned.
	"""

	if not ignorable_renderables:
		selected_children = self.childNodes
	else:
		selected_children = \
			tuple(node for node in self.childNodes \
				  if not isinstance(node, ignorable_renderables))

	result = ILatexContentFragment(' '.join([x.source for x in selected_children]).strip())
	return result

class _LocalContentMixin(_BaseLocalContentMixin):
	# SAJ: HACK. Something about naqvideo and _LocalContentMixin? ALl the parts
	# and solutions from this module are excluded from rendering
	_asm_ignorable_renderables = ()

	# SAJ: The only time the following method is executed is prior to initial
	# rendering of the element. The _after_render method of the parent class
	# overwrites _asm_local_content to contain the filtered rendered content
	# instead of the following method.
	@readproperty
	def _asm_local_content(self):
		if self.renderer and _is_renderable(self.renderer, self.childNodes):
			result = _asm_rendered_textcontent(self, self._asm_ignorable_renderables)
		else:
			result = _asm_local_sourcecontent(self)
		return result

class _AbstractNAQPart(_LocalContentMixin, Base.Environment):

	randomize = False

	#: Defines the type of part this maps too
	part_interface = None

	#: Defines the type of solution this part produces.
	#: Solution objects will be created by adapting the text content of the solution DOM nodes
	#: into this interface.
	soln_interface = None

	part_factory = None
	hint_interface = IQHTMLHint

	args = '[randomize:str]'

	def _asm_solutions(self):
		"""
		Returns a list of solutions (of the type identified in ``soln_interface``).
		This implementation investigates the child nodes of this object; subclasses
		may do something different.

		"""
		solutions = []
		solution_els = self.getElementsByTagName( 'naqsolution' )
		for solution_el in solution_els:
			# If the textContent is taken instead of the source of the child element, the
			# code fails on Latex solutions like $\frac{1}{2}$
			# TODO: Should this be rendered? In some cases yes, in some cases no?
			content = ' '.join([c.source.strip() for c in solution_el.childNodes]).strip()
			if len(content) >= 2 and content.startswith( '$' ) and content.endswith( '$' ):
				content = content[1:-1]

			# Note that this is already a latex content fragment, we don't need
			# to adapt it with the interfaces. If we do, a content string like "75\%" becomes
			# "75\\\\%\\", which is clearly wrong
			sol_text = unicode(content).strip()
			solution = self.soln_interface(LatexContentFragment(sol_text))
			weight = solution_el.attributes['weight']
			if weight is not None:
				solution.weight = weight

			if self.soln_interface.isOrExtends(IQMathSolution):
				# Units given? We currently always make units optional, given or not
				# This can easily be changed or configured
				allowed_units = solution_el.units_to_text_list()
				if not allowed_units:
					allowed_units = ('',)
				if '' not in allowed_units:
					allowed_units = list(allowed_units)
					allowed_units.append( '' )
				solution.allowed_units = allowed_units
			solutions.append( solution )

		return solutions

	def _asm_explanation(self):
		exp_els = self.getElementsByTagName( 'naqsolexplanation' )
		assert len(exp_els) <= 1
		if exp_els:
			return exp_els[0]._asm_local_content
		return ILatexContentFragment( '' )

	def _asm_hints(self):
		"""
		Collects the ``naqhint`` tags found beneath this element,
		converts them to the type of object identified by ``hint_interface``,
		and returns them in a list. For use by :meth:`assessment_object`
		"""
		hints = []
		hint_els = self.getElementsByTagName('naqhint')
		for hint_el in hint_els:
			hint = self.hint_interface( hint_el._asm_local_content )
			hints.append( hint )
		return hints

	def _asm_object_kwargs(self):
		"""
		Subclasses may override this to return a dictionary of keyword
		arguments to pass to ``part_factory`` when creating
		the corresponding assessment object.
		"""
		return {}

	@cachedIn('_v_assessment_object')
	def assessment_object( self ):
		# Be careful to turn textContent into plain unicode objects, not
		# plastex Text subclasses, which are also expensive nodes.
		result = self.part_factory( content=self._asm_local_content,
									solutions=self._asm_solutions(),
									explanation=self._asm_explanation(),
									hints=self._asm_hints(),
									**self._asm_object_kwargs()	)

		errors = schema.getValidationErrors( self.part_interface, result )
		if errors: # pragma: no cover
			__traceback_info__ = self.part_interface, errors, result
			raise errors[0][1]
		return result

	def _after_render( self, rendered ):
		super(_AbstractNAQPart,self)._after_render( rendered )
		# The hints and explanations don't normally get rendered
		# by the templates, so make sure they do
		for x in itertools.chain(self.getElementsByTagName('naqsolexplanation'),
								 self.getElementsByTagName('naqsolution'),
								 self.getElementsByTagName('naqhint'),
								 self.getElementsByTagName('naqchoice'),
								 self.getElementsByTagName('naqmlabel'),
								 self.getElementsByTagName('naqmvalue')):
			unicode(x)

	def invoke(self, tex):
		token = super(_AbstractNAQPart, self).invoke(tex)
		if	'randomize' in self.attributes and \
			(self.attributes['randomize'] or '').lower() == 'randomize=true':
			self.randomize = True
			self.attributes['randomize'] = 'true'
		else:
			self.randomize = False
			self.attributes['randomize'] = 'false'
		return token

class naqvalue(_LocalContentMixin, Base.List.item):

	@readproperty
	def _asm_local_content(self):
		if _is_renderable(self.renderer, self.childNodes):
			result = _htmlcontent_rendered_elements(self.renderer, self.childNodes)
		else:
			result = ILatexContentFragment(unicode(self.textContent).strip())
		return result
