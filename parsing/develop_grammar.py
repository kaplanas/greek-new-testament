import pickle
from text_and_vocab import load_text_tagged
from file_locs import PARSER

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


if __name__ == '__main__':
    sent_lengths = [1, 2]
    old_parses = {}
    parses = {}
    new_unamb = {}
    new_amb_p = {}
    new_amb_up = {}
    new_unparsed = {}
    for sl in [str(sent_length) for sent_length in sent_lengths]:
        old_parses[sl] = load_parses(sent_length=int(sl))
        parses[sl] = parse_sents(sent_length=int(sl))
        new_unamb[sl] = [s
                         for s in get_sent_ids(get_unambiguous_sents(parses[sl]))
                         if s in get_sent_ids(get_unparsed_sents(old_parses[sl]))]
        new_amb_p[sl] = [s
                         for s in get_sent_ids(get_ambiguous_sents(parses[sl]))
                         if s in get_sent_ids(get_parsed_sents(old_parses[sl]))]
        new_amb_up[sl] = [s
                          for s in get_sent_ids(get_ambiguous_sents(parses[sl]))
                          if s in get_sent_ids(get_unparsed_sents(old_parses[sl]))]
        new_unparsed[sl] = [s
                            for s in get_sent_ids(get_unparsed_sents(parses[sl]))
                            if s in get_sent_ids(get_parsed_sents(old_parses[sl]))]
        print('*** Sentences of length ' + str(sl)  + ' ***')
        print('PARSED: ' + str(len(get_unambiguous_sents(parses[sl]))) +
              ' (' + str(len(new_unamb[sl])) + ' new)')
        print('AMBIGUOUS: ' + str(len(get_ambiguous_sents(parses[sl]))) +
              ' (' + str(len(new_amb_p[sl])) + ' previously parsed, ' +
              str(len(new_amb_up[sl])) + ' previously unparsed)')
        print('UNPARSED: ' + str(len(get_unparsed_sents(parses[sl]))) +
              ' (' + str(len(new_unparsed[sl])) + ' previously parsed)')
        print('')
