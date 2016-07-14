# coding: utf-8
from __future__ import unicode_literals, print_function, division

from pyclpa.util import *
from pyclpa.tests.util import TestCase

from nose.tools import assert_raises


class Tests(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        self.wlp = self.data_path('KSL.tsv')
        self.clpa = load_CLPA()
        self.whitelist = load_whitelist()
        self.alias = load_alias('alias.tsv')
        self.patterns = load_alias('patterns.tsv')
        self.explicit = load_alias('explicit.tsv')
        self.delete = ['\u0361', '\u035c', '\u0301']

    def test_load_wordlist(self):
        wordlist = load_wordlist(self.wlp)
        assert 'TOKENS' in wordlist[0]
        assert len(wordlist) == 1400

    def test_local_path(self):
        assert local_path('bla').name == 'bla'
    
    def test_write_CLPA(self):
        write_CLPA(self.clpa, self.tmp_path('bla'))

    def test_load_whitelist(self):
        whitelist = load_whitelist()
        assert whitelist['t']['ID'] == 'c118'
    
    def test_load_alias(self):
        alias = load_alias(local_path('alias.tsv'))
        assert alias['ɡ'] == 'g'

    def test_check_string(self):
        mystring = 'm a tt i s'
        check = check_string(mystring, self.whitelist)
        assert check[2] == '?'

    def test_find_token(self):
        assert not find_token('t', {}, {}, {}, {}, [])
        assert find_token('t', self.whitelist, {}, {}, {}, []) == 't'
        assert find_token('th', self.whitelist, {'h':'ʰ'}, {}, {}, []) == 'tʰ'
        assert find_token('th', self.whitelist, {}, {'th' : 'x'}, {}, []) == 'x'
        assert_raises(ValueError, find_token, 'th', self.whitelist, {}, 
                {'th':'X'}, {}, [])
        assert find_token('th', self.whitelist, {}, {}, self.patterns, []) == 'tʰ'
        assert find_token('th', self.whitelist, {}, {}, {}, ['h']) == 't'

    def test_write_wordlist(self):
        wl = load_wordlist(self.wlp)
        write_wordlist(self.tmp_path('xxx'), wl)
        wl2 = load_wordlist(self.tmp_path('xxx'))
        self.assertEqual(wl, wl2)

    def test_check_wordlist(self):
        sounds, errors, wordlist = check_wordlist(self.wlp)
        assert errors['convertable'] == 13
        assert errors['non-convertable'] == 4
        assert sounds['t']['frequency'] == 223

        sounds, errors, wordlist = check_wordlist(self.wlp, rules=self.data_path('KSL.rules'))
        assert errors['non-convertable'] == 3
