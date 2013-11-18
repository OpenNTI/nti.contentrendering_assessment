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

from persistent import Persistent

from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage

from . import interfaces
from ._util import TrivialValuedMixin

@interface.implementer(interfaces.IQResponse)
class QResponse(Persistent):
	"""
	Base class for responses.
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
class QUploadedFile(NamedBlobFile):
	pass

@interface.implementer(interfaces.IQUploadedFile)
class QUploadedImageFile(NamedBlobImage):
	pass

@interface.implementer(interfaces.IQFileResponse)
class QFileResponse(TrivialValuedMixin, QResponse):
	"""
	An uploaded file response.
	"""
