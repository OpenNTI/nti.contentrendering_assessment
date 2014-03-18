#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import is_not
from hamcrest import contains
from hamcrest import equal_to
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_property

import unittest

from nti.assessment.wordbank import WordBank
from nti.assessment.wordbank import WordEntry
from nti.assessment import interfaces as asm_interfaces

from nti.assessment.tests import SharedConfiguringTestLayer

from nti.testing.matchers import verifiably_provides

class TestWordBank(unittest.TestCase):

	layer = SharedConfiguringTestLayer

	def test_entry(self):
		we = WordEntry(id='1', word='bankai')
		assert_that(we, verifiably_provides(asm_interfaces.IWordEntry))
		assert_that(we, has_property('lang', is_('en')))

	def test_bank(self):
		entries = {'1': WordEntry(id='1', word='bankai'), 
				   '2': WordEntry(id='2', word='shikai')}
		bank = WordBank(entries=entries, unique=True)
		assert_that(bank, verifiably_provides(asm_interfaces.IWordBank))
		assert_that(bank, has_length(2))
		assert_that(bank.contains_id('1'), is_(True))
		assert_that(bank.contains_id('2'), is_(True))
		assert_that(bank.contains_id('2x'), is_(False))
		assert_that(bank.contains_word('shikai'), is_(True))
		assert_that(bank.contains_word('BANKAI'), is_(True))
		assert_that(bank.contains_word('foo'), is_(False))

		for x in bank:
			assert_that(x, has_property('__parent__', is_(bank)))

		assert_that(bank.words, has_length(2))
		assert_that(bank.words, contains('bankai', 'shikai'))

		w1 = bank.get('1')
		assert_that(w1, has_property('id', is_('1')))
		w2 = bank.get('2')
		assert_that(w2, has_property('id', is_('2')))
		assert_that(w1, is_not(equal_to(w2)))
