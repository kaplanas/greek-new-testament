import re
from os import listdir
from typed_dependencies import TypedDependencyGrammar, TypedNonprojectiveDependencyParser

GRAMMAR_DIR = '../parsing/grammar/'
LEXICON_FILE = 'lexicon.fcfg'

def load_grammar():
    g = TypedDependencyGrammar.fromstring('\n'.join([open(GRAMMAR_DIR + f, 'r').read()
                                                     for f in listdir(GRAMMAR_DIR)
                                                     if re.match('.*\.dg', f)]))
    g.load_lexicon(open(GRAMMAR_DIR + '/' + LEXICON_FILE, 'r').read())
    p = TypedNonprojectiveDependencyParser(g)
    return g, p

GRAMMAR, PARSER = load_grammar()
