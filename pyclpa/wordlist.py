# coding: utf8
from __future__ import unicode_literals, print_function, division
import unicodedata

from clldutils.path import Path
from clldutils.dsv import reader, UnicodeWriter

from pyclpa.util import load_alias, split, join
from pyclpa.base import get_clpa, Errors


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

    def check(self, column='TOKENS', rules=False, clpa=None):
        clpa = clpa or get_clpa()

        if rules:
            rules = load_alias(rules)
            for val in self:
                tokens = [rules[t] if t in rules else t for t in split(val[column])]
                val[column] = join(tokens)

        sounds, errors = {}, Errors()
        for item in self:
            tokens, _, _ = clpa.check_sequence(
                split(item[column]), sounds=sounds, errors=errors)
            item['CLPA_TOKENS'] = join(tokens)
            item['CLPA_IDS'] = join([clpa.segment2clpa(t) for t in tokens])

        return sounds, errors
