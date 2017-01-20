# coding: utf-8
from __future__ import unicode_literals, print_function, division
from unittest import TestCase

from pyclpa.base import get_clpa, CLPA


class Tests(TestCase):
    def setUp(self):
        self.clpa = get_clpa()
        self.clpa2 = CLPA(rules=dict(th='t'))

    def test_check_sequence(self):
        test1 = self.clpa.check_sequence(['t', 'e', 's', 't'])
        assert '?' not in test1[0]
        test2 = self.clpa.check_sequence('t e s t')
        assert '?' not in test2[0]
        test3 = self.clpa.check_sequence('t e th s t')
        assert test3[0][2][1] == 'ʰ'
        test4 = self.clpa.check_sequence('t X s t')
        assert test4[0][1] == '?'
        test5 = self.clpa.check_sequence('ˈt e s t')
        assert test5[0][0][1] == 't'
        test6 = self.clpa2.check_sequence('th e')
        assert test6[0][0] == 't'
        test7 = self.clpa.check_sequence('p h₂ t e r')
        assert ' '.join(test7[0]) == 'p ? t e r'
        test8 = self.clpa.check_sequence('p h₂/ t e r')
        assert ' '.join(test8[0]) == 'p *h₂ t e r'
        assert test8[2]['custom'] == 1
        test9 = self.clpa.check_sequence('p h₂/x t e r')
        assert ' '.join(test9[0]) == 'p x t e r'
        assert 'h₂/x' in test9[1]

    def test_segment2clpa(self):
        assert self.clpa.segment2clpa('t') == 'c118'
        assert self.clpa.segment2clpa("'t") == 'c118'
