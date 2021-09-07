from text_and_vocab import load_text_tagged
from file_locs import PARSER


# Get the shortest sentences (by word count).
def get_shortest_sents():
    """Get the shortest sentences, by word count."""
    nt = load_text_tagged()
    ts = nt.tagged_sents(refs=True)
    return sorted(ts, key=lambda s: len(s[1]))


# Attempt to parse a sentence; return None if unsuccessful.
def attempt_to_parse(s):
    """Attempt to parse a sentence."""
    try:
        return PARSER.parse(s)
    except:
        return None


# Get trees for parsable sentences and a list of unparsable sentences.
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


if __name__ == '__main__':
    nt = load_text_tagged()
    parses = parse_sents()
