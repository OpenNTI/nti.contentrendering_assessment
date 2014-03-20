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
from hamcrest import has_entries
from hamcrest import has_property

import unittest

from nti.assessment.wordbank import WordBank
from nti.assessment.wordbank import WordEntry
from nti.assessment import interfaces as asm_interfaces

from nti.externalization.tests import externalizes

from nti.testing.matchers import verifiably_provides

import nti.testing.base

# nose module-level setup
setUpModule = lambda: nti.testing.base.module_setup(set_up_packages=(__name__,))
tearDownModule = nti.testing.base.module_teardown

class TestWordBank(unittest.TestCase):

	def test_entry(self):
		we = WordEntry(wid='1', word='bankai')
		assert_that(we, verifiably_provides(asm_interfaces.IWordEntry))
		assert_that(we, has_property('lang', is_('en')))
		assert_that(we, externalizes(has_entries('Class', 'WordEntry',
												 'word', 'bankai',
												 'wid', '1',
												 'lang', 'en')))

	def test_bank(self):
		entries = {'1': WordEntry(wid='1', word='bankai'),
				   '2': WordEntry(wid='2', word='shikai')}
		bank = WordBank(entries=entries, unique=True)
		assert_that(bank, verifiably_provides(asm_interfaces.IWordBank))
		assert_that(bank, has_length(2))
		assert_that('1' in bank, is_(True))
		assert_that('2x' in bank, is_(False))
		assert_that(bank.contains_id('2'), is_(True))
		assert_that(bank.contains_word('shikai'), is_(True))
		assert_that(bank.contains_word('BANKAI'), is_(True))
		assert_that(bank.contains_word('foo'), is_(False))

		assert_that(bank.words, has_length(2))
		assert_that(bank.words, contains('bankai', 'shikai'))

		w1 = bank.get('1')
		assert_that(w1, has_property('wid', is_('1')))
		w2 = bank.get('2')
		assert_that(w2, has_property('wid', is_('2')))
		assert_that(w1, is_not(equal_to(w2)))

		assert_that(bank, externalizes(has_entries('Class', 'WordBank',
												   'unique', True,
												   'entries', has_length(2))))

		bank.append(WordEntry(wid='3', word='zaraki'))
		assert_that(bank.words, has_length(3))