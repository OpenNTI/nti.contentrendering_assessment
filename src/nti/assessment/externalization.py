#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Externalization for assessment objects.

$Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface
from zope import component

from zope.file.upload import nameFinder

from nti.dataserver import links
from nti.dataserver import interfaces as nti_interfaces

from nti.externalization import interfaces as ext_interfaces
from nti.externalization.externalization import to_external_object
from nti.externalization.externalization import to_external_ntiid_oid
from nti.externalization.datastructures import AbstractDynamicObjectIO
from nti.externalization.singleton import SingletonDecorator

from nti.utils.schema import DataURI
from nti.utils.dataurl import DataURL

from . import interfaces
from .response import QUploadedFile
from .response import QUploadedImageFile

@interface.implementer(ext_interfaces.IInternalObjectIO)
class _AssessmentInternalObjectIOBase(object):
	"Base class to customize object IO. See zcml."

	@classmethod
	def _ap_compute_external_class_name_from_interface_and_instance(cls, iface, impl):
		# Strip off 'IQ' if it's not 'IQuestionXYZ'
		return iface.__name__[2:] if not iface.__name__.startswith('IQuestion') else iface.__name__[1:]


	@classmethod
	def _ap_compute_external_class_name_from_concrete_class(cls, a_type):
		k = a_type.__name__
		ext_class_name = k[1:] if not k.startswith('Question') else k
		return ext_class_name


@interface.implementer(ext_interfaces.IExternalObjectDecorator)
@component.adapter(interfaces.IQAssessedQuestion)
class _QAssessedQuestionExplanationSolutionAdder(object):
	"""
	Because we don't generally want to provide solutions and explanations
	until after a student has submitted, we place them on the assessed object.

	.. note:: In the future this may be registered/unregistered on a site
		by site basis (where a Course is a site) so that instructor preferences
		on whether or not to provide solutions can be respected.
	"""

	__metaclass__ = SingletonDecorator

	def decorateExternalObject( self, context, mapping ):
		question_id = context.questionId
		question = component.queryUtility( interfaces.IQuestion,
										   name=question_id )
		if question is None:
			# In case of old answers to questions
			# that no longer exist mostly
			return

		for question_part, external_part in zip(question.parts, mapping['parts']):
			external_part['solutions'] = to_external_object(question_part.solutions)
			external_part['explanation'] = to_external_object(question_part.explanation)

@interface.implementer(ext_interfaces.IExternalObjectDecorator)
class _QAssessmentObjectIContainedAdder(object):
	"""
	When an assignment or question set comes from a content package
	and thus has a __parent__ that has an NTIID, make that NTIID
	available as the ``containerId``, just like an
	:class:`nti.dataserver.interfaces.IContained` object. This is
	meant to help provide contextual information for the UI because
	sometimes these objects (assignments especially) are requested
	in bulk without any other context.

	Obviously this only works if assignments are written in the TeX
	files at a relevant location (within the section aka lesson they
	are about)---if they are lumped together at the end, this does no
	good.

	This is perhaps a temporary measure as assessments will be moving
	into course definitions.
	"""

	__metaclass__ = SingletonDecorator

	def decorateExternalObject( self, context, mapping ):
		if 'containerId' not in mapping:
			containerId = getattr( context.__parent__, 'ntiid', None )
			mapping['containerId'] = containerId


##
# File uploads
# TODO: This can probably be generalized.
# We do want to have specific interfaces for files
# submitted for assessment reasons.
##

@component.adapter(interfaces.IQUploadedFile)
class _QUploadedFileObjectIO(AbstractDynamicObjectIO):

	def __init__( self, ext_self ):
		super(_QUploadedFileObjectIO,self).__init__()
		self._ext_self = ext_self

	def _ext_replacement(self):
		return self._ext_self

	def _ext_all_possible_keys(self):
		return ()

	# For symmetry with the other response types,
	# we accept either 'url' or 'value'

	def updateFromExternalObject( self, parsed, *args, **kwargs ):
		updated = super(_QUploadedFileObjectIO,self).updateFromExternalObject( parsed, *args, **kwargs )
		ext_self = self._ext_replacement()
		url = parsed.get( 'url', parsed.get('value') )
		if url:
			data_url = DataURI(__name__='url').fromUnicode( url )
			ext_self.contentType = data_url.mimeType
			ext_self.data = data_url.data
			updated = True
		if 'filename' in parsed:
			ext_self.filename = parsed['filename']
			# some times we get full paths
			name = nameFinder( ext_self )
			if name:
				ext_self.filename = name
			updated = True

		return updated

	def toExternalObject( self, mergeFrom=None ):
		ext_dict = super(_QUploadedFileObjectIO,self).toExternalObject()

		# TODO: View name. Coupled to the app layer. And this is now in three
		# places.
		# It's not quite possible to fully traverse to the file sometimes
		# (TODO: verify this in this case)
		# so we go directly to the file address
		the_file = self._ext_replacement()
		ext_dict['FileMimeType'] = the_file.mimeType or None
		ext_dict['filename'] = the_file.filename or None
		# We should probably register an externalizer on
		# i
		target = to_external_ntiid_oid( the_file, add_to_connection=True )
		if target:
			link = links.Link( target=target,
							   target_mime_type=the_file.mimeType,
							   elements=('@@download',),
							   rel="data" )
			interface.alsoProvides( link, nti_interfaces.ILinkExternalHrefOnly )
			ext_dict['url'] = to_external_object( link )
		else:
			ext_dict['url'] = None

		ext_dict['value'] = ext_dict['url']
		return ext_dict

def _QUploadedFileFactory(ext_obj):
	factory = QUploadedFile
	url = ext_obj.get( 'url', ext_obj.get('value') )
	if url and url.startswith(b'data:'):
		ext_obj['url'] = DataURL(url)
		ext_obj.pop('value', None)
		if ext_obj['url'].mimeType.startswith('image/'):
			factory = QUploadedImageFile
	return factory
