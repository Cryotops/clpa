# coding: utf8
from __future__ import unicode_literals, print_function, division
import re
import logging

from clldutils.misc import UnicodeMixin

from pyclpa.util import load_alias, load_whitelist, split, join


_clpa = None


def get_clpa():
    global _clpa
    if not _clpa:
        _clpa = CLPA()
    return _clpa


class Token(UnicodeMixin):
    def __init__(self, origin):
        self.origin = origin

    def __unicode__(self):
        return self.origin  # pragma: no cover


class Unknown(Token):
    def __unicode__(self):
        return '\ufffd'


class Custom(Token):
    def __unicode__(self):
        return self.origin[:-1]


class Sound(Token):
    def __init__(self, origin, clpa):
        Token.__init__(self, origin)
        self.clpa = clpa

    @property
    def converted(self):
        return self.origin != self.clpa.CLPA

    def __unicode__(self):
        return self.clpa.CLPA


class CLPA(object):
    def __init__(self,
                 whitelist=None,
                 alias=None,
                 explicit=None,
                 patterns=None,
                 accents=None,
                 normalized=None):
        self.whitelist = load_whitelist() if whitelist is None else whitelist
        self.alias = load_alias('alias.tsv') if alias is None else alias
        self.explicit = load_alias('explicit.tsv') if explicit is None else explicit
        self.patterns = load_alias('patterns.tsv') if patterns is None else patterns
        self.accents = "ˈˌ'" if accents is None else accents
        self.normalized = load_alias('normalized.tsv') \
            if normalized is None else normalized

        log = logging.getLogger(__name__)
        for v in self.explicit.values():
            if v not in self.whitelist:
                log.debug('explicit token "{0}" not in whitelist'.format(v))

    def __call__(self, seq, sounds=None, text=False):
        """
        Convert a sequence to CLPA tokens.

        Parameters
        ----------
        seq
        sounds: To speed up lookup, a `dict` can be passed in to accumulate a sequence \
        item to CLPA token mapping.

        Returns
        -------

        """
        tokens = []
        sounds = {} if sounds is None else sounds

        for item in seq if isinstance(seq, (list, tuple)) else split(seq):
            if item in sounds:
                tokens.append(sounds[item])
                continue

            cls, clpa = self._cls_clpa(item)
            tokens.append((cls, item, clpa))
            sounds[item] = tokens[-1]

        res = [class_(i) if c is None else class_(i, c) for class_, i, c in tokens]
        if text:
            return join(res)
        return res

    def _cls_clpa(self, token):
        if token[0] in self.accents:
            token = token[1:]

        if token in self.whitelist:
            return Sound, self.whitelist[token]

        if token.endswith('/') and len(token) > 1:
            return Custom, None

        if '/' in token and len(token) > 1:
            token = token.split('/', 1)[-1]
            if token in self.whitelist:
                # Sound converted from right hand side of custom symbol.
                return Sound, self.whitelist[token]

        if token in self.explicit:
            assert self.explicit[token] in self.whitelist
            return Sound, self.whitelist[self.explicit[token]]

        token = ''.join([self.alias.get(t, t) for t in token])
        if token in self.whitelist:
            return Sound, self.whitelist[token]

        for source, target in self.patterns.items():
            token = re.sub(source, target, token)
            if token in self.whitelist:
                break

        if token in self.whitelist:
            return Sound, self.whitelist[token]

        return Unknown, None

    def normalize(self, string):
        return ''.join([self.normalized.get(x, x) for x in string])
