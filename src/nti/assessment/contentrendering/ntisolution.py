#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from plasTeX import Base

from .ntibase import _LocalContentMixin

# Handle custom counter names

class naqsolutionnumname(Base.Command):
	unicode = ''

class naqsolutions(Base.List):

	counters = ['naqsolutionnum']
	args = '[ init:int ]'

	def invoke( self, tex ):
		# TODO: Why is this being done?
		res = super(naqsolutions, self).invoke( tex )

		if 'init' in self.attributes and self.attributes['init']:
			self.ownerDocument.context.counters[self.counters[0]].setcounter(self.attributes['init'])
		elif self.macroMode != Base.Environment.MODE_END:
			self.ownerDocument.context.counters[self.counters[0]].setcounter(0)

		return res

	def digest( self, tokens ):
		# After digesting loop back over the children moving nodes before
		# the first item into the first item
		# TODO: Why is this being done?
		res = super(naqsolutions, self).digest(tokens)
		if self.macroMode != Base.Environment.MODE_END:
			nodesToMove = []

			for node in self:

				if isinstance(node, Base.List.item):
					nodesToMove.reverse()
					for nodeToMove in nodesToMove:
						self.removeChild(nodeToMove)
						node.insert(0, nodeToMove)
					break

				nodesToMove.append(node)

		return res

class naqsolution(Base.List.item):

	args = '[weight:float] <units>'

	# We use <> for the units list because () looks like a geometric
	# point, and there are valid answers like that.
	# We also do NOT use the :list conversion, because if the units list
	# has something like an (escaped) % in it, plasTeX fails to tokenize the list
	# Instead, we work with the TexFragment object ourself

	def invoke( self, tex ):
		# TODO: Why is this being done? Does the counter matter?
		self.counter = naqsolutions.counters[0]
		self.position = self.ownerDocument.context.counters[self.counter].value + 1
		#ignore the list implementation
		return Base.Command.invoke(self,tex)

	def units_to_text_list(self):
		"""Find the units, if any, and return a list of their text values"""
		units = self.attributes.get( 'units' )
		if units:
			# Remove trailing delimiter and surrounding whitespace. For consecutive
			# text parts, we have to split ourself
			result = []
			for x in units:
				# We could get elements (Macro/Command) or strings (plastex.dom.Text)
				if getattr( x, 'tagName', None ) == 'math':
					raise ValueError( "Math cannot be roundtripped in units. Try unicode symbols" )
				x = unicode(x).rstrip( ',' ).strip()
				result.extend( x.split( ',' ) )
			return result

	def units_to_html(self):
		units = self.units_to_text_list()
		if units:
			return ','.join( units )

###
# Explanations
###

class naqsolexplanation(_LocalContentMixin, Base.Environment):
	pass

