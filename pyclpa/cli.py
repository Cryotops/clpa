"""
Main command line interface to the pyclpa package.
"""
from __future__ import unicode_literals, print_function
import sys
from collections import defaultdict

from clldutils.path import Path
from clldutils.clilib import ArgumentParser, ParserError
from clldutils.jsonlib import load

from pyclpa import util as clpa_util

def report(args):
    """
    clpa report <FILE> [rules=FILE] [format=md|csv|cldf] [outfile=FILENAME]

    Note
    ----
    
    * Rules point to a tab-separated value file in which source and target are
      given to convert a segment to another segment to be applied on a
      data-set-specific basis which may vary from dataset to dataset and can thus
      not be included as standard clpa behaviour.
    * Input file needs to be in csv-format, with tabstop as separator, and it
      needs to contain one column named "TOKENS". 
    * format now allows for md (MarkDown), csv (CSV, tab as separator), or cldf
      (no pure cldf but rather current lingpy-csv-format). CLDF format means
      that the original file will be given another two columns, one called
      CLPA_TOKENS, one called CLPA_IDS.
    * if you specify an outfile from the input, the data will be written to
      file instead showing it on the screen.

    """
    if len(args.args) < 1:
        raise ParserError('not enough arguments')

    # get keywords from arguments @xrotwang: is there any better way to do so?
    settings = defaultdict(str)
    settings['format'] = 'md'
    for arg in args.args:
        if '=' in arg:
            key, val = arg.split('=')
            settings[key] = val
        else:
            fname = arg

    # get the data
    sounds, errors, wordlist = clpa_util.check_wordlist(fname, rules=settings['rules'])
    
    if settings['format'] in ['md', 'csv']:
        md_template =""" # {0}
| number | sound | clpa | frequency |
| ------ | ----- | ---- | --------- |
"""
        md_line = "| {0[0]} | {0[1]} | {0[2]} | {0[3]} |\n"
        csv_line = "{0[0]}\t{0[1]}\t{0[2]}\t{0[3]}\t{1}\n"

        text = ""
        
        # check existing sounds
        if [s for s in sounds if sounds[s]['clpa'] == s]:
            idx = 1
            text += md_template.format('Existing sounds') if settings['format'] == 'md' else ''
            for k in sorted(sounds, key=lambda x: sounds[x]['frequency'], reverse=True):
                if k == sounds[k]['clpa']:
                    _tmp = [idx, k, sounds[k]['id'], sounds[k]['frequency']]
                    if settings['format'] == 'md':
                        text += md_line.format(_tmp)
                    else:
                        text += csv_line.format(_tmp, 'existing')
                    idx += 1
        
        if [s for s in sounds if sounds[s]['clpa'] == '?']:
            idx = 1
            text += md_template.format('Missing sounds') if settings['format'] == 'md' else ''
            for k in sorted(sounds, key=lambda x: sounds[x]['frequency'], reverse=True):
                if k != sounds[k]['clpa'] and sounds[k]['clpa'] == '?':
                    _tmp = [idx, k, sounds[k]['id'], sounds[k]['frequency']]
                    if settings['format'] == 'md':
                        text += md_line.format(_tmp)
                    else:
                        text += csv_line.format(_tmp, 'missing')
                    idx += 1

        if [s for s in sounds if sounds[s]['clpa'] != '?' and sounds[s]['clpa'] != s]:
            idx = 1
            text += md_template.format('Convertible sounds') if settings['format'] == 'md' else ''
            for k in sorted(sounds, key=lambda x: sounds[x]['frequency'], reverse=True):
                check = sounds[k]['clpa']
                if sounds[k]['clpa'][0] in "'ˌˈ":
                    check = sounds[k]['clpa'][1:]            
                if k != check != '?':
                    _tmp = [idx, k+' >> '+sounds[k]['clpa'], sounds[k]['id'], sounds[k]['frequency']]
                    if settings['format'] == 'md':
                        text += md_line.format(_tmp)
                    else:
                        text += csv_line.format(_tmp, 'convertible')
                    idx += 1
    else:
        text = clpa_util.serialize_wordlist(wordlist)

    if settings['outfile']:
        clpa_util.write_file(text)
    else:
        print(text)

def check(args):
    """
    clpa check <STRING>
    """
    if len(args.args) != 1:
        raise ValueError('only one argument allowed')
    check = clpa_util.check_string(args.args[0], clpa_util.load_whitelist())
    print('\t'.join(args.args[0].split(' ')))
    print('\t'.join(check))

def main():  # pragma: no cover
    parser = ArgumentParser('pyclpa', report, check)
    sys.exit(parser.main())
