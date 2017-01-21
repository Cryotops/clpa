# coding: utf-8
from __future__ import unicode_literals, print_function, division
from unittest import TestCase

from pyclpa.base import get_clpa, CLPA


class Tests(TestCase):
    def setUp(self):
        self.clpa = get_clpa()
        self.clpa2 = CLPA(rules=dict(th='t'))

    def test_normalize(self):
        self.assertEqual(self.clpa.normalize('a \u01dd'), 'a \u0259')

    def test_check_sequence(self):
        tokens, sounds, errors = self.clpa.check_sequence(['t', 'e', 's', 't'])
        assert '?' not in tokens

        tokens, sounds, errors = self.clpa.check_sequence('t e s t')
        assert '?' not in tokens

        tokens, sounds, errors = self.clpa.check_sequence('t e th s t')
        assert tokens[2][1] == 'ʰ'

        tokens, sounds, errors = self.clpa.check_sequence('t X s t')
        assert tokens[1] == '?'

        tokens, sounds, errors = self.clpa.check_sequence('ˈt e s t')
        assert tokens[0][1] == 't'

        tokens, sounds, errors = self.clpa2.check_sequence('th e')
        assert tokens[0] == 't'

        tokens, sounds, errors = self.clpa.check_sequence('p h₂ t e r')
        assert ' '.join(tokens) == 'p ? t e r'

        tokens, sounds, errors = self.clpa.check_sequence('p h₂/ t e r')
        assert ' '.join(tokens) == 'p *h₂ t e r'
        self.assertEqual(sum(1 for s in sounds.values() if s.custom), 1)

        tokens, sounds, errors = self.clpa.check_sequence('p h₂/x t e r')
        assert ' '.join(tokens) == 'p x t e r'
        assert 'h₂/x' in sounds

        # test for bad custom characters
        tokens, sounds, errors = self.clpa.check_sequence('p / t e r')
        assert ' '.join(tokens) == 'p ? t e r'

    def test_find_token(self):
        from pyclpa.util import load_whitelist, load_alias

        def _find(token, **kw):
            for k in [
                    'whitelist', 'alias', 'explicit', 'patterns', 'rules', 'normalized']:
                kw.setdefault(k, {})
            kw.setdefault('delete', [])
            return CLPA(**kw)._find(token)[0]

        wl = load_whitelist()
        patterns = load_alias('patterns.tsv')

        self.assertIsNone(_find('t'))
        self.assertEqual(_find('t', whitelist=wl), 't')
        self.assertEqual(_find('t', whitelist=wl), 't')
        self.assertEqual(_find('th', whitelist=wl, alias={'h': 'ʰ'}), 'tʰ')
        self.assertEqual(_find('th', whitelist=wl, explicit={'th': 'x'}), 'x')

        with self.assertRaises(AssertionError):
            _find('th', whitelist=wl, explicit={'th': 'X'})

        self.assertEqual(_find('th', whitelist=wl, patterns=patterns), 'tʰ')
        self.assertEqual(_find('th', whitelist=wl, delete=['h']), 't')
        self.assertEqual(_find('x/t', whitelist=wl), 't')

    def test_segment2clpa(self):
        assert self.clpa.segment2clpa('t') == 'c118'
        assert self.clpa.segment2clpa("'t") == 'c118'
