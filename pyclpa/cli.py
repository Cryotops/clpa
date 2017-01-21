# coding: utf-8
"""
Main command line interface to the pyclpa package.
"""
from __future__ import unicode_literals, print_function
import sys
from collections import OrderedDict
import argparse

from clldutils.clilib import ArgumentParser, ParserError, command
from clldutils.path import Path
from clldutils.dsv import UnicodeWriter
from clldutils.markup import Table

from pyclpa.util import check_string, load_whitelist
from pyclpa.wordlist import Wordlist


def _checked_wordlist_from_args(args):
    if len(args.args) != 1:
        raise ParserError('no input file specified')

    fname = Path(args.args[0])
    if not fname.exists():
        raise ParserError('invalid input file specified')

    wordlist = Wordlist.from_file(fname, delimiter=args.delimiter)
    sounds, errors = wordlist.check(rules=args.rules, column=args.column)
    return wordlist, sounds, errors


@command()
def annotate(args):
    """
    Will add two columns CLPA_TOKENS and CLPA_IDS to the input file.

    clpa annotate <FILE>

    Note
    ----

    * Rules point to a tab-separated value file in which source and target are
      given to convert a segment to another segment to be applied on a
      data-set-specific basis which may vary from dataset to dataset and can thus
      not be included as standard clpa behaviour.
    * Input file needs to be in csv-format with header, delimiter and name of the
      relevant column can be specified as --delimiter and --column options respectively.
    * The resulting CSV is printed to <stdout> or to the file specified as --output.

    """
    wordlist, _, _ = _checked_wordlist_from_args(args)
    res = wordlist.write(args.output)
    if args.output is None:
        print(res)


@command()
def report(args):
    """
    clpa report <FILE>

    Note
    ----

    * Rules point to a tab-separated value file in which source and target are
      given to convert a segment to another segment to be applied on a
      data-set-specific basis which may vary from dataset to dataset and can thus
      not be included as standard clpa behaviour.
    * Input file needs to be in csv-format with header, delimiter and name of the
      relevant column can be specified as --delimiter and --column options respectively.
    * format now allows for md (MarkDown), csv (CSV, tab as separator), or cldf
      (no pure cldf but rather current lingpy-csv-format). CLDF format means
      that the original file will be given another two columns, one called
      CLPA_TOKENS, one called CLPA_IDS.
    * The report is printed to <stdout> or to the file specified as --output.

    """
    wordlist, sounds, errors = _checked_wordlist_from_args(args)

    segments = OrderedDict([('existing', []), ('missing', []), ('convertible', [])])
    for k in sorted(
            sounds, key=lambda x: (sounds[x].frequency, sounds[x].id), reverse=True):
        type_, symbol = None, None
        if k == sounds[k].clpa:
            type_, symbol = 'existing', k
        elif sounds[k].clpa == '?':
            type_, symbol = 'missing', k
        else:
            check = sounds[k].clpa
            if k != check != '?':
                type_, symbol = 'convertible', k + ' >> ' + sounds[k].clpa
        if type_ and symbol:
            segments[type_].append([symbol, sounds[k].id, sounds[k].frequency])

    if args.format == 'csv':
        with UnicodeWriter(args.output, delimiter='\t') as writer:
            for key, items in segments.items():
                for i, item in enumerate(items):
                    writer.writerow([i + 1] + item + [key])
        if args.output is None:
            print(writer.read())
        return

    res = []
    for key, items in segments.items():
        sounds = Table('number', 'sound', 'clpa', 'frequency')
        for i, item in enumerate(items):
            sounds.append([i + 1] + item)
        res.append('\n# {0} sounds\n\n{1}'.format(
            key.capitalize(), sounds.render(condensed=False)))
    res = '\n'.join(res)
    if args.output:
        with Path(args.output).open('w', encoding='utf8') as fp:
            fp.write(res)
    else:
        print(res)


@command()
def check(args):
    """
    clpa check <STRING>
    """
    if len(args.args) != 1:
        raise ParserError('only one argument allowed')
    check = check_string(args.args[0], load_whitelist())
    print('\t'.join(args.args[0].split(' ')))
    print('\t'.join(check))


def main(args=None):
    parser = ArgumentParser('pyclpa', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "-d", "--delimiter",
        help="Delimiting character of the input file.\n(default: <tab>)",
        default="\t")
    parser.add_argument(
        "-o", "--output",
        help="Output file.",
        default=None)
    parser.add_argument(
        "-r", "--rules",
        help="Rules file.",
        default=None)
    parser.add_argument(
        "-c", "--column",
        help="Delimiting character of the input file.\n(default: TOKENS)",
        default="TOKENS")
    parser.add_argument(
        "--format",
        help="Output format for the report.\n(default: md)",
        choices=['md', 'csv', 'cldf'],
        default="md")

    res = parser.main(args=args)
    if args is None:  # pragma: no cover
        sys.exit(res)
