# coding: utf8
from __future__ import unicode_literals, print_function, division
import unicodedata
from collections import Counter

from clldutils.path import Path
from clldutils.dsv import reader, UnicodeWriter

from pyclpa.util import load_alias, load_whitelist, find_token, split, join


class Wordlist(list):
    @classmethod
    def from_file(cls, path, sep="\t", comment="#"):
        wl = cls()
        wl.read(path, sep=sep, comment=comment)
        return wl

    def read(self, path, sep="\t", comment="#"):
        with Path(path).open(encoding='utf-8') as handle:
            lines = [unicodedata.normalize('NFC', hline) for hline in handle.readlines()
                     if hline and not hline.startswith(comment)]
        self.extend(list(reader(lines, dicts=True, delimiter=sep)))

    def write(self, path, sep="\t"):
        with UnicodeWriter(path, delimiter=sep) as writer:
            for i, item in enumerate(self):
                if i == 0:
                    writer.writerow(list(item.keys()))
                writer.writerow(list(item.values()))
        if path is None:
            return writer.read()

    def check(self, column='TOKENS', rules=False):
        # whitelist is the basic list, which is in fact a dictionary
        whitelist = load_whitelist()
        # alias are segments of length 1 and they are parsed second in the app
        alias = load_alias('alias.tsv')
        # deleted items are those which we don't need once we have the tokens
        delete = ['\u0361', '\u035c', '\u0301']
        # explicit are explicit aliases, applied to a full segment, not to its parts
        explicit = load_alias('explicit.tsv')
        # patterns are regexes which are difficult to state in separation
        patterns = load_alias('patterns.tsv')
        accents = "ˈˌ'"

        if rules:
            rules = load_alias(rules)
            for val in self:
                tokens = [rules[t] if t in rules else t for t in split(val[column])]
                val[column] = join(tokens)

        sounds, errors = {}, Counter({'convertable': 0, 'non-convertable': 0})
        for item in self:
            new_tokens, idxs = [], []

            for token in split(item[column]):
                accent = ''
                if token[0] in accents:
                    accent, token = token[0], token[1:]

                if token in whitelist or token in sounds:
                    if token in sounds:
                        sounds[token]['frequency'] += 1
                    else:
                        sounds[token] = dict(
                            frequency=1, clpa=accent + token, id=whitelist[token]['ID'])
                else:
                    check = find_token(
                        token, whitelist, alias, explicit, patterns, delete)
                    sounds[token] = dict(
                        frequency=1,
                        clpa=accent + check if check else '?',
                        id=whitelist[check]['ID'] if check else '?')
                    errors.update(['convertable' if check else 'non-convertable'])

                new_tokens.append(accent + sounds[token]['clpa'])
                idxs.append(sounds[token]['id'])
            item['CLPA_TOKENS'] = join(new_tokens)
            item['CLPA_IDS'] = join(idxs)

        return sounds, errors
