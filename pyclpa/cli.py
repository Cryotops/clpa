# coding: utf-8
"""
Main command line interface to the pyclpa package.
"""
from __future__ import unicode_literals, print_function
import sys
from collections import defaultdict, OrderedDict

from clldutils.clilib import ArgumentParser, ParserError
from clldutils.path import Path
from clldutils.dsv import UnicodeWriter

from pyclpa.util import check_string, load_whitelist
from pyclpa.wordlist import Wordlist


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
    fname = None
    for arg in args.args:
        if '=' in arg:
            key, val = arg.split('=')
            settings[key] = val
        else:
            fname = arg

    if not fname:
        raise ParserError('no filename passed as argument')

    wordlist = Wordlist.from_file(fname)
    sounds, errors = wordlist.check(rules=settings['rules'])

    if settings['format'] not in ['md', 'csv']:
        text = wordlist.write(settings['outfile'] or None)
        if not settings['outfile']:
            print(text)
        return

    segments = OrderedDict([('existing', []), ('missing', []), ('convertible', [])])
    for k in sorted(
        sounds, key=lambda x: (sounds[x]['frequency'], sounds[x]['id']), reverse=True
    ):
        type_, symbol = None, None
        if k == sounds[k]['clpa']:
            type_, symbol = 'existing', k
        elif sounds[k]['clpa'] == '?':
            type_, symbol = 'missing', k
        else:
            check = sounds[k]['clpa']
            if sounds[k]['clpa'][0] in "'ˌˈ":
                check = sounds[k]['clpa'][1:]
            if k != check != '?':
                type_, symbol = 'convertible', k + ' >> ' + sounds[k]['clpa']
        if type_ and symbol:
            segments[type_].append([symbol, sounds[k]['id'], sounds[k]['frequency']])

    if settings['format'] == 'csv':
        with UnicodeWriter(settings['outfile'] or None, delimiter='\t') as writer:
            for key, items in segments.items():
                for i, item in enumerate(items):
                    writer.writerow([i + 1] + item + [key])
        if not settings['outfile']:
            print(writer.read())
        return

    text = []
    header_template = """
# {0} sounds

| number | sound | clpa | frequency |
| ------:| ----- | ---- | ---------:|"""

    for key, items in segments.items():
        text.append(header_template.format(key.capitalize()))
        for i, item in enumerate(items):
            text.append("| {0} | {1[0]} | {1[1]} | {1[2]} |".format(i + 1, item))

    text = '\n'.join(text)
    if settings['outfile']:
        with Path(settings['outfile']).open('w', encoding='utf8') as fp:
            fp.write(text)
    else:
        print(text)


def check(args):
    """
    clpa check <STRING>
    """
    if len(args.args) != 1:
        raise ParserError('only one argument allowed')
    check = check_string(args.args[0], load_whitelist())
    print('\t'.join(args.args[0].split(' ')))
    print('\t'.join(check))


def main():  # pragma: no cover
    parser = ArgumentParser('pyclpa', report, check)
    sys.exit(parser.main())
