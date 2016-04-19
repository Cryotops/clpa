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
    print('| number | sound | clpa | frequency |')
    print('| ------ | ----- | ---- | --------- |')

    for k in sorted(sounds, key=lambda x: sounds[x]['frequency'], reverse=True):
        if k == sounds[k]['clpa']:
            print('| {0} | {1} | {2} | {3} |'.format(
            #print('[{0}] Existing sound «{1}» (frequency: {2}) not known to CLPA.'.format(
               idx,
               k, sounds[k]['id'], sounds[k]['frequency']))
            idx += 1

    print('')
    print("Missing Sounds")
    print("--------------")
    print('| number | sound | clpa | frequency |')
    print('| ------ | ----- | ---- | --------- |')
    idx = 1
    for k in sorted(sounds, key=lambda x: sounds[x]['frequency'], reverse=True):
        if sounds[k]['clpa'] == '?':
            print('| {0} | {1} | {2} | {3} |'.format(
               idx,
               k, sounds[k]['id'], sounds[k]['frequency']))
            idx += 1
    
    print('')
    print("Convertible Sounds")
    print("------------------")
    print('| number | sound | ipa-equivalent | clpa | frequency |')
    print('| ------ | ----- | -------------- | ---- | --------- |')
    
    idx = 1
    # write them also to file!
    outfile = codecs.open(argv[1].replace('.tsv', '.converted.tsv'), 'w', 'utf-8')
    for k in sorted(sounds, key=lambda x: sounds[x]['frequency'], reverse=True):
        check = sounds[k]['clpa']
        if sounds[k]['clpa'][0] in "'ˌˈ":
            check = sounds[k]['clpa'][1:]
        if k != check and check != '?':
            print('| {0} | {1} | {2} | {3} | {4} |'.format(
                        idx,
                        k,
                        sounds[k]['clpa'],
                        sounds[k]['id'],
                        sounds[k]['frequency'],
                        ))
            idx += 1
            outfile.write(k+'\t'+sounds[k]['clpa']+'\n')

   
    write_wordlist(argv[1].replace('.tsv', '.mapped.tsv'), wordlist)
