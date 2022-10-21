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
POS_CODES = bidict({'noun': 'N',
                    'relative pronoun': 'R',
                    'verb': 'V',
                    'personal pronoun': 'E',
                    'definite article': 'D',
                    'preposition': 'P',
                    'conjunction': 'C',
                    'conjunction A': 'a',
                    'conjunction B': 'b',
                    'conjunction C': 'c',
                    'conjunction E': 'e',
                    'conjunction I': 'i',
                    'conjunction L': 'l',
                    'conjunction N': 'n',
                    'conjunction P': 'p',
                    'conjunction V': 'v',
                    'adjective': 'A',
                    'adverb': 'B',
                    'particle': 'L',
                    'demonstrative pronoun': 'M',
                    'interrogative/indefinite pronoun': 'I',
                    'interjection': 'J'})
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


def get_morph_codes(df_row):
    """Get morphological parsing codes for a wordform."""
    morph_codes = POS_CODES.get(df_row['pos'], '-') +\
                  PERSON_CODES.get(df_row['person'], '-') +\
                  TENSE_CODES.get(df_row['tense'], '-') +\
                  VOICE_CODES.get(df_row['voice'], '-') +\
                  MOOD_CODES.get(df_row['mood'], '-') +\
                  CASE_CODES.get(df_row['case'], '-') +\
                  NUMBER_CODES.get(df_row['number'], '-') +\
                  GENDER_CODES.get(df_row['gender'], '-')
    if df_row['pos'] == 'personal pronoun':
        morph_codes = morph_codes[0] + '-' + morph_codes[2:]
    return morph_codes