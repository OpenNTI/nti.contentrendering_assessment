#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import os
import codecs
import simplejson as json  # Needed for sort_keys, ensure_ascii

from zope import component
from zope import interface

from nti.contentrendering.interfaces import IRenderedBook

from nti.assessment.common import hashfile
from nti.assessment.common import signature

from nti.externalization.internalization import find_factory_for
from nti.externalization.externalization import toExternalObject
from nti.externalization.internalization import update_from_external_object

from ..interfaces import IAssessmentExtractor

@interface.implementer(IAssessmentExtractor)
@component.adapter(IRenderedBook)
class _AssessmentExtractor(object):
	"""
	"Transforms" a rendered book by extracting assessment information into a separate file
	called ``assessment_index.json.`` This file describes a dictionary with the following
	structure::

		Items => { # Keyed by NTIID of the file
			NTIID => string # This level is about an NTIID section
			filename => string # The relative containing file for this NTIID
			AssessmentItems => { # Keyed by NTIID of the question
				NTIID => string # The NTIID of the question
				... # All the rest of the keys of the question object
			}
			Items => { # Keyed by NTIIDs of child sections; recurses
				# As containing, except 'filename' will be null/None
			}
		}

	"""

	def __init__(self, book=None):
		pass

	def transform(self, book, savetoc=True, outpath=None):
		outpath = outpath or book.contentLocation
		outpath = os.path.expanduser(outpath)
		target = os.path.join(outpath, 'assessment_index.json')

		index = {'Items': {}, 'Signatures':{}}
		documents = book.document.getElementsByTagName('document')
		if not documents:
			return

		self._build_index(documents[0], index['Items'], index['Signatures'])
		index['href'] = index.get('href', 'index.html')

		logger.info("extracting assessments to %s" , target)
		with codecs.open(target, 'w', encoding='utf-8') as fp:
			# sort_keys for repeatability. Do force ensure_ascii because even though
			# we're using codes to  encode automatically, the reader might not decode
			json.dump(index, fp, indent='\t', sort_keys=True, ensure_ascii=True)

		with open(target, "rb") as fp:
			sha256 = hashfile(fp)

		target = os.path.join(outpath, 'assessment_index.json.sha256')
		with open(target, "wb") as fp:
			fp.write(sha256)
		return index

	def _to_external_object(self, obj):
		return toExternalObject(obj, decorate=False)

	def _build_index(self, element, index, signatures):
		"""
		Recurse through the element adding assessment objects to the index,
		keyed off of NTIIDs.

		:param dict index: The containing index node. Typically, this will be
			an ``Items`` dictionary in a containing index.
		"""
		if self._is_uninteresting(element):
			# It's important to identify uninteresting nodes because
			# some uninteresting nodes that would never make it into the TOC or
			# otherwise be noticed actually can present with hard-coded duplicate
			# NTIIDs, which would cause us to fail.
			return

		ntiid = getattr(element, 'ntiid', None)
		if not ntiid:
			# If we hit something without an ntiid, it's not a section-level
			# element, it's a paragraph or something like it. Thus we collapse into
			# the parent. Obviously, we'll only look for AssessmentObjects inside of here
			element_index = index
		else:
			assert ntiid not in index, ("NTIIDs must be unique", ntiid, index.keys())
			element_index = index[ntiid] = {}

			element_index['NTIID'] = ntiid
			element_index['filename'] = getattr(element, 'filename', None)
			if 	not element_index['filename'] and \
				getattr(element, 'filenameoverride', None):
				# FIXME: XXX: We are assuming the filename extension.
				# Why aren't we finding these at filename? See EclipseHelp.zpts for
				# comparison
				element_index['filename'] = \
						getattr(element, 'filenameoverride') + '.html'
			element_index['href'] = getattr(element, 'url', element_index['filename'])

		__traceback_info__ = element_index
		assessment_objects = element_index.setdefault('AssessmentItems', {})

		for child in element.childNodes:
			ass_obj = getattr(child, 'assessment_object', None)
			if callable(ass_obj):
				int_obj = ass_obj()
				# Verify that we can round-trip this object
				self._ensure_roundtrips(int_obj, provenance=child)
				ext_obj = self._to_external_object(int_obj)
				assessment_objects[child.ntiid] = ext_obj
				signatures[child.ntiid] = self._signature(ext_obj)
				# assessment_objects are leafs, never have children to worry about
			elif child.hasChildNodes():  # Recurse for children if needed
				if getattr(child, 'ntiid', None):
					# we have a child with an NTIID; make sure we have a
					# container for it
					containing_index = element_index.setdefault('Items', {})
				else:
					# an unnamed thing; wrap it up with us; should only
					# have AssessmentItems
					containing_index = element_index
				self._build_index(child, containing_index, signatures)

	def _ensure_roundtrips(self, assm_obj, provenance=None):
		# No need to go into its children, like parts.
		ext_obj = self._to_external_object(assm_obj)
		__traceback_info__ = provenance, assm_obj, ext_obj

		# Use the class of the object returned as a factory.
		raw_int_obj = type(assm_obj)()
		update_from_external_object(raw_int_obj, ext_obj, require_updater=True,
									notify=False)

		# Also be sure factories can be found
		factory = find_factory_for(self._to_external_object(assm_obj))
		assert factory is not None
		# The ext_obj was mutated by the internalization process,
		# so we need to externalize again. Or run a deep copy (?)

	def _signature(self, data):
		return signature(data)

	def _is_uninteresting(self, element):
		"""
		Uninteresting elements do not get an entry in the index. These are
		elements that have no children and no assessment items of their own.
		"""

		cache_attr = '@assessment_extractor_uninteresting'
		if getattr(element, cache_attr, None) is not None:
			return getattr(element, cache_attr)

		boring = False
		if callable(getattr(element, 'assessment_object', None)):
			boring = False
		elif not element.hasChildNodes():
			boring = True
		elif all((self._is_uninteresting(x) for x in element.childNodes)):
			boring = True

		try:
			setattr(element, cache_attr, boring)
		except AttributeError:
			pass
		return boring
