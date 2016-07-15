# coding: utf-8
from __future__ import unicode_literals, print_function, division

from pyclpa.tests.util import TestCase


class Tests(TestCase):
    def test_local_path(self):
        from pyclpa.util import local_path

        assert local_path('bla').name == 'bla'

    def test_write_CLPA(self):
        from pyclpa.util import write_CLPA, load_CLPA

        write_CLPA(load_CLPA(), self.tmp_path('bla'))

    def test_load_whitelist(self):
        from pyclpa.util import load_whitelist

        assert load_whitelist()['t']['ID'] == 'c118'

    def test_load_alias(self):
        from pyclpa.util import local_path, load_alias

        assert load_alias(local_path('alias.tsv'))['ɡ'] == 'g'

    def test_check_string(self):
        from pyclpa.util import check_string, load_whitelist

        check = check_string('m a tt i s', load_whitelist())
        assert check[2] == '?'

    def test_find_token(self):
        from pyclpa.util import find_token, load_whitelist, load_alias

        wl = load_whitelist()
        patterns = load_alias('patterns.tsv')
        assert not find_token('t', {}, {}, {}, {}, [])
        assert find_token('t', wl, {}, {}, {}, []) == 't'
        assert find_token('th', wl, {'h': 'ʰ'}, {}, {}, []) == 'tʰ'
        assert find_token('th', wl, {}, {'th': 'x'}, {}, []) == 'x'
        with self.assertRaises(ValueError):
            find_token('th', wl, {}, {'th': 'X'}, {}, [])
        assert find_token('th', wl, {}, {}, patterns, []) == 'tʰ'
        assert find_token('th', wl, {}, {}, {}, ['h']) == 't'
