#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope.interface.registry import Components

from nti.contentfragments.interfaces import LatexContentFragment

from nti.externalization.internalization import find_factory_for
from nti.externalization.internalization import update_from_external_object

from .interfaces import IQuestion
from .interfaces import IQAssignment
from .interfaces import IQuestionSet

from ._util import iface_of_assessment as _iface_to_register

def _ntiid_object_hook( k, v, x ):
	"""
	In this one, rare, case, we are reading things from external
	sources and need to preserve an NTIID value.
	"""
	if 'NTIID' in x and not getattr( v, 'ntiid', None ):
		v.ntiid = x['NTIID']
		v.__name__ = v.ntiid

	if 'value' in x and 'Class' in x and x['Class'] == 'LatexSymbolicMathSolution' and \
		x['value'] != v.value:
		# We started out with LatexContentFragments when we wrote these,
		# and if we re-convert when we read, we tend to over-escape
		# One thing we do need to do, though, is replace long dashes with standard
		# minus signs
		v.value = LatexContentFragment(x['value'].replace(u'\u2212', '-'))
	return v

class QuestionIndex(object):

	def _explode_assignment_to_register(self, assignment):
		things_to_register = set([assignment])
		for part in assignment.parts:
			qset = part.question_set
			things_to_register.update(self._explode_object_to_register(qset))
		return things_to_register

	def _explode_question_set_to_register(self, question_set):
		things_to_register = set([question_set])
		for child_question in question_set.questions:
			things_to_register.add( child_question )
		return things_to_register

	def _explode_object_to_register(self, obj):
		things_to_register = set([obj])
		if IQAssignment.providedBy(obj):
			things_to_register.update(self._explode_assignment_to_register(obj))
		elif IQuestionSet.providedBy(obj):
			things_to_register.update(self._explode_question_set_to_register(obj))
		return things_to_register

	def _canonicalize_question_set(self, obj, registry):
		obj.questions = [registry.getUtility(IQuestion, name=x.ntiid)
						 for x
						 in obj.questions]

	def _canonicalize_object(self, obj, registry):
		if IQAssignment.providedBy(obj):
			for part in obj.parts:
				ntiid = part.question_set.ntiid
				part.question_set = registry.getUtility(IQuestionSet, name=ntiid)
				self._canonicalize_question_set(part.question_set, registry)
		elif IQuestionSet.providedBy(obj):
			self._canonicalize_question_set(obj, registry)

	def _register_and_canonicalize(self, things_to_register, registry):

		for thing_to_register in things_to_register:
			iface = _iface_to_register(thing_to_register)

			registry.registerUtility( thing_to_register,
									  provided=iface,
									  name=thing_to_register.ntiid,
									  event=False)

		# Now that everything is in place, we can canonicalize
		for o in things_to_register:
			self._canonicalize_object(o, registry)

	def _process_assessments( self, 
							  assessment_item_dict,
							  containing_hierarchy_key,
							  level_ntiid=None,
							  signatures_dict=None):

		result = set()
		for k, v in assessment_item_dict.items():
			__traceback_info__ = k, v
			
			factory = find_factory_for( v )
			assert factory is not None
			
			obj = factory()
			update_from_external_object(obj, v, require_updater=True,
										notify=False,
										object_hook=_ntiid_object_hook )

			obj.ntiid = k
			obj.signature = signatures_dict.get(k) if signatures_dict else None
			obj.__name__ = unicode( k ).encode('utf8').decode('utf8')

			# No matter if we got an assignment or question set first or the questions
			# first, register the question objects exactly once. Replace
			# any question children of a question set by the registered object.
			things_to_register = self._explode_object_to_register(obj)
			result.update(things_to_register)

		return result

	def _from_index_entry( self, 
						   index,
						   nearest_containing_key=None,
						   nearest_containing_ntiid=None):

		key_for_this_level = nearest_containing_key
	
		things_to_register = set()
		level_ntiid = index.get( 'NTIID' ) or nearest_containing_ntiid
		
		i = self._process_assessments(  index.get( "AssessmentItems", {} ),
										key_for_this_level,
										level_ntiid,
										index.get("Signatures"))

		things_to_register.update(i)
		for child_item in index.get('Items',{}).values():
			i = self._from_index_entry( child_item,
										nearest_containing_key=key_for_this_level,
										nearest_containing_ntiid=level_ntiid)
			things_to_register.update(i)

		return things_to_register

	def _from_root_index( self, assessment_index_json, registry=None):

		__traceback_info__ = assessment_index_json
	
		registry = registry if registry is not None else Components()

		assert 'Items' in assessment_index_json, "Root must contain 'Items'"
		root_items = assessment_index_json['Items']
		if not root_items:
			logger.warn("Assessment index does not contains any assessments")
			return
		assert len(root_items) == 1, "Root's 'Items' must only have Root NTIID"

		root_ntiid = root_items.keys()[0]
		assert 	'Items' in assessment_index_json['Items'][root_ntiid], \
				"Root's 'Items' contains the actual section Items"

		things_to_register = set()

		for child_ntiid, child_index in root_items[root_ntiid]['Items'].items():
			
			__traceback_info__ = child_ntiid, child_index

			assert 	child_index.get( 'filename' ), \
					'Child must contain valid filename to contain assessments'
		
			i = self._from_index_entry( child_index,
										nearest_containing_ntiid=child_ntiid)
			things_to_register.update(i)

		# register assessment items
		self._register_and_canonicalize(things_to_register, registry)

		registered =  {x.ntiid for x in things_to_register}
		return registered
