Cross-Linguistic Phonetic Alphabet
==================================

This is an attempt to create a cross-linguistic phonetic alphabet, realized as
a dialect of IPA, which can be used for cross-linguistic approaches to language
comparison.

The basic idea is to provide a fixed set of symbols for phonetic representation
along with a full description regarding their pronunciation following the
tradition of IPA. This list is essentially expandable, when new languages
arise, and it can be linked to alternative datasets, like Mielke's (2008)
P-Base, and Phoible.

In addition to the mere description of symbols, we provide also a range of
scripts that can be used in order to test how well a dataset reflects our
cross-linguistic standard, and to which degree it diverges from it. In this
way, linguists who want to publish their data in phonetic transcriptions that
follow a strict standard, they can use our tools and map their data to CLPA. In
this way, by conforming to our whitelist (and informing us in cases where we
miss important sounds that are essential for the description of a dataset so
that we can expand the CLPA), the community can make sure that we have a
maximal degree of comparability across lexical datasets. 

## The initial dataset

Our [initial dataset](clpa/clpa.tsv) currently consists of 1192 symbols, including consonants,
vowels, diphtongs, tones, and three markers (for word and morpheme boundaries).
The original data is inspired by the IPA description used in the P-Base
project, and we mostly follow their symbol conventions, but we added tone
letters and symbols which were missing in their inventory.

Additionally, the dataset contains sets of instructions for conversion of symbols which do not occur in our whitelist. Here, we distinguish between:

* [explitic mappings](clpa/explicit.tsv), which are explicit mappings of input segments with output segments, which are taken in full. As an example, consider [ʔʲ] which we map to [ʔj], or [uu], which we map to [uː].
* [alias symbols](clpa/alias.tsv), which are one-to-more mappings of symbols of length 1 in unicode, and are regularly applied to a symbol if we can't find it in our whitelist. As an example, consider [ʦ] which we map to [ts].
* [symbols to be ignored](clpa/delete.tsv), which are symbols of length 1 which we ignore from the input data and then check whether we can find a mapping. As a an example, compare the combinging mark in the symbols [t͡s], which we delete in order to map to our [ts].
* [symbols to be converted as patterns](clpa/patterns.tsv): these are potentially riscant operations which we try to minimize as well as possible, but there are situations in which it is useful to apply changes on a pattern basis, as for example, in datasets in which "aspiration" is not marked by a superscript letter, where we would then turn every instance of plosive + h into plosive + ʰ

## Testing the conversion procedure

In order to test the current conversion procedure, run 

```shell

python3 test.py INPUTFILE.tsv
```

in the shell. Your inputfile should be a tab-separated file in [LingPy-Wordlist format](http://lingpy.org/tutorial/lingpy.basic.wordlist.html), with your phonetic sequences being represented as space-segmented values in a column "TOKENS" of the input file. This is a mere proof-of-concept at the moment, and the script will be further enhanced. 


