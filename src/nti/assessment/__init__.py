#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import unicode_literals, print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from . import interfaces

def grade_one_response(questionResponse, possible_answers):
	"""
	:param questionResponse: The string to evaluate. It may be in latex notation
		or openmath XML notation, or plain text. We may edit the response
		to get something parseable.
	:param list possible_answers: A sequence of possible answers to compare
		`questionResponse` with.
	"""

	answers = [interfaces.IQLatexSymbolicMathSolution(t) for t in possible_answers]

	match = False
	for answer in answers:
		match = answer.grade(questionResponse)
		if match:
			return match

	return False

def assess(quiz, responses):
	result = {}
	for questionId, questionResponse in responses.iteritems():
		result[questionId] = \
			grade_one_response(questionResponse, quiz[questionId].answers)
	return result

def grader_for_solution_and_response(part, solution, response):
	grader = component.queryMultiAdapter((part, solution, response),
										  part.grader_interface,
										  name=part.grader_name)
	return grader() if grader is not None else None
grader = grader_for_solution_and_response # alias BWC

def grader_for_response(part, response):
	for solution in part.solutions or ():
		grader = grader_for_solution_and_response(part, solution, response)
		if grader is not None:
			return grader
	return None

		