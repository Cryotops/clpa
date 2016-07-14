# coding: utf8
from __future__ import unicode_literals, print_function, division

from mock import Mock
from clldutils.testing import capture

from pyclpa.tests.util import TestCase


class Tests(TestCase):
    def test_report(self):
        from pyclpa.cli import report

        args = [self.data_path('KSL.tsv').as_posix()]

        with capture(report, Mock(args=args)) as out:
            self.assertIn('Convertible sounds', out)

        args.append('format=cldf')
        with capture(report, Mock(args=args)) as out:
            if hasattr(out, 'decode'):
                out = out.decode('utf8')
            self.assertIn('CLPA_TOKENS', out)

    def test_check(self):
        from pyclpa.cli import check

        with capture(check, Mock(args=['abcd'])) as out:
            self.assertIn('?', out)
