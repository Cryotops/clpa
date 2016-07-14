# coding: utf-8
from __future__ import unicode_literals, print_function, division
import unicodedata
import re

from clldutils.path import Path
from clldutils.dsv import reader, UnicodeWriter
from clldutils import jsonlib


def load_wordlist(path, sep="\t", comment="#"):
    """
    Load a wordlist and make it easily parseable by turning it into a dictionary. 
    """
    with Path(path).open(encoding='utf-8') as handle:
        lines = [unicodedata.normalize('NFC', hline) for hline in handle.readlines()
                 if hline and not hline.startswith(comment)]
    return list(reader(lines, dicts=True, delimiter=sep))


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
        outdir, fname = local_path(), path
    old_clpa = load_CLPA()
    jsonlib.dump(old_clpa, outdir.joinpath(fname + '.bak'))
    jsonlib.dump(clpadata, outdir.joinpath(fname))


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


def check_string(seq, whitelist):
    return ['*' if t in whitelist else '?'
            for t in unicodedata.normalize('NFC', seq).split(' ')]


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


def write_wordlist(path, wordlist, sep="\t"):
    """
    Write a wordlist to file (for example, after having it checked).
    """
    with UnicodeWriter(path, delimiter=sep) as writer:
        for i, item in enumerate(wordlist):
            if i == 0:
                writer.writerow(list(item.keys()))
            writer.writerow(list(item.values()))
    if path is None:
        return writer.read()


def check_wordlist(path, sep='\t', comment='#', column='TOKENS', rules=False):
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

    # accents
    accents = "ˈˌ'"

    wordlist = load_wordlist(path, sep=sep, comment=comment)

    if rules:
        rules = load_alias(rules)
        for val in wordlist:
            tokens = []
            for t in val['TOKENS'].split(' '):
                tokens.append(rules[t] if t in rules else t)
            val['TOKENS'] = ' '.join(tokens)
    
    # store errors in dictionary
    sounds = {}
    errors = {'convertable': 0, 'non-convertable': 0}

    # iterate over teh tokens
    for item in wordlist:
        tokens = item[column]
        
        for token in tokens.split(' '):
            accent = ''
            if token[0] in accents:
                accent = token[0]
                token = token[1:]

            if token in whitelist or token in sounds:
                try:
                    sounds[token]['frequency'] += 1
                except KeyError:
                    sounds[token] = {}
                    sounds[token]['frequency'] = 1
                    sounds[token]['clpa'] = accent + token
                    sounds[token]['id'] = whitelist[token]['ID']

            else:
                check = find_token(token, whitelist, alias, explicit, patterns, delete)
                sounds[token] = {}
                sounds[token]['frequency'] = 1
                if check:
                    sounds[token]['clpa'] = accent + check
                    sounds[token]['id'] = whitelist[check]['ID']
                    errors['convertable'] += 1
                else:
                    sounds[token]['clpa'] = '?'
                    sounds[token]['id'] = '?'
                    errors['non-convertable'] += 1

        new_tokens = []
        idxs = []
        for token in tokens.split(' '):
            accent = ''
            if token[0] in accents:
                accent = token[0]
                token = token[1:]

            new_tokens += [accent + sounds[token]['clpa']]
            idxs += [sounds[token]['id']]
        item['CLPA_TOKENS'] = ' '.join(new_tokens)
        item['CLPA_IDS'] = ' '.join(idxs)

    return sounds, errors, wordlist
