import numpy as np
from bidict import bidict

TEXT_DATA_DIR = '../text_data/'
TAGGED_CORPUS_DIR = 'nt_tagged/'
BOOK_MAPPING = bidict({pretty_book: pretty_book.lower().replace(' ', '_')
                       for pretty_book in ['Matthew', 'Mark', 'Luke', 'John',
                                           'Acts', 'Romans', '1 Corinthians',
                                           '2 Corinthians', 'Galatians',
                                           'Ephesians', 'Philippians',
                                           'Colossians', '1 Thessalonians',
                                           '2 Thessalonians', '1 Timothy',
                                           '2 Timothy', 'Titus', 'Philemon',
                                           'Hebrews', 'James', '1 Peter',
                                           '2 Peter', '1 John', '2 John',
                                           '3 John', 'Jude', 'Revelation']})
PERSON_CODES = bidict({i + 1: str(i + 1) for i in range(3)})
TENSE_CODES = bidict({'aorist': 'A',
                      'present': 'P',
                      'perfect': 'R',
                      'imperfect': 'I',
                      'future': 'F',
                      'pluperfect': 'L'})
VOICE_CODES = bidict({'active': 'A',
                      'middle': 'M',
                      'passive': 'P'})
MOOD_CODES = bidict({'indicative': 'I',
                     'infinitive': 'N',
                     'participle': 'P',
                     'imperative': 'M',
                     'subjunctive': 'S',
                     'optative': 'O'})
CASE_CODES = bidict({'nominative': 'N',
                     'genitive': 'G',
                     'accusative': 'A',
                     'dative': 'D',
                     'vocative': 'V'})
NUMBER_CODES = bidict({'singular': 'S',
                       'plural': 'P'})
GENDER_CODES = bidict({'masculine': 'M',
                       'feminine': 'F',
                       'neuter': 'N'})
