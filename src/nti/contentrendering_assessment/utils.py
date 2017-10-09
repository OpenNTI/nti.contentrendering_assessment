#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from nti.contentrendering_assessment.ntibase import aspveint

from nti.externalization.datetime import datetime_from_string

logger = __import__('logging').getLogger(__name__)


def secs_converter(s):
    if s.endswith('m') or s.endswith('M'):
        s = s[:-1]
        result = aspveint(s) * 60
    elif s.endswith('h') or s.endswith('H'):
        s = s[:-1]
        result = aspveint(s) * 3600
    else:
        result = aspveint(s)
    return result


def parse_assessment_datetime(key, options, default_time, local_tzname=None):
    if key in options:
        val = options[key]
        if 'T' not in val:
            val += default_time
        # Now parse it, assuming that any missing timezone should be treated
        # as local timezone
        dt = datetime_from_string(val, assume_local=True, 
                                  local_tzname=local_tzname)
        return dt
    return None
