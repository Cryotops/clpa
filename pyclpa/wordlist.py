# coding: utf8
from __future__ import unicode_literals, print_function, division
import unicodedata
from itertools import groupby

import attr
from clldutils.path import Path
from clldutils.dsv import reader, UnicodeWriter

from pyclpa.util import split, join
from pyclpa.base import get_clpa, Sound


@attr.s
class Segment(object):
    origin = attr.ib()
    clpa = attr.ib()
    frequency = attr.ib()


class Wordlist(list):
    @classmethod
    def from_file(cls, path, delimiter="\t", comment="#"):
        wl = cls()
        wl.read(path, delimiter=delimiter, comment=comment)
        return wl

    def read(self, path, delimiter="\t", comment="#"):
        with Path(path).open(encoding='utf-8') as handle:
            lines = [unicodedata.normalize('NFC', hline) for hline in handle.readlines()
                     if hline and not hline.startswith(comment)]
        self.extend(list(reader(lines, dicts=True, delimiter=delimiter)))

    def write(self, path=None, sep="\t"):
        with UnicodeWriter(path, delimiter=sep) as writer:
            for i, item in enumerate(self):
                if i == 0:
                    writer.writerow(list(item.keys()))
                writer.writerow(list(item.values()))
        if path is None:
            return writer.read()

    def check(self, column='TOKENS', clpa=None):
        clpa = clpa or get_clpa()

        all, sounds = [], {}
        for item in self:
            tokens = clpa(split(item[column]), sounds=sounds)
            item['CLPA_TOKENS'] = join(['%s' % t for t in tokens])
            item['CLPA_IDS'] = join(
                [t.clpa.ID if hasattr(t, 'clpa') else '' for t in tokens])
            all.extend(tokens)

        res = []
        for segment, sounds in groupby(
                sorted(all, key=lambda t: t.origin), lambda t: t.origin):
            sounds = list(sounds)
            res.append(Segment(
                origin=segment,
                clpa=sounds[0].clpa.CLPA if isinstance(sounds[0], Sound) else None,
                frequency=len(sounds)))

        return sorted(res, key=lambda seg: seg.frequency, reverse=True)
