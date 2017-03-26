"""
CLTS module for consistent IPA handling.
========================================

"""
from clldutils.dsv import UnicodeReader
import re
from clldutils.path import Path
from clldutils.misc import cached_property
import attr
import unicodedata

from pyclpa.util import local_path, split, join

# conforms to our norm which says that we treat the symbol ◌ as an empty symbol
def _norm(string):
    """Replace our symbol "◌" for empty replacements with nothing"""
    return string.replace("◌", "")


# helper normalizes to nfd
def _nfd(string):
    return unicodedata.normalize("NFD", string)


# functions can be later easily modified
def csv_as_list(path):
    with UnicodeReader(local_path(path), delimiter="\t") as f:
        return [[unicodedata.normalize('NFD', x).strip() for x in line] for line in f]


def csv_as_dict(path):
    data = csv_as_list(path)
    return {line[0]: dict(zip(data[0][1:], line[1:])) for line in data[1:]}


class Clts(object):
    """
    Basic object to store the data.
    """
    # basic data
    _consonants = csv_as_list('consonants.tsv')
    _vowels = csv_as_list('vowels.tsv')
    _diacritics = csv_as_list('diacritics.tsv')
    _tones = csv_as_list('tones.tsv')
    _markers = csv_as_list('markers.tsv')
    _clicks = csv_as_list('clicks.tsv')

    # feature information
    _corder = dict(
            pre = ['preceding', 'phonation', 'syllabicity', 'nasalization', 
                'palatalization', 'labialization', 'aspiration', 
                'velarization', 'pharyngalization', 'duration'],
            post = ['release'])
    _vorder = dict(
            pre = ['nasalization', 'duration'],
            post = ['frication'])
    _lorder = dict(
            pre = ['preceding', 'phonation', 'place'],
            post = [])

    # normalization data
    _normalize = {_norm(a): _norm(b) for a, b in
            csv_as_list('normalize.tsv')[1:]}
    
    # basic regular expressions
    crex = '|'.join(sorted([y[0] for y in _consonants[1:]],
        key=lambda x: len(x),
        reverse=True))
    vrex = '|'.join(sorted([y[0] for y in _vowels[1:]],
        key=lambda x: len(x),
        reverse=True))
    trex = '|'.join(sorted([y[0] for y in _tones[1:]],
        key=lambda x: len(x),
        reverse=True))
    mrex = r'|'.join(sorted([re.escape(x[0]) for x in _markers[1:]]))
    lrex = '|'.join(sorted([y[0] for y in _clicks[1:]],
        key=lambda x: len(x),
        reverse=True))
    
    @cached_property()
    def features(self):
        """Create features which can be retrieved from the name of the sounds.
        
        Note
        ----
        E.g., Clts().features['voiced bilabial plosive'], is "b".
        """
        # retrieve values
        features = dict(consonant={}, vowel={})
        for line in self._consonants[1:]:
            if not line[4]:
                features[self.get_sound(line[0]).name] = line[0]
        for line in self._vowels[1:]:
            if not line[4]:
                features[self.get_sound(line[0]).name] = line[0]
        for line in self._tones[1:]:
            if not line[5]:
                features[' '.join(line[1:5]+['tone'])] = line[0]
        for line in self._diacritics[1:]:
            if not line[4]:
                features[line[1]][line[3]] = line[0]
        # TODO: change lines in code in the click description
        for line in self._clicks[1:]:
            if not line[5]:
                features[' '.join([line[1], line[2], line[4],
                    line[3], 'click'])] = line[0]
        return features

    def _norm(self, string):
        """Extended normalization: normalize by list of norm-characers, split
        by character "/"."""
        nstring = _norm(string)
        if "/" in string:
            s, t = string.split('/')
            if t:
                nstring = t
            else:
                nstring = s
        return self.normalize(nstring)

    def normalize(self, string):
        """Normalize the string according to normalization list"""
        return ''.join([self._normalize.get(x, x) for x in _nfd(string)])

    def sound_type(self, string):
        """Quickly determine the type of the string."""
        if re.search(self.lrex, _norm(string)):
            return "click"
        if re.search(self.crex, _norm(string)):
            return 'consonant'
        if re.search(self.vrex, _norm(string)):
            return 'vowel'
        if re.search(self.trex, _norm(string)):
            return 'tone'
        if re.search(self.mrex, _norm(string)):
            return 'marker'
    
    @cached_property()
    def clicks(self):
        clck = {}
        for line in self._clicks[1:]:
            clck[line[0]] = dict(
                    phonation=line[1], place=line[2], secondary=line[3],
                    manner=line[4])
            if line[5]:
                clck[line[0]].update(
                    {x: y for x, y in [itm.split(':') for itm in
                        line[5].split(',')]})
            if line[6]:
                clck[line[0]]['alias'] = True
            clck[line[0]]['type'] = 'click'
        return clck
    
    @cached_property()
    def consonants(self):
        cons = {}
        for line in self._consonants[1:]:
            cons[line[0]] = dict(
                    phonation=line[1], place=line[2], manner=line[3])
            if line[5]:
                cons[line[0]].update(
                    {x: y for x, y in [itm.split(':') for itm in
                        line[5].split(',')]})
            if line[4]:
                cons[line[0]]['alias'] = True
            cons[line[0]]['type'] = 'consonant'
        return cons

    @cached_property()
    def vowels(self):
        vows = {}
        for line in self._vowels[1:]:
            vows[line[0]] = dict(
                    roundedness=line[1], height=line[2], backness=line[3])
            if line[5]:
                vows[line[0]].update(
                    {x: y for x, y in [itm.split(':') for itm in
                        line[5].split(',')]})
            if line[4]:
                vows[line[0]]['alias'] = True
            vows[line[0]]['type'] = 'vowel'
        return vows

    @cached_property()
    def markers(self):
        marks = {}
        for line in self._markers:
            marks[line[0]] = {"feature": line[1], "value": line[2]}
            if line[3]:
                marks[line[0]]['alias'] = True
        return marks

    @cached_property()
    def tones(self):
        tons = {}
        for line in self._tones[1:]:
            tons[line[0]] = dict(
                    contour=line[1], start=line[2], middle=line[3], end=line[4])
            if line[5].strip():
                tons[line[0]]['alias'] = True
            tons[line[0]]['type'] = 'tone'
        return tons

    @cached_property()
    def diacritics(self):
        dias = dict(consonant={}, vowel={}, click={}, dipthong={})
        for line in self._diacritics[1:]:
            dias[line[1]][line[0]] = {line[2]: line[3]}
        return dias

    def vowel(self, string):
        "Return the features of a vowel."
        return self.vowels.get(_nfd(string), {})

    def consonant(self, string):
        "Return the features of a consonant."
        return self.consonants.get(_nfd(string), {})

    def tone(self, string):
        return self.tones.get(_nfd(string), {})

    def diacritic(self, string, stype):
        "Return the diacritic features."
        return self.diacritics[stype].get(_nfd(string), {})

    def click(self, string):
        return self.clicks.get(_nfd(string), {})

    def parse_string(self, string):
        """Parse a string and return its features.
        
        Note
        ----
        Strategy is rather simple: we determine the base part of a string and
        then search left and right of this part for the additional features as
        expressed by the diacritics. Fails if a segment has more than one basic
        part.
        """
        nstring = self._norm(string)
        stype = self.sound_type(nstring)
        if stype == 'marker':
            return {'type': 'marker', 'source': string, 
                    'base': re.split('('+self.mrex+')', nstring)[1]}
        if not stype: return {}
        rex = {"vowel": self.vrex, "consonant": self.crex, "tone":
                self.trex, "click": self.lrex}.get(stype, '')
        pre, mid, post = re.split('('+rex+')', self._norm(nstring))
        base_features = getattr(self, stype, '')(mid).copy()
        base_features.update({'source': string, "base": mid})
        unknown = []
        for p in pre:
            elm = self.diacritic(p+'◌', stype)
            if not elm:
                unknown += [p+'◌']
            base_features.update(elm)
        for p in post:
            elm = self.diacritic('◌'+p, stype)
            if not elm:
                unknown += ['◌'+p]
            base_features.update(elm)
        if unknown:
            base_features.update({'unknown': unknown})
        return base_features

    def get_sound(self, string):
        try:
            data = self.parse_string(string)
            data['clts'] = self
            if not 'type' in data:
                return UnknownSound(source=string)
            if data['type'] == 'consonant':
                return Consonant(**data)
            elif data['type'] == 'vowel':
                return Vowel(**data)
            elif data['type'] == 'tone':
                return Tone(**data)
            elif data['type'] == 'marker':
                return Marker(**data)
            elif data['type'] == 'click':
                return Click(**data)
            
        # here, we should take over to handle also dipthongs
        except ValueError:
            return UnknownSound(source=string)

    def get_sounds(self, string):
        for s in split(string):
            yield self.get_sound(s)

    def __call__(self, string):
        return self.get_sounds(string)

@attr.s
class UnknownSound(object):

    source = attr.ib(default=None)
    type = attr.ib(default='unknown')
    name = None
    
    def __str__(self):
        return self.source

@attr.s
class Sound(object):
    """
    Sound object stores basic features of the individual sound objects.
    """
    base = attr.ib(default=None)
    clts = attr.ib(default=None) # pass clts object to save time
    alias = attr.ib(default=None)
    unknown = attr.ib(default=None)

    type = attr.ib(default=None)
    source = attr.ib(default=None)

    def keys(self):
        return attr.asdict(self).keys()
    
    def values(self):
        return attr.asdict(self).values()

    def items(self):
        return attr.asdict(self).items()

    def __str__(self):
        # determine base values to avoid that we type the same diacritic
        # multiple times
        base_vals = getattr(self.clts, self.type)(self.base)
        base_str = clts.features.get(
                clts.get_sound(self.base).name,
                '?')
        out = ''
        for p in [x for x in self.write_order['pre'] if x not in base_vals]:
            out += _norm(self.clts.features[self.type].get(
                getattr(self, p, ''), ''))
        out += base_str
        for p in [x for x in self.write_order['post'] if x not in base_vals]:
            out += _norm(self.clts.features[self.type].get(
                        getattr(self, p, ''), ''))
        return out
    
    @property
    def name(self):
        out = []
        for p in self.name_order:
            out += [getattr(self, p, '')]
        return ' '.join([x for x in out if x]+[self.type])

    @classmethod
    def from_string(cls, string, clts=None):
        clts = clts or Clts()
        kw = clts.parse_string(string)
        kw['clts'] = clts
        return cls(**kw)

    def get(self, desc):
        return self.clts.features.get(desc, '')

@attr.s
class Click(Sound):
    manner = attr.ib(default=None)
    place = attr.ib(default=None)
    phonation = attr.ib(default=None)
    secondary = attr.ib(default=None)
    preceding = attr.ib(default=None)

    write_order = dict(
            pre = ['preceding'],
            post = ['phonation'])
    name_order = ['preceding', 'phonation', 'place', 'manner', 'secondary']


@attr.s
class Marker():
    type = attr.ib(default=None)
    source = attr.ib(default=None)
    base = attr.ib(default=None)
    alias = attr.ib(default=None)
    clts = attr.ib(default=None)
    unknown = attr.ib(default=None)

    @property
    def name(self):
        return self.clts.markers[self.base]['value']

    def __str__(self):
        return self.base

@attr.s
class Consonant(Sound):
    
    # features follow basic information about IPA from various sources, they
    # are potentially not yet exhaustive and should be updated at some point
    manner = attr.ib(default=None)
    place = attr.ib(default=None)
    aspiration = attr.ib(default=None)
    labialization = attr.ib(default=None)
    palatalization = attr.ib(default=None)
    preceding = attr.ib(default=None)
    velarization = attr.ib(default=None)
    duration = attr.ib(default=None)
    phonation = attr.ib(default=None)
    release = attr.ib(default=None)
    syllabicity = attr.ib(default=None)
    nasalization = attr.ib(default=None)

    # write order determines how consonants are written according to their
    # features, so this normalizes the order of diacritics preceding and
    # following the base part of the consonant
    write_order = dict(
            pre = ['preceding'],
            post = ['phonation', 'syllabicity', 'nasalization', 
                'palatalization', 'labialization', 'aspiration', 
                'velarization', 'pharyngalization', 'duration', 'release'])
    name_order = ['syllabicity', 'nasalization', 'palatalization',
                'labialization', 'aspiration', 'velarization',
                'pharyngealization', 'duration', 'phonation', 'place', 'manner', 'release']


@attr.s
class Vowel(Sound):

    roundedness = attr.ib(default=None)
    height = attr.ib(default=None)
    backness = attr.ib(default=None)
    nasalization = attr.ib(default=None)
    frication = attr.ib(default=None)
    duration = attr.ib(default=None)
    phonation = attr.ib(default=None)
    release = attr.ib(default=None)
    syllabicity = attr.ib(default=None)

    write_order = dict(
            pre = [],
            post = ['phonation', 'syllabicity', 'nasalization', 'duration',
                'frication'])
    name_order = ['phonation', 'syllabicity', 'duration', 'nasalization', 
            'roundedness', 'height', 'backness', 'frication']

@attr.s
class Tone(Sound):

    contour = attr.ib(default=None)
    start = attr.ib(default=None)
    middle = attr.ib(default=None)
    end = attr.ib(default=None)

    write_order = dict(
            pre = [],
            post = [])
    name_order = ['contour', 'start', 'middle', 'end']




if __name__ == "__main__":
    from lingpy import *
    from pyclpa import base
    from pylexibank.util import data_path
    clpa = base.get_clpa()
    clts = Clts()
    wl = Wordlist(data_path('baidial', 'raw', 'Bai-Dialect-Survey.tsv').as_posix())
    wl = get_wordlist(
            data_path('galuciotupi', 'cldf', 'galuciotupi.csv'),
            col="Language_name", row="Parameter_name")
    sounds = []
    for k, ipa in iter_rows(wl, 'segments'):
        sounds += ipa.split()
        #if ipa:
        #    tks = ipa2tokens(ipa, merge_vowels=False)
        #    sounds += tks
    sounds = sorted(set(sounds))
    errors = []
    errors2 = []
    modified = []
    for sound in sounds:
        test = clts.get_sound(sound)
        test2 = clpa(sound)[0]
        if not hasattr(test2, 'clpa'):
            errors2 += [sound]
        if test.type == 'unknown':
            errors += [sound]
        elif test.unknown:
            errors += [sound]
        else:
            if test.source != str(test):
                modified += [[sound, str(test)]]
            print(str(test), test.name)
