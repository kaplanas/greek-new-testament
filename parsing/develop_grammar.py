import pickle
from text_and_vocab import load_text_tagged
from file_locs import PARSER

SAVED_PARSES_FILE = 'saved_parses.pickle'


def get_shortest_sents():
    """Get the shortest sentences, by word count."""
    nt = load_text_tagged()
    ts = nt.tagged_sents(refs=True)
    return sorted(ts, key=lambda s: len(s[1]))


def attempt_to_parse(s):
    """Attempt to parse a sentence."""
    try:
        return PARSER.parse(s)
    except:
        return None


def parse_sents():
    """Parse as many sentences as possible."""
    unambiguous_parses = []
    ambiguous_parses = []
    no_parses = []
    for sent in get_shortest_sents():
        ap = attempt_to_parse([w + '_' + m
                               for (w, m) in sent[1]])
        trees = None
        if ap is not None:
            trees = [tree for tree in ap]
            if len(trees) == 0:
                trees = None
        if trees is None:
            no_parses.append((sent[0], sent[1], trees))
        elif len(trees) == 1:
            unambiguous_parses.append((sent[0], sent[1], trees[0]))
        else:
            ambiguous_parses.append((sent[0], sent[1], trees))
    return {'parsed': unambiguous_parses,
            'ambiguous': ambiguous_parses,
            'unparsed': no_parses}


def sentence_ids(parses):
    """Get a list of just references and wordforms, to uniquely identify a sentence."""
    return [(p[0], ' '.join([w for w, _ in p[1]]))
            for p in parses]


def save_parses(parses, filename=SAVED_PARSES_FILE):
    """Save parses as a pickle file."""
    with open(filename, 'wb') as file:
        pickle.dump(parses, file)


def load_parses(filename=SAVED_PARSES_FILE):
    """Load the saved parses from a pickle file."""
    with open(filename, 'rb') as file:
        parses = pickle.load(file)
    return parses


if __name__ == '__main__':
    old_parses = load_parses()
    parses = parse_sents()
    new_parses = [s
                  for s in sentence_ids(parses['parsed'])
                  if s not in sentence_ids(old_parses['parsed'])]
    new_ambiguous_previously_parsed = [s
                                       for s in sentence_ids(parses['ambiguous'])
                                       if s in sentence_ids(old_parses['parsed'])]
    new_ambiguous_previously_unparsed = [s
                                         for s in sentence_ids(parses['ambiguous'])
                                         if s in sentence_ids(old_parses['unparsed'])]
    new_unparsed = [s
                    for s in sentence_ids(parses['unparsed'])
                    if s not in sentence_ids(old_parses['unparsed'])]
    print('PARSED: ' + str(len(parses['parsed'])) +
          ' (' + str(len(new_parses)) + ' new)')
    print('AMBIGUOUS: ' + str(len(parses['ambiguous'])) +
          ' (' + str(len(new_ambiguous_previously_parsed)) + ' previously parsed, ' +
          str(len(new_ambiguous_previously_unparsed)) + ' previously unparsed)')
    print('UNPARSED: ' + str(len(parses['unparsed'])) +
          ' (' + str(len(new_unparsed)) + ' previously parsed)')
