from clpa.clpa import load_CLPA, write_CLPA
from sys import argv
from collections import defaultdict
import json

if len(argv) < 2:
    import sys
    print("usage: python addvalues.py newdata.json")

    sys.exit()

clpa = load_CLPA()
new_data = json.load(open(argv[1]))

# get the maximal indices for all four classes to generate new data
maxidxs = {}
for dtype in ['consonant', 'vowel', 'diphtong', 'tone', 'marker']:
    maxidx = [int(key[1:]) for key in clpa[dtype+'s']]
    maxidxs[dtype] = max(maxidx)+1

# create feature-hash to check for identical representations
features = defaultdict(list)
for idx in clpa:
    if 'class' in clpa[idx]:
        this_feature = '-'.join([clpa[idx][h] for h in
            clpa[clpa[idx]['class']+'_features']])
        features[this_feature] += idx

for dpoint in new_data:
    
    if dpoint['glyph'] != '':
        glyph = dpoint['glyph']
        cls = dpoint['class']
        idx = cls[0] + str(maxidxs[cls]).rjust(3, '0')
        maxidxs[cls] += 1

        # create major types
        for feature in clpa[cls+'_features']:
            if feature not in dpoint:
                dpoint[feature] = ''
        
        # create feature-hash
        this_feature = '-'.join([dpoint[h] for h in clpa[cls+'_features']])
        if this_feature in features:
            print('Same feature for different glyphs encountered!  ({0}: {1})'.format(glyph, this_feature))
            raise ValueError("Features for different glyphs point to the same sounds.")

        clpa[idx] = dpoint
        clpa[cls+'s'] += [idx]
        print("[i] Added new glyph {0} to CLPA (ID={1}).".format(glyph, idx))

question = input('Submit the changes? (y/n) ')
if question in 'yYjJ':
    write_CLPA(clpa)
