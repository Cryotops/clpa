# coding: utf-8
from __future__ import unicode_literals, print_function, division
import unicodedata
import re

from clldutils.path import Path
from clldutils import jsonlib


def local_path(*comps):
    """Helper function to create a local path to the current directory of CLPA"""
    return Path(__file__).parent.joinpath('data', *comps)


def load_CLPA():
    """
    Load the main data file.
    """
    return jsonlib.load(local_path('clpa.main.json'))


def write_CLPA(clpadata, path):
    """
    Basic function to write clpa-data.
    """
    if isinstance(path, Path):
        outdir, fname = path.parent, path.name
    else:
        outdir, fname = local_path(), path  # pragma: no cover
    old_clpa = load_CLPA()
    jsonlib.dump(old_clpa, outdir.joinpath(fname + '.bak'), indent=4)
    jsonlib.dump(clpadata, outdir.joinpath(fname), indent=4)


def load_whitelist():
    """
    Basic function to load the CLPA whitelist.
    """
    _clpadata = jsonlib.load(local_path('clpa.main.json'))
    whitelist = {}
    for group in ['consonants', 'vowels', 'markers', 'tones', 'diphtongs']:
        for val in _clpadata[group]:
            whitelist[_clpadata[val]['glyph']] = _clpadata[val]
            whitelist[_clpadata[val]['glyph']]["ID"] = val

    return whitelist


def load_alias(_path):
    """
    Alias are one-character sequences which we can convert on a step-by step
    basis by applying them successively to all subsegments of a segment.
    """
    path = Path(_path)
    if not path.is_file():
        path = local_path(_path)

    alias = {}
    with path.open(encoding='utf-8') as handle:
        for line in handle:
            if not line.startswith('#') and line.strip():
                source, target = line.strip().split('\t')
                alias[eval('"' + source + '"')] = eval('r"' + target + '"')
    return alias


def split(string):
    return string.split(' ')


def join(tokens):
    return ' '.join(tokens)


def check_string(seq, whitelist):
    return [
        '*' if t in whitelist else '?' for t in split(unicodedata.normalize('NFC', seq))]


def find_token(token, whitelist, alias, explicit, patterns, delete):
    if token in whitelist:
        return token

    # first run, delete useless stuff
    tokens = list(token)
    for i, t in enumerate(tokens):
        if t in delete:
            tokens[i] = ''
    new_token = ''.join(tokens)
    if new_token in whitelist:
        return new_token

    # third run, explicit match
    if new_token in explicit:
        new_token = explicit[new_token]
        if new_token in whitelist:
            return new_token
        raise ValueError(
            "Explicit list does not point to whitelist with sound «{0}»".format(
                new_token))

    # second run, replace
    tokens = list(new_token)
    for i, t in enumerate(tokens):
        if t in alias:
            tokens[i] = alias[t]

    new_token = ''.join(tokens)
    if new_token in whitelist:
        return new_token

    # forth run, pattern matching
    for source, target in patterns.items():
        search = re.search(source, new_token)
        if search:
            new_token = re.sub(source, target, new_token)
        if new_token in whitelist:
            return new_token
    return False
