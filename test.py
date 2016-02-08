from clpa.clpa import check_wordlist, load_whitelist, check_string, write_wordlist
from sys import argv
import codecs

if __name__ == '__main__':
    
    try:
        path = argv[1]
    except IndexError:
        import sys
        print("Usage: python test.py wordlist.tsv")
        sys.exit()
    
    if len(argv) == 3:
        path2 = argv[2]
    else:
        path2 = ''

    # now check a full list
    sounds, errors, wordlist = check_wordlist(path, rules=path2)

    idx = 1
    print('Existing Sounds')
    print("---------------")
    for k in sorted(sounds):
        if k == sounds[k]['clpa']:
            print('[{0}] Missing sound «{1}» (frequency: {2}) not known to GIPA.'.format(
               idx,
               k, sounds[k]['frequency']))
            idx += 1

    print('')
    print("Missing Sounds")
    print("--------------")
    idx = 1
    for k in sorted(sounds):
        if sounds[k]['clpa'] == '?':
            print('[{0}] Missing sound «{1}» (frequency: {2}) not known to GIPA.'.format(
               idx,
               k, sounds[k]['frequency']))
            idx += 1
    
    print('')
    print("Convertible Sounds")
    print("------------------")
    idx = 1
    # write them also to file!
    outfile = codecs.open(argv[1].replace('.tsv', '.converted.tsv'), 'w', 'utf-8')
    for k in sorted(sounds):
        if k != sounds[k]['clpa'] and sounds[k]['clpa'] != '?':
            print('[{0}] Sound «{1}» (frequency: {2}) is equivalent to «{3}» in GIPA'.format(
                        idx,
                        k,
                        sounds[k]['frequency'],
                        sounds[k]['clpa']
                        ))
            idx += 1
            outfile.write(k+'\t'+sounds[k]['clpa']+'\n')
   
    write_wordlist(argv[1].replace('.tsv', '.mapped.tsv'), wordlist)
