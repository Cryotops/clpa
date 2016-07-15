# coding: utf8
from __future__ import unicode_literals, print_function, division

from mock import Mock
from clldutils.testing import capture
from clldutils.clilib import ParserError
from clldutils.dsv import reader

from pyclpa.tests.util import TestCase


class Tests(TestCase):
    def _read_tsv(self, path):
        return set(tuple(row[1:]) for row in reader(path, delimiter='\t'))

    def test_report(self):
        from pyclpa.cli import report

        with self.assertRaises(ParserError):
            report(Mock(args=[]))

        with self.assertRaises(ParserError):
            report(Mock(args=['format=csv']))

        args = [self.data_path('KSL.tsv').as_posix()]

        with capture(report, Mock(args=args)) as out:
            self.assertIn('Convertible sounds', out)

        out = self.tmp_path('test.csv')
        report(Mock(args=args + ['format=csv', 'outfile=' + out.as_posix()]))
        self.assertEqual(
            self._read_tsv(out), self._read_tsv(self.data_path('KSL_report.csv')))

        with capture(report, Mock(args=args + ['format=csv'])) as out:
            if hasattr(out, 'decode'):
                out = out.decode('utf8')
            self.assertIn('existing', out)

        with capture(report, Mock(args=args + ['format=cldf'])) as out:
            if hasattr(out, 'decode'):
                out = out.decode('utf8')
            self.assertIn('CLPA_TOKENS', out)

        out = self.tmp_path('test.md')
        report(Mock(args=args + ['outfile=' + out.as_posix()]))
        self.assertTrue(out.exists())

    def test_check(self):
        from pyclpa.cli import check

        with self.assertRaises(ParserError):
            check(Mock(args=[]))

        with capture(check, Mock(args=['abcd'])) as out:
            self.assertIn('?', out)
