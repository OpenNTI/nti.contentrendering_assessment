#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
$Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from six import text_type
from six import string_types

from zope import interface
from zope.container.contained import Contained

from persistent import Persistent

from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from nti.dataserver.datastructures import PersistentCreatedModDateTrackingObject

from . import interfaces
from ._util import TrivialValuedMixin

@interface.implementer(interfaces.IQResponse)
class QResponse(Persistent,
				Contained):
	"""
	Base class for responses.

	In general, responses are not expected to be created
	directly by clients. Subclasses may change this, however.
	"""
	__external_can_create__ = False

@interface.implementer(interfaces.IQTextResponse)
class QTextResponse(TrivialValuedMixin,QResponse):
	"""
	A text response.
	"""

	def __init__( self, *args, **kwargs ):
		super(QTextResponse,self).__init__( *args, **kwargs )
		if self.value is not None and not isinstance(self.value, string_types):
			# Convert e.g., numbers, to text values
			self.value = text_type(self.value)
		if isinstance(self.value, bytes): # pragma: no cover
			# Decode incoming byte strings to text
			self.value = text_type(self.value, 'utf-8')

@interface.implementer(interfaces.IQListResponse)
class QListResponse(TrivialValuedMixin,QResponse):
	"""
	A list response.
	"""

@interface.implementer(interfaces.IQDictResponse)
class QDictResponse(TrivialValuedMixin,QResponse):
	"""
	A dictionary response.
	"""

@interface.implementer(interfaces.IQUploadedFile)
class QUploadedFile(PersistentCreatedModDateTrackingObject, # Order matters
					NamedBlobFile):
	pass

@interface.implementer(interfaces.IQUploadedFile)
class QUploadedImageFile(PersistentCreatedModDateTrackingObject, # Order matters
						 NamedBlobImage):
	pass

@interface.implementer(interfaces.IQFileResponse)
class QFileResponse(TrivialValuedMixin, QResponse):
	"""
	An uploaded file response.
	"""

from nti.dataserver.contenttypes.note import BodyFieldProperty
from nti.utils.schema import AdaptingFieldProperty

@interface.implementer(interfaces.IQModeledContentResponse)
class QModeledContentResponse(TrivialValuedMixin,
							  QResponse):
	"""
	A modeled content response, intended to be created
	from external objects.
	"""

	__external_can_create__ = True

	value = BodyFieldProperty(interfaces.IQModeledContentResponse['value'])
	title = AdaptingFieldProperty(interfaces.IQModeledContentResponse['title'])
