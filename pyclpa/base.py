# coding: utf8
from __future__ import unicode_literals, print_function, division
import re
import logging

import attr
from clldutils.text import strip_chars

from pyclpa.util import load_alias, load_whitelist, split


_clpa = None


def get_clpa():
    global _clpa
    if not _clpa:
        _clpa = CLPA()
    return _clpa


@attr.s
class Sound(object):
    id = attr.ib(convert=lambda v: v or '?')
    clpa = attr.ib(convert=lambda v: v or '?')
    frequency = attr.ib(default=1)
    custom = attr.ib(default=False)


@attr.s
class Errors(object):
    convertible = attr.ib(default=0)
    non_convertible = attr.ib(default=0)


class CLPA(object):
    def __init__(self,
                 whitelist=None,
                 alias=None,
                 delete=None,
                 explicit=None,
                 patterns=None,
                 accents=None,
                 rules=None,
                 normalized=None):
        self.whitelist = load_whitelist() if whitelist is None else whitelist
        self.alias = load_alias('alias.tsv') if alias is None else alias
        self.delete = ['\u0361', '\u035c', '\u0301'] if delete is None else delete
        self.explicit = load_alias('explicit.tsv') if explicit is None else explicit
        self.patterns = load_alias('patterns.tsv') if patterns is None else patterns
        self.accents = "ˈˌ'" if accents is None else accents
        self.rules = rules or {}
        self.normalized = load_alias('normalized.tsv') \
            if normalized is None else normalized

        log = logging.getLogger(__name__)
        for v in self.explicit.values():
            if v not in self.whitelist:
                log.debug('explicit token "{0}" not in whitelist'.format(v))

    def check_sequence(self, seq, sounds=None, errors=None):
        seq = seq if isinstance(seq, (list, tuple)) else split(seq)
        tokens = []
        sounds = {} if sounds is None else sounds
        errors = errors or Errors()

        for token in [self.rules.get(t, t) for t in seq]:
            accent = ''
            if token[0] in self.accents:
                accent, token = token[0], token[1:]

            if token in sounds:
                sounds[token].frequency += 1
            elif token in self.whitelist:
                sounds[token] = Sound(clpa=token, id=self.whitelist[token]['ID'])
            elif token.endswith('/') and len(token) > 1:
                sounds[token] = Sound(
                    custom=True, clpa='*' + token[:-1], id='custom:%s' % token[:-1])
            else:
                tkn, id_ = self._find(token)
                sounds[token] = Sound(clpa=tkn, id=id_)
                if tkn:
                    errors.convertible += 1
                else:
                    errors.non_convertible += 1

            tokens.append(accent + sounds[token].clpa)
        return tokens, sounds, errors

    def segment2clpa(self, segment):
        """Convert a segment to its identifier"""
        segment = segment[1:] if segment[0] in self.accents else segment
        return self.whitelist[segment]['ID'] if segment in self.whitelist else '?'

    def normalize(self, string):
        return ''.join([self.normalized.get(x, x) for x in string])

    def _find(self, token):
        # custom symbols, indicated by "/", in the form "custom/value", if value is
        # missing, this will be subsumed under "custom" in the count
        if '/' in token and len(token) > 1:
            _, token = token.split('/', 1)
            assert token  # note: the custom case "c/" has been dealt with already!

        # first run, delete useless stuff
        token = strip_chars(self.delete, token)
        if token in self.whitelist:
            return token, self.whitelist[token]['ID']

        # second run, explicit match
        if token in self.explicit:
            assert self.explicit[token] in self.whitelist
            return self.explicit[token], self.whitelist[self.explicit[token]]['ID']

        # third run, replace
        token = ''.join([self.alias.get(t, t) for t in token])
        if token in self.whitelist:
            return token, self.whitelist[token]['ID']

        # forth run, pattern matching
        for source, target in self.patterns.items():
            token = re.sub(source, target, token)
            if token in self.whitelist:
                return token, self.whitelist[token]['ID']

        return None, None
