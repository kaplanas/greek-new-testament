import pickle
import pandas as pd
from texttable import Texttable
from text_and_vocab import load_text_df, load_text_tagged
from parsing.utils import PARSER, VERBOSE_PARSER

SAVED_PARSES_FILE = '../parsing/saved_parses/saved_parses'


def attempt_to_parse(s):
    """Attempt to parse a sentence."""
    try:
        return PARSER.parse(s)
    except:
        return None


def parse_sents(sent_length=1):
    """Parse as many sentences as possible."""
    # Load the text.
    nt = load_text_tagged()
    ts = nt.tagged_sents(refs=True)
    # Filter to sentences of the specified length.
    ts = [sent for sent in ts if len(sent[1]) == sent_length]
    parses = []
    for sent in ts:
        ap = attempt_to_parse([w + '_' + m
                               for (w, m) in sent[1]])
        trees = []
        if ap is not None:
            trees = [tree for tree in ap]
            if len(trees) == 0:
                trees = []
        parses.append((sent[0],
                       ' '.join(w for w, _ in sent[1]),
                       [w + '_' + m for w, m in sent[1]],
                       trees))
    return parses


def get_unambiguous_sents(parses):
    """Get sentences with exactly one parse."""
    if len(parses) == 0:
        return []
    else:
        return [p for p in parses if len(p[3]) == 1]


def get_ambiguous_sents(parses):
    """Get sentences with more than one parse."""
    if len(parses) == 0:
        return []
    else:
        return [p for p in parses if len(p[3]) > 1]


def get_parsed_sents(parses):
    """Get sentences with at least one parse."""
    if len(parses) == 0:
        return []
    else:
        return [p for p in parses if len(p[3]) > 0]


def get_unparsed_sents(parses):
    """Get sentences with no parse."""
    if len(parses) == 0:
        return []
    else:
        return [p for p in parses if len(p[3]) == 0]


def get_sent_ids(parses):
    """Get a list of just references and wordforms, to uniquely identify a sentence."""
    if len(parses) == 0:
        return []
    else:
        return [(p[0], p[1]) for p in parses]


def get_parses_filename(filename=SAVED_PARSES_FILE, sent_length=None):
    """Get the filename for saved parses of a given length."""
    parses_filename = filename
    if sent_length is not None:
        parses_filename = parses_filename + '_' + str(sent_length)
    parses_filename = parses_filename + '.pickle'
    return parses_filename


def save_parses(parses, filename=SAVED_PARSES_FILE, include_count=True):
    """Save parses as a pickle file."""
    for k, v in parses.items():
        sent_length = None
        if include_count:
            sent_length = len(parses[k][0][2])
        with open(get_parses_filename(filename, sent_length), 'wb') as file:
            pickle.dump(parses[k], file)


def load_parses(filename=SAVED_PARSES_FILE, sent_length=None):
    """Load the saved parses from a pickle file."""
    try:
        with open(get_parses_filename(filename, sent_length), 'rb') as file:
            parses = pickle.load(file)
    except:
        parses = []
    return parses


def show_parses(parses, ref):
    """Show the parse trees of a sentence, IDed by its scripture reference."""
    for parse in parses:
        if parse[0] == ref:
            for tree in parse[3]:
                print(tree)


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    sent_lengths = [1, 2, 3, 4]
    old_parses = {}
    parses = {}
    changes = {}
    for sl in sent_lengths:
        old_parses[sl] = load_parses(sent_length=sl)
        old_sis = get_sent_ids(old_parses[sl])
        parses[sl] = parse_sents(sent_length=sl)
        sis = get_sent_ids(parses[sl])
        changes[sl] = {}
        for i, p in enumerate(parses[sl]):
            num_parses = len(p[3])
            if not num_parses in changes[sl].keys():
                changes[sl][num_parses] = {'fewer': [], 'same': [], 'more': []}
            num_old_parses = len(old_parses[sl][old_sis.index(sis[i])][3])
            if num_parses < num_old_parses:
                changes[sl][num_parses]['fewer'].append(p)
            elif num_parses == num_old_parses:
                changes[sl][num_parses]['same'].append(p)
            else:
                changes[sl][num_parses]['more'].append(p)
        print('*** Sentences of length ' + str(sl) + ' ***')
        t = Texttable()
        t.header(['Change'] + sorted(str(k) + ' parse' + '' if k == 1
                                     else str(k) + ' parses'
                                     for k in changes[sl].keys()))
        t.add_rows([[diff] +
                    [str(len(changes[sl][np][diff]))
                     for np in sorted(changes[sl].keys())]
                    for diff in ['fewer', 'same', 'more']], header=False)
        t.set_cols_align(['l'] + ['r' for i in range(len(changes[sl].keys()))])
        t.set_deco(Texttable.HEADER)
        print(t.draw())
        print('')
