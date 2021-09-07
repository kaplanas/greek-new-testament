from os import listdir
from nltk.grammar import FeatureGrammar
from nltk.parse.featurechart import FeatureChartParser

GRAMMAR_DIR = '../parsing/grammar/'
LEXICON_FILE = 'lexicon.fcfg'
PARSER = FeatureChartParser(FeatureGrammar.fromstring('\n'.join([open(GRAMMAR_DIR + f,
                                                                      'r').read()
                                                                 for f in listdir(GRAMMAR_DIR)])))
