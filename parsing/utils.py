from os import listdir
from nltk.grammar import FeatureGrammar
from nltk.parse.featurechart import FeatureChartParser

GRAMMAR_DIR = '../parsing/grammar/'
LEXICON_FILE = 'lexicon.fcfg'
GRAMMAR = FeatureGrammar.fromstring('\n'.join([open(GRAMMAR_DIR + f,
                                                    'r').read()
                                               for f in listdir(GRAMMAR_DIR)]))
PARSER = FeatureChartParser(GRAMMAR)
VERBOSE_PARSER = FeatureChartParser(GRAMMAR, trace=1)