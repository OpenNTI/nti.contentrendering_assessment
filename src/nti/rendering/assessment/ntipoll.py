#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six
from six import text_type

from zope import schema
from zope import interface
from zope.cachedescriptors.method import cachedIn
from zope.cachedescriptors.property import readproperty

from persistent.list import PersistentList

from plasTeX import Base
from plasTeX.Base import Crossref
from plasTeX.Renderers import render_children

from nti.contentrendering.plastexids import NTIIDMixin
from nti.contentrendering.interfaces import IEmbeddedContainer

from nti.assessment.poll import QPoll
from nti.assessment.poll import QSurvey

from nti.assessment.interfaces import IQPoll
from nti.assessment.interfaces import IQSurvey

from nti.assessment.interfaces import NTIID_TYPE
from nti.assessment.interfaces import SURVEY_MIME_TYPE

from .ntibase import _LocalContentMixin

class napollname(Base.Command):
	unicode = ''

class nasurveyname(Base.Command):
	unicode = ''

class napoll(_LocalContentMixin, Base.Environment, NTIIDMixin):
	args = ''

	blockType = True

	counter = 'napoll'

	forcePars = False

	_ntiid_type = NTIID_TYPE

	_ntiid_suffix = 'naq.'
	_ntiid_title_attr_name = 'ref'
	_ntiid_allow_missing_title = True
	_ntiid_cache_map_name = '_napoll_ntiid_map'

	def invoke( self, tex ):
		res = super(napoll, self).invoke(tex)
		return res

	@property
	def _ntiid_get_local_part(self):
		result = self.attributes.get( "pollnum" )
		if not result:
			result = super(napoll, self)._ntiid_get_local_part
		return result

	def _asm_videos(self):
		return ''.join(())

	def _asm_poll_parts(self):
		
		def _filter(x):
			result = hasattr(x, 'tagName') and x.tagName.startswith('naq') and \
					 x.tagName.endswith('part') and hasattr(x, 'assessment_object')
			if result:
				x.gradable = False # polls are not gradable
			return result

		to_iter = (x for x in self.allChildNodes if _filter(x))
		return [x.assessment_object() for x in to_iter]

	def _createPoll(self):
		result = QPoll(content=self._asm_local_content,
					   parts=self._asm_question_parts())
		return result

	@cachedIn('_v_assessment_object')
	def assessment_object(self):
		result = self._createPoll()
		errors = schema.getValidationErrors(IQPoll, result)
		if errors: # pragma: no cover
			raise errors[0][1]
		result.ntiid = self.ntiid # copy the id
		return result

class napollref(Crossref.ref):
	pass

@interface.implementer(IEmbeddedContainer)
class nasurvey(Base.List, NTIIDMixin):
	r"""
	Question sets are a list of questions that should be submitted
	together. For authoring, questions are included in a question
	set by reference, and a question set can be composed of any
	other labeled questions found within the same processing unit.

	Example::

		\begin{napoll}
			\label{poll}
			...
		\end{napoll}

		\begin{nasurvey}<My Title>
			\label{survey}
			\napollref{poll}
		\end{nasurvey}
	"""

	args = "[options:dict:str] <title:str:source>"

	# Only classes with counters can be labeled, and \label sets the
	# id property, which in turn is used as part of the 
	# NTIID (when no NTIID is set explicitly)
	counter = 'nasurvey'

	_ntiid_type = NTIID_TYPE
	_ntiid_suffix = 'naq.survey.'
	_ntiid_title_attr_name = 'ref'
	_ntiid_allow_missing_title = True
	_ntiid_cache_map_name = '_nasurvey_ntiid_map'

	mimeType = SURVEY_MIME_TYPE
	
	def create_survey(self, questions, title, **kwargs):
		result = QSurvey(questions=questions, title=title)
		return result
	
	def validate_survey(self, survey):
		errors = schema.getValidationErrors(IQSurvey, survey)
		if errors: # pragma: no cover
			raise errors[0][1]
		return survey
	
	@cachedIn('_v_assessment_object')
	def assessment_object(self):
		questions = [qref.idref['label'].assessment_object()
					 for qref in self.getElementsByTagName('napollref')]
		questions = PersistentList( questions )

		# Note that we may not actually have a renderer, depending on when
		# in our lifetime this is called (the renderer object mixin is deprecated
		# anyway)
		# If the title is ours, we're guaranteed it's a string. It's only in the
		# weird legacy code path that tries to inherit a title from some arbitrary
		# parent that it may not be a string
		if getattr(self, 'renderer', None) and not isinstance(self.title, six.string_types):
			title = text_type(''.join(render_children(getattr(self, 'renderer'),
													  self.title)))
		else:
			title = text_type(getattr(self.title, 'source', self.title))

		title = title.strip() or None

		result = self.create_survey(questions=questions, title=title)
		self.validate_survey(result)
		result.ntiid = self.ntiid # copy the id
		return result

	@readproperty
	def question_count(self):
		return unicode(len(self.getElementsByTagName('napollref')))

	@readproperty
	def title(self):
		r"""
		Provide an abstraction of the two ways to get a question set's title
		"""
		title = self.attributes.get('title') or None
		if title is None:
			title_el = self.parentNode
			while not hasattr(title_el, 'title'):
				title_el = title_el.parentNode
			title = title_el.title
		assert title is not None
		return title

class nasurveyref(Crossref.ref):
	"""
	A reference to the label of a survey.
	"""

	@readproperty
	def survey(self):
		return self.idref['label']
