import re
from os import listdir
from typed_dependencies import TypedDependencyGrammar, TypedNonprojectiveDependencyParser

GRAMMAR_DIR = '../parsing/grammar/'

def load_grammar():
    g = TypedDependencyGrammar.fromstring('\n'.join([open(GRAMMAR_DIR + f, 'r').read()
                                                     for f in listdir(GRAMMAR_DIR)
                                                     if re.match('.*\.dg', f)]))
    p = TypedNonprojectiveDependencyParser(g)
    return g, p

GRAMMAR, PARSER = load_grammar()
