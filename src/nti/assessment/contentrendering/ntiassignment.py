#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import schema
from zope import interface
from zope.cachedescriptors.method import cachedIn
from zope.cachedescriptors.property import readproperty

from plasTeX import Base
from plasTeX.Base import Crossref

from paste.deploy.converters import asbool

from nti.contentrendering import plastexids
from nti.contentrendering.interfaces import IEmbeddedContainer

from nti.externalization.datetime import datetime_from_string

from ..assignment import QAssignment
from ..assignment import QAssignmentPart

from ..interfaces import NTIID_TYPE
from ..interfaces import IQAssignment

from .ntibase import _LocalContentMixin

class naassignmentpart(_LocalContentMixin,
					   Base.Environment):
	r"""
	One part of an assignment. These are always nested inside
	an :class:`naassignment` environment.

	Example::
		\begin{naquestionset}
			\label{set}
			\naquestionref{question}
		\end{naquestionset}

		\begin{naasignmentpart}[auto_grade=true]{set}
			Local content
		\end{naassignmentpart}

	"""

	args = "[options:dict:str] <title:str:source> question_set:idref"

	@cachedIn('_v_assessment_object')
	def assessment_object(self):
		question_set = self.idref['question_set'].assessment_object()
		auto_grade = self.attributes.get('options',{}).get('auto_grade')
		return QAssignmentPart(	content=self._asm_local_content,
								question_set=question_set,
								auto_grade=asbool(auto_grade),
								title=self.attributes.get('title'))

class naassignmentname(Base.Command):
	unicode = ''

@interface.implementer(IEmbeddedContainer)
class naassignment(_LocalContentMixin,
				   Base.Environment,
				   plastexids.NTIIDMixin):
	r"""
	Assignments specify some options such as availability dates,
	some local content, and finish up nesting the parts
	of the assignment as ``naassignmentpart`` elements.

	Example::

		\begin{naassignment}[not_before_date=2014-01-13,category=homework,public=true]<Homework>
			\label{assignment}
			Some introductory content.

			\begin{naasignmentpart}[auto_grade=true]{set}<Easy Part>
				Local content
			\end{naassignmentpart}
		\end{naquestionset}

	"""

	args = "[options:dict:str] <title:str:source>"

	# Only classes with counters can be labeled, and \label sets the
	# id property, which in turn is used as part of the NTIID (when no
	# NTIID is set explicitly)
	counter = 'naassignment'

	_ntiid_suffix = 'naq.asg.'
	_ntiid_type = NTIID_TYPE
	_ntiid_title_attr_name = 'ref' # Use our counter to generate IDs if no ID is given
	_ntiid_allow_missing_title = True
	_ntiid_cache_map_name = '_naassignment_ntiid_map'
	
	#: From IEmbeddedContainer
	mimeType = u'application/vnd.nextthought.assessment.assignment'
	
	@cachedIn('_v_assessment_object')
	def assessment_object(self):
		# FIXME: We want these to be relative, not absolute, so they
		# can be made absolute based on when the course begins.
		# How to represent that? Probably need some schema transformation
		# step in nti.externalization? Or some auixilliary data fields?
		options = self.attributes.get('options') or ()
		def _parse(key, default_time):
			if key in options:
				val = options[key]
				if 'T' not in val:
					val += default_time

				# Now parse it, assuming that any missing timezone should be treated
				# as local timezone
				dt = datetime_from_string(
							val,
							assume_local=True,
							local_tzname=self.ownerDocument.userdata.get('document_timezone_name'))
				return dt

		# If they give no timestamp, make it midnight
		not_before = _parse('not_before_date', 'T00:00')
		# For after, if they gave us no time, make it just before
		# midnight. Together, this has the effect of intuitively defining
		# the range of dates as "the first instant of before to the last minute of after"
		not_after = _parse('not_after_date', 'T23:59')

		# Public/ForCredit.
		# It's opt-in for authoring and opt-out for code
		is_non_public = True
		if 'public' in options and asbool(options['public']):
			is_non_public = False

		parts = [part.assessment_object() for part in
				 self.getElementsByTagName('naassignmentpart')]

		result = QAssignment(content=self._asm_local_content,
							 available_for_submission_beginning=not_before,
							 available_for_submission_ending=not_after,
							 parts=parts,
							 title=self.attributes.get('title'),
							 is_non_public=is_non_public)
		if 'category' in options:
			result.category_name = \
				IQAssignment['category_name'].fromUnicode( options['category'] )

		errors = schema.getValidationErrors(IQAssignment, result )
		if errors: # pragma: no cover
			raise errors[0][1]

		result.ntiid = self.ntiid
		return result

	@readproperty
	def containerId(self):
		parentNode = self.parentNode
		while (not hasattr(parentNode, 'filename')) or (parentNode.filename is None):
			parentNode = parentNode.parentNode
		return parentNode.ntiid

class naassignmentref(Crossref.ref):
	r"""
	A reference to the label of a question set.
	"""

	@readproperty
	def assignment(self):
		return self.idref['label']
