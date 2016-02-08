import csv
import codecs
import unicodedata
from collections import OrderedDict
import json
import os
import re

def load_wordlist(path, sep="\t", comment="#"):
    """
    Load a wordlist and make it easily parseable by turning it into a dictionary. 
    """
    D = OrderedDict()
    with codecs.open(path, 'r', 'utf-8') as handle:
        header = False
        for line in csv.reader(
                [unicodedata.normalize(
                    'NFC', 
                    hline
                    ) for hline in handle.readlines()], delimiter=sep):
            if not line or line[0].startswith(comment):
                pass
            else:
                if not header:
                    header = [l for l in line]
                    D[0] = header
                else:
                    D[line[0]] = OrderedDict()
                    for k,v in zip(header, line):
                        D[line[0]][k] = v
    return D

def local_path(path):
    """Helper function to create a local path to the current directory of CLPA"""
    return os.path.join(
            os.path.split(__file__)[0],
            path
            )

def load_whitelist():
    """
    Basic function to load the CLPA whitelist.
    """
    whitelist = {}
    with codecs.open(local_path('clpa.tsv'), 'r', 'utf-8') as handle:
        head = False
        for line in handle:
            if line.strip():
                if not head:
                    head = line.split('\t')
                else:
                    items = line.split('\t')
                    source = items[1]
                    target = items
                    whitelist[source] = dict(zip(head, target))

    return whitelist

def load_alias(path):
    """
    Alias are one-character sequences which we can convert on a step-by step
    basis by applying them successively to all subsegments of a segment.
    """
    if not os.path.isfile(path):
        path = local_path(path) 
    
    alias = {}
    with codecs.open(path, 'r', 'utf-8') as handle:
        for line in handle:
            if not line.startswith('#') and line.strip():
                source, target = line.strip().split('\t')
                alias[eval('"'+source+'"')] = eval('r"'+target+'"')
    return alias

def check_string(seq, whitelist):

    tokens = unicodedata.normalize('NFC', seq).split(' ')
    out = []
    for token in tokens:
        if token in whitelist:
            out += ['*']
        else:
            out += ['?']
    return out

def find_token(token, whitelist, alias, explicit, patterns, delete):
    
    # check if token in whitelist
    if token in whitelist:
        return token

    # first run, delete useless stuff
    tokens = list(token)
    for i,t in enumerate(tokens):
        if t in delete:
            tokens[i] = ''
    new_token = ''.join(tokens)
    if new_token in whitelist:
        return new_token

    # second run, replace
    tokens = list(new_token)
    for i,t in enumerate(tokens):
        try:
            tokens[i] = alias[t]
        except KeyError:
            pass
    new_token = ''.join(tokens)
    if new_token in whitelist:
        return new_token

    # third run, explicit match
    if new_token in explicit:
        new_token = explicit[new_token]
        if new_token in whitelist:
            return new_token
        else:
            raise ValueError("Explicit list does not point to whitelist")

    # forth run, pattern matching
    for source, target in patterns.items():
        search = re.search(source, new_token)
        if search:
            new_token = re.sub(
                    source,
                    target,
                    new_token
                    )
        if new_token in whitelist:
            return new_token
    return False

def write_wordlist(path, wordlist, sep="\t", header=[]):
    """
    Write a wordlist to file (for example, after having it checked).
    """
    if not header:
        header = wordlist[0]

    out = '\t'.join(header)+'\n'
    for k in [x for x in wordlist if x != 0]:
        out += '\t'.join([wordlist[k][h] for h in header])+'\n'

    with codecs.open(path, 'w', 'utf-8') as f:
        f.write(out)


def check_wordlist(path, sep='\t', comment='#', column='TOKENS', pprint=False,
        rules=False):
    
    # whitelist is the basic list, which is in fact a dictionary
    whitelist = load_whitelist()
    # alias are segments of length 1 and they are parsed second in the app
    alias = load_alias('alias.tsv')
    # deleted items are those which we don't need once we have the tokens
    delete = ['\u0361', '\u035c', '\u0301']
    # explicit are explicit aliases, applied to a full segment, not to its
    # parts
    explicit = load_alias('explicit.tsv')
    # patterns are regexes which are difficult to state in separation
    patterns = load_alias('patterns.tsv')

    # now, load teh wordlist
    wordlist = load_wordlist(path, sep=sep, comment=comment)

    # check for rules
    if rules:
        rules = load_alias(rules)
        for k,val in wordlist.items():
            tokens = []
            for t in val['TOKENS'].split(' '):
                nt = rules[t] if t in rules else t
                tokens += [nt]
            wordlist[k]['TOKENS'] = ' '.join(tokens)
    
    # store errors in dictionary
    sounds = {}
    errors = {'convertable' : 0, 'non-convertable' : 1}

    # iterate over teh tokens
    for key in sorted([k for k in wordlist if k != 0]):
        tokens = wordlist[key][column]
        
        for token in tokens.split(' '):
            if token in whitelist or token in sounds:
                try:
                    sounds[token]['frequency'] += 1
                except KeyError:
                    sounds[token] = {}
                    sounds[token]['frequency'] = 1
                    sounds[token]['clpa'] = token
                    sounds[token]['id'] = whitelist[token]['ID']

            else:
                check = find_token(
                        token, whitelist, alias, explicit, patterns, delete)
                sounds[token] = {}
                sounds[token]['frequency'] = 1
                if check:
                    sounds[token]['clpa'] = check
                    sounds[token]['id'] = whitelist[check]['ID']
                    errors['convertable'] += 1
                else:
                    sounds[token]['clpa'] = '?'
                    sounds[token]['id'] = '?'
                    errors['non-convertable'] += 1
    if pprint:
        print('Sounds: {0}'.format(len(sounds)))
        print('Missing: {0}'.format(errors['convertable'] + errors['non-convertable'])
                )
        print("Convertable {0}".format(errors['convertable']))
        print("Non-Convertable {0}".format(errors['non-convertable']))

    
    for key in sorted([x for x in wordlist if x != 0]):
        tokens = wordlist[key][column]
        new_tokens = []
        idxs = []
        for token in tokens.split(' '):
            new_tokens += [sounds[token]['clpa']]
            idxs += [sounds[token]['id']]
        wordlist[key]['CLPA_TOKENS'] = ' '.join(new_tokens)
        wordlist[key]['CLPA_IDS'] = ' '.join(idxs)

    wordlist[0] += ["CLPA_TOKENS", "CLPA_IDS"]

    return sounds, errors, wordlist


