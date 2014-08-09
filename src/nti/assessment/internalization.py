#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import six
import collections

from zope import interface
from zope import component

from nti.externalization.datastructures import InterfaceObjectIO
from nti.externalization.interfaces import IInternalObjectUpdater

from nti.externalization.internalization import find_factory_for
from nti.externalization.internalization import update_from_external_object

from .interfaces import IRegEx
from .interfaces import IWordEntry
from .interfaces import IQFillInTheBlankShortAnswerSolution

@interface.implementer(IInternalObjectUpdater)
@component.adapter(IWordEntry)
class _WordEntryUpdater(object):

    __slots__ = ('obj',)

    def __init__(self, obj):
        self.obj = obj

    def updateFromExternalObject(self, parsed, *args, **kwargs):
        if 'content' not in parsed or not parsed['content']:
            parsed['content'] = parsed['word']

        result = InterfaceObjectIO(self.obj, IWordEntry).updateFromExternalObject(parsed)
        return result

@interface.implementer(IInternalObjectUpdater)
@component.adapter(IQFillInTheBlankShortAnswerSolution)
class _QFillInTheBlankWithWordBankSolutionUpdater(object):

    __slots__ = ('obj',)

    def __init__(self, obj):
        self.obj = obj

    def updateFromExternalObject(self, parsed, *args, **kwargs):
        value = parsed.get('value', {})
        for key in value.keys():
            regex = value.get(key)
            if isinstance(regex, six.string_types):
                regex = IRegEx(regex)
            elif isinstance(regex, collections.Mapping):
                ext_obj = regex
                regex = find_factory_for(ext_obj)()
                update_from_external_object(regex, ext_obj)
            value[key] = regex
            
        result = InterfaceObjectIO(
                    self.obj,
                    IQFillInTheBlankShortAnswerSolution).updateFromExternalObject(parsed)
        return result
