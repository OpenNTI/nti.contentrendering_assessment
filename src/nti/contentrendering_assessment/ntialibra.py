#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import re
import six

from zope.cachedescriptors.property import readproperty

from plasTeX import Base

from plasTeX.Renderers import render_children

from nti.assessment.interfaces import IRegEx
from nti.assessment.interfaces import IWordBank
from nti.assessment.interfaces import IWordEntry
from nti.assessment.interfaces import IQFillInTheBlankShortAnswerPart
from nti.assessment.interfaces import IQFillInTheBlankWithWordBankPart
from nti.assessment.interfaces import IQFillInTheBlankShortAnswerSolution
from nti.assessment.interfaces import IQFillInTheBlankWithWordBankSolution

from nti.assessment.parts import QFillInTheBlankShortAnswerPart
from nti.assessment.parts import QFillInTheBlankWithWordBankPart

from nti.assessment.question import QFillInTheBlankWithWordBankQuestion

from nti.contentfragments.interfaces import HTMLContentFragment
from nti.contentfragments.interfaces import ILatexContentFragment

from nti.contentprocessing._compat import text_

from nti.contentrendering.plastexpackages._util import _is_renderable
from nti.contentrendering.plastexpackages._util import _htmlcontent_rendered_elements

from nti.contentrendering_assessment.ntibase import naqvalue
from nti.contentrendering_assessment.ntibase import _AbstractNAQPart
from nti.contentrendering_assessment.ntibase import _LocalContentMixin

from nti.contentrendering_assessment.ntiquestion import naquestion

logger = __import__('logging').getLogger(__name__)

# Parts


class _WordBankMixIn(object):

    def _parse_wordentries(self, naqwordbank):
        result = []
        for x in naqwordbank.getElementsByTagName('naqwordentry'):
            if 'wid' in x.attributes:
                # if no word attribute is specified then use the renderered
                # content
                content = x._asm_local_content or ''
                content = re.sub('\n', '', content.strip())
                word = (x.attributes['word'] or u'').strip() or content
                data = [x.attributes['wid'],
                        word,
                        x.attributes.get('lang'),
                        content]
                we = IWordEntry(data)
                result.append(we)
        return result

    def _asm_entries(self):
        raise NotImplementedError()

    def _asm_wordbank(self):
        result = None
        _naqwordbank, entries = self._asm_entries()
        if entries:
            result = IWordBank(entries)
            unique = _naqwordbank.attributes.get('unique', 'true') 
            result.unique = unique == 'true'
        return result


class naqfillintheblankwithwordbankpart(_WordBankMixIn, _AbstractNAQPart):
    """
    A fill in the blank with word bank part.

    \begin{naquestion}
            Arbitrary prefix content goes here.
            \begin{naqfillintheblankwithwordbankpart}
                    Arbitrary content for this part goes here.
                    \begin{naqinput}
                            empty fields \naqblankfield{1} \naqblankfield{2} \naqblankfield{3} go here
                    \end{naqinput}
                    \begin{naqwordbank}
                            \naqwordentry{0}{montuno}{es}
                            \naqwordentry{1}{tiene}{es}
                            \naqwordentry{2}{borinquen}{es}
                            \naqwordentry{3}{tierra}{es}
                            \naqwordentry{4}{alma}{es}
                    \end{naqwordbank}
                    \begin{naqpaireditems}
                            \naqpaireditem{1}{2}
                            \naqpaireditem{2}{1}
                            \naqpaireditem{3}{0}
                    \end{naqpaireditems}
                    \begin{naqsolexplanation}
                            Arbitrary content explaining how the correct solution is arrived at.
                    \end{naqsolexplanation}
            \end{naqfillintheblankwithwordbankpart}
    \end{naquestion}
    """

    part_factory = QFillInTheBlankWithWordBankPart
    part_interface = IQFillInTheBlankWithWordBankPart
    soln_interface = IQFillInTheBlankWithWordBankSolution

    def _asm_entries(self):
        _naqwordbank = self.getElementsByTagName('naqwordbank')
        if not _naqwordbank:
            result = None, ()
        else:
            _naqwordbank = _naqwordbank[0]
            entries = self._parse_wordentries(_naqwordbank)
            result = _naqwordbank, entries
        return result

    def _asm_object_kwargs(self):
        return {'wordbank': self._asm_wordbank(),
                'input': self._asm_input()}

    def _asm_input(self):
        input_el = self.getElementsByTagName('naqinput')[0]
        return HTMLContentFragment(input_el._asm_local_content.strip())

    def _asm_solutions(self):
        solutions = []
        solution_els = self.getElementsByTagName('naqsolution')
        for solution_el in solution_els:
            solution = self.soln_interface(solution_el.answer)
            weight = solution_el.attributes['weight']
            if weight is not None:
                solution.weight = weight
            solutions.append(solution)
        return solutions

    def digest(self, tokens):
        res = super(naqfillintheblankwithwordbankpart, self).digest(tokens)
        if self.macroMode != Base.Environment.MODE_END:
            input_els = self.getElementsByTagName('naqinput')
            assert len(input_els) == 1

            _naqblanks = input_els[0].getElementsByTagName('naqblankfield')
            assert len(input_els) >= 1

            _blankids = {x.attributes.get('id') for x in _naqblanks}
            _blankids.discard(None)
            assert len(_blankids) == len(_naqblanks)

            _naqwordbank = self.getElementsByTagName('naqwordbank')
            assert len(_naqwordbank) <= 1
            if _naqwordbank:
                _naqwordbank = _naqwordbank[0]
                _naqwordentries = _naqwordbank.getElementsByTagName('naqwordentry')
                assert len(_naqwordentries) > 0, \
                       "Must specified at least one word entry"
                for x in _naqwordentries:
                    word = x.attributes['word'] or x._asm_local_content
                    assert x.attributes['wid'] and word

            assert len(self.getElementsByTagName('naqsolutions')) == 0

            naqpaireditems = self.getElementsByTagName('naqpaireditems')
            assert len(naqpaireditems) == 1
            _naqpaireditems = naqpaireditems[0]
            _paireditems = _naqpaireditems.getElementsByTagName(
                'naqpaireditem')
            assert len(_paireditems) == len(_blankids)

            answer = {}
            _naqsolns = self.ownerDocument.createElement('naqsolutions')
            _naqsolns.macroMode = _naqsolns.MODE_BEGIN
            for _item in _paireditems:
                bid = _item.attributes['x']
                wid = _item.attributes['y']
                assert bid and isinstance(
                    bid, six.string_types) and bid in _blankids
                assert wid and isinstance(wid, six.string_types)
                answer[bid] = wid.split(',')
            _naqsoln = self.ownerDocument.createElement('naqsolution')
            _naqsoln.attributes['weight'] = 1.0
            _naqsoln.argSource = '[%s]' % _naqsoln.attributes['weight']
            _naqsoln.answer = answer
            _naqsolns.appendChild(_naqsoln)
            self.insertAfter(_naqsolns, _naqpaireditems)
        return res


class naqfillintheblankshortanswerpart(_AbstractNAQPart):
    """
    A fill in the blank short answer part (usually used as the sole part to a question).
    It must have a child listing the regex solutions.  Further the all
    solutions with a weight of 1:: are required to be submitted to receive credit for the
    question

    \begin{naquestion}
            Arbitrary prefix content goes here.
            \begin{naqfillintheblankshortanswerpart}
                    Arbitrary content for this part goes here \naqblankfield{001}[2] \naqblankfield{002}[2]
                    \begin{naqregexes}
                            \naqregex{001}{.*}  Everything.
                            \naqregex{002}{^1\$} Only 1.
                    \end{naqregexes}
                    \begin{naqsolexplanation}
                            Arbitrary content explaining how the correct solution is arrived at.
                    \end{naqsolexplanation}
            \end{naqfillintheblankshortanswerpart}
    \end{naquestion}
    """

    part_factory = QFillInTheBlankShortAnswerPart
    part_interface = IQFillInTheBlankShortAnswerPart
    soln_interface = IQFillInTheBlankShortAnswerSolution

    def _asm_object_kwargs(self):
        return {}

    def _asm_solutions(self):
        solutions = []
        solution_els = self.getElementsByTagName('naqsolution')
        for solution_el in solution_els:
            solution = self.soln_interface(solution_el.answer)
            weight = solution_el.attributes['weight']
            if weight is not None:
                solution.weight = weight
            solutions.append(solution)
        return solutions

    def digest(self, tokens):
        res = super(naqfillintheblankshortanswerpart, self).digest(tokens)
        if self.macroMode != Base.Environment.MODE_END:

            _naqblanks = self.getElementsByTagName('naqblankfield')
            assert len(_naqblanks) >= 1

            _blankids = {x.attributes.get('id') for x in _naqblanks}
            _blankids.discard(None)
            assert len(_blankids) == len(_naqblanks)

            _naqregexes = self.getElementsByTagName('naqregexes')
            assert len(_naqregexes) == 1

            _naqregexes = _naqregexes[0]
            _regentries = _naqregexes.getElementsByTagName('naqregex')
            assert len(_regentries) > 0, "Must specified at least one regex"

            assert len(_blankids) <= len(_regentries)
            assert len(self.getElementsByTagName('naqsolutions')) == 0

            answer = {}
            _naqsolns = self.ownerDocument.createElement('naqsolutions')
            _naqsolns.macroMode = _naqsolns.MODE_BEGIN
            for _naqmregex in _regentries:
                pid, pattern, solution = _naqmregex.attributes['pid'], \
                    _naqmregex.attributes['pattern'], \
                    _naqmregex._asm_local_content
                assert pattern and pid
                answer[pid] = IRegEx((pattern, solution or None))
            _naqsoln = self.ownerDocument.createElement('naqsolution')
            _naqsoln.answer = answer
            _naqsoln.attributes['weight'] = 1.0
            _naqsoln.argSource = '[%s]' % _naqsoln.attributes['weight']
            _naqsolns.appendChild(_naqsoln)
            self.insertAfter(_naqsolns, _naqregexes)
        return res


class naqregex(naqvalue):
    args = 'pid:str pattern:str:source'

    def invoke(self, tex):
        tok = super(naqregex, self).invoke(tex)
        return tok

    @readproperty
    def _asm_local_content(self):
        return text_(self.textContent).strip()

    def _after_render(self, rendered):
        self._asm_local_content = rendered


class naqregexes(Base.List):
    pass


class naqpaireditem(naqvalue):
    args = 'x:str y:str'


class naqpaireditems(Base.List):
    args = '[label:idref]'


class naqwordentry(naqvalue):
    args = 'wid:str word:str lang:str'


class naqblankfield(Base.Command):

    args = 'id:str [maxlength:int]'

    def digest(self, tokens):
        res = super(naqblankfield, self).digest(tokens)
        return res


class naqwordbank(Base.List):

    args = '[unique:str] [label:idref]'

    def invoke(self, tex):
        token = super(naqwordbank, self).invoke(tex)
        if      'unique' in self.attributes \
            and (self.attributes['unique'] or '').lower() == 'unique=false':
            self.attributes['unique'] = 'false'
        else:
            self.attributes['unique'] = 'true'
        return token


class naqwordbankref(Base.Crossref.ref):

    args = '[options:dict] label:idref'

    def digest(self, tokens):
        tok = super(naqwordbankref, self).digest(tokens)
        return tok


class naqregexref(Base.Crossref.ref):

    args = '[options:dict] label:idref'

    def digest(self, tokens):
        tok = super(naqregexref, self).digest(tokens)
        return tok


class naqinput(_LocalContentMixin, Base.Environment):

    @readproperty
    def _asm_local_content(self):
        if _is_renderable(self.renderer, self.childNodes):
            result = _htmlcontent_rendered_elements(self.renderer,
                                                    self.childNodes)
        else:
            result = ILatexContentFragment(text_(self.textContent).strip())
        return result


# Questions


def _remove_parts_after_render(self, _):
    # CS: Make sure we only render the children that do not contain any 'question' part,
    # since those will be rendereds when the part is so.
    def _check(node):
        def f(x): return isinstance(x, (_AbstractNAQPart,))
        found = any(map(f, node.childNodes)) or f(node)
        return not found
    # Each node in self.childNodes is a plasTeX.Base.TeX.Primitives.par
    # check its children to see if they contain any question 'part' objects.
    # do not include them in the asm_local_content
    selected = [n for n in self.childNodes if _check(n)]
    output = render_children(self.renderer, selected)
    output = HTMLContentFragment(u''.join(output).strip())
    return output


class naquestionfillintheblankwordbank(_WordBankMixIn, naquestion):

    def _get_parent(self, element):
        try:
            parent = element.parentNode
            while (parent is not None and not isinstance(parent, _WordBankMixIn)):
                parent = parent.parentNode
            result = parent
        except AttributeError:
            result = None
        return result

    def _asm_entries(self):
        _naqwordbank = self.getElementsByTagName('naqwordbank')
        if not _naqwordbank or self._get_parent(_naqwordbank[0]) != self:
            result = None, ()
        else:
            _naqwordbank = _naqwordbank[0]
            entries = self._parse_wordentries(_naqwordbank)
            result = _naqwordbank, entries
        return result

    def _after_render(self, rendered):
        self._asm_local_content = _remove_parts_after_render(self, rendered)

    def _createQuestion(self):
        wordbank = self._asm_wordbank()
        result = QFillInTheBlankWithWordBankQuestion(content=self._asm_local_content,
                                                     parts=self._asm_question_parts(),
                                                     tags=self._asm_tags(),
                                                     wordbank=wordbank)
        return result
