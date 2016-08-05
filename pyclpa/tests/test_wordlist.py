# coding: utf-8
from __future__ import unicode_literals, print_function, division

from pyclpa.tests.util import TestCase
from pyclpa.wordlist import Wordlist


class Tests(TestCase):
    def _make_one(self, path=None):
        return Wordlist.from_file(path or self.data_path('KSL.tsv'))

    def test_load_wordlist(self):
        wl = self._make_one()
        self.assertIn('TOKENS', wl[0])
        self.assertEqual(len(wl), 1400)

    def test_write_wordlist(self):
        wl = self._make_one()
        out = self.tmp_path('xxx')
        wl.write(out)
        wl2 = self._make_one(out)
        self.assertEqual(wl, wl2)

    def test_check_wordlist(self):
        wl = self._make_one()
        sounds, errors = wl.check()
        assert errors['convertable'] == 13
        assert errors['non-convertable'] == 4
        assert sounds['t']['frequency'] == 223

        sounds, errors = wl.check(rules=self.data_path('KSL.rules'))
        assert errors['non-convertable'] == 3
