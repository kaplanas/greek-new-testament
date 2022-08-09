import re
import pickle
import pandas as pd
import termtables
from yachalk import chalk
from nltk.tree import Tree
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


def print_parse(tree, features=False, margin=70, indent=0, nodesep="",
                parens="[]", quotes=False, top_level=True):
    """Pretty-print parse trees WITHOUT feature info."""
    if features:
        parens = "()"
    if isinstance(tree._label, str):
        label_to_print = tree._label
    else:
        label_to_print = repr(tree._label)
    if not features:
        label_to_print = re.sub('\[[^/]*\]', '', label_to_print)
    s = f"{parens[0]}{label_to_print}{nodesep}"
    if features:
        new_indent = indent + 2
    else:
        new_indent = indent + len(label_to_print) + 2
    for child_i, child in enumerate(tree):
        if features:
            child_sep = "\n" + " " * (indent + 2)
        elif child_i == 0:
            child_sep = " "
        else:
            child_sep = "\n" + " " * new_indent
        if isinstance(child, Tree):
            s += (
                child_sep
                + print_parse(child, features, margin, new_indent, nodesep,
                              parens, quotes, top_level=False)
            )
        elif isinstance(child, tuple):
            s += child_sep + "/".join(child)
        elif isinstance(child, str) and not quotes:
            s += child_sep
            s += "%s" % chalk.blue(repr(child))
        else:
            if features:
                s += child_sep
            else:
                s += " "
            s += chalk.blue(repr(child))
    if top_level:
        print(s + parens[1])
    else:
        return s + parens[1]


def print_parses(parses, features=False):
    """Show the parse trees of a set of parses."""
    for i, parse in enumerate(parses):
        print('*** [' + str(i) + '] ' + parse[0] + ' - ' + parse[1] + ' ***')
        print('')
        for tree in parse[3]:
            print_parse(tree, features)
            print('')


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    chalk.enable_full_colors()
    sent_lengths = [1, 2, 3, 4, 5]
    # sent_lengths = [4, 5]
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
            num_old_parses = 0
            if sis[i] in old_sis:
                num_old_parses = len(old_parses[sl][old_sis.index(sis[i])][3])
            if num_parses < num_old_parses:
                changes[sl][num_parses]['fewer'].append(p)
            elif num_parses == num_old_parses:
                changes[sl][num_parses]['same'].append(p)
            else:
                changes[sl][num_parses]['more'].append(p)
        print('*** Sentences of length ' + str(sl) + ' ***')
        termtables.print([[diff] +
                          [str(chalk.red(str(len(changes[sl][np][diff]))))
                           if diff in ['fewer', 'more'] and len(changes[sl][np][diff]) > 0
                           else str(len(changes[sl][np][diff]))
                           for np in sorted(changes[sl].keys())]
                          for diff in ['fewer', 'same', 'more']],
                         header=['Change'] + [str(k) + ' parse' + '' if k == 1
                                              else str(k) + ' parses'
                                              for k in sorted(changes[sl].keys())],
                         style=termtables.styles.markdown,
                         padding=(0, 1),
                         alignment='l' + ('r' * len(changes[sl])))
        print('')
