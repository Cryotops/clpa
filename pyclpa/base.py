# coding: utf8
from __future__ import unicode_literals, print_function, division
from collections import Counter

from pyclpa.util import load_alias, load_whitelist, find_token


_clpa = None


def get_clpa():
    global _clpa
    if not _clpa:
        _clpa = CLPA()
    return _clpa


class CLPA(object):
    def __init__(self,
                 whitelist=None,
                 alias=None,
                 delete=None,
                 explicit=None,
                 patterns=None,
                 accents=None,
                 rules=None):
        self.whitelist = whitelist or load_whitelist()
        self.alias = alias or load_alias('alias.tsv')
        self.delete = delete or ['\u0361', '\u035c', '\u0301']
        self.explicit = explicit or load_alias('explicit.tsv')
        self.patterns = patterns or load_alias('patterns.tsv')
        self.accents = accents or "ˈˌ'"
        self.rules = rules or []

    def check_sequence(self, seq, sounds=None, errors=None):
        if not isinstance(seq, (list, tuple)):
            new_seq = seq.split(' ')
        else:
            new_seq = [x for x in seq]
        if self.rules:
            new_seq = [self.rules[t] if t in self.rules else t for t in new_seq]

        new_tokens = []
        sounds = sounds or {}
        errors = errors or Counter({'convertable': 0, 'non-convertable': 0})

        for token in new_seq:
            accent = ''
            if token[0] in self.accents:
                accent, token = token[0], token[1:]

            if token in self.whitelist or token in sounds:
                if token in sounds:
                    sounds[token]['frequency'] += 1
                else:
                    sounds[token] = dict(
                        frequency=1, clpa=token, id=self.whitelist[token]['ID'])
            else:
                check = find_token(
                    token, self.whitelist, self.alias, self.explicit,
                    self.patterns, self.delete)
                sounds[token] = dict(
                    frequency=1,
                    clpa=check if check else '?',
                    id=self.whitelist[check]['ID'] if check else '?')
                errors.update(['convertable' if check else 'non-convertable'])

            new_tokens.append(accent + sounds[token]['clpa'])
        return new_tokens, sounds, errors

    def segment2clpa(self, segment):
        """Convert a segment to it identifier"""
        if segment[0] in self.accents:
            new_segment = segment[1:]
        else:
            new_segment = segment
        return self.whitelist[new_segment]['ID'] \
            if new_segment in self.whitelist else '?'
