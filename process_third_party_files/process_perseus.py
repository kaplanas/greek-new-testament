import os
import pymysql
import re
import pandas as pd
from ast import literal_eval

RAW_DATA_DIR = 'perseus/'
TEXT_DATA_DIR = '../text_data/'
ASCII_UNICODE_MAPPING = [('\\*\\(/a\\|', 'ᾍ'),
                         ('\\*\\)/a', 'Ἄ'), ('\\*\\)=a', 'Ἆ'), ('\\*\\(/a', 'Ἅ'), ('a\\)/=', 'ἄ῀'), ('a\\)=\\|', 'ᾆ'),
                         ('a\\(/=', 'ἅ῀'), ('a\\(/\\|', 'ᾅ'), ('a\\(=\\|', 'ᾇ'), ('a\\)/\\|', 'ᾄ'),
                         ('\\*\\)a', 'Ἀ'), ('\\*a\\)', 'Ἀ'), ('\\*\\(a', 'Ἁ'), ('a\\)/', 'ἄ'), ('a/\\)', 'ἄ'),
                         ('a\\)\\\\', 'ἂ'), ('a\\)=', 'ἆ'), ('a=\\)', 'ἆ'), ('a\\+\\)', 'ἀ̈'), ('a\\(/', 'ἅ'),
                         ('a\\(\\\\', 'ἃ'), ('a\\(=', 'ἇ'), ('a\\)\\|', 'ᾀ'), ('a/\\|', 'ᾴ'), ('a=\\|', 'ᾷ'),
                         ('a\\+/', 'ά̈'), ('a/\\+', 'ά̈'),
                         ('\\*a', 'Ἀ'), ('a\\)', 'ἁ'), ('a\\(', 'ἁ'), ('a/', 'ά'), ('a\\\\', 'ὰ'), ('a=', 'ᾶ'),
                         ('a\\|', 'ᾳ'), ('a\\+', 'α̈'),
                         ('a', 'α'),
                         ('\\*b', 'Β'), ('b', 'β'),
                         ('\\*g', 'Γ'), ('g', 'γ'),
                         ('\\*d', 'Δ'), ('d', 'δ'),
                         ('\\*\\)/e', 'Ἔ'), ('\\*\\(/e', 'Ἕ'),
                         ('\\*\\)e', 'Ἐ'), ('\\*\\(e', 'Ἑ'), ('e\\)/', 'ἔ'), ('e\\)\\\\', 'ἒ'), ('e\\)=', 'ἐ῀'),
                         ('e\\(/', 'ἕ'),
                         ('\\*e', 'Ε'), ('e\\)', 'ἐ'), ('e\\(', 'ἑ'), ('e/', 'έ'), ('e\\\\', 'ὲ'), ('e=', 'ε῀'),
                         ('e', 'ε'),
                         ('\\*z', 'Ζ'), ('z', 'ζ'),
                         ('\\*\\(/h', 'Ἥ'), ('h\\)/=', 'ή῀'), ('h\\)/\\|', 'ᾔ'), ('h\\)=\\|', 'ᾖ'), ('h\\(/\\|', 'ᾕ'),
                         ('h\\(=\\|', 'ᾗ'),
                         ('\\*\\)h', 'Ἠ'), ('\\*\\(h', 'Ἡ'), ('h\\)/', 'ἤ'), ('h\\)=', 'ἦ'), ('h\\)\\|', 'ᾐ'),
                         ('h\\(/', 'ἥ'), ('h\\(=', 'ἧ'), ('h=\\(', 'ἧ'), ('h\\(\\|', 'ᾑ'), ('h/\\|', 'ῄ'),
                         ('h\\|/', 'ῄ'), ('h=\\|', 'ῇ'),
                         ('h\\)', 'ἠ'), ('h\\(', 'ἡ'), ('h/', 'ή'), ('h\\\\', 'ὴ'), ('h=', 'ῆ'), ('h\\|', 'ῃ'),
                         ('h', 'η'),
                         ('\\*q', 'Θ'), ('q', 'θ'),
                         ('\\*\\)/i', 'Ἴ'), ('\\*\\)=i', 'Ἶ'), ('i\\)/=', 'ἴ῀'), ('i\\)/\\+', 'ΐ᾿'),
                         ('\\*\\)i', 'Ἰ'), ('i\\)/', 'ἴ'), ('i\\)=', 'ἶ'), ('i\\)\\+', 'ϊ᾿'), ('i\\+\\)', 'ϊ᾿'),
                         ('i\\(/', 'ἵ'), ('i\\(=', 'ἷ'), ('i/=', 'ί῀'), ('i/\\+', 'ΐ'), ('i\\+/', 'ΐ'), ('i=\\+', 'ῗ'),
                         ('i\\+=', 'ῗ'),
                         ('i\\)', 'ἰ'), ('i\\(', 'ἱ'), ('i/', 'ί'), ('i\\\\', 'ὶ'), ('i=', 'ῖ'), ('i\\+', 'ϊ'),
                         ('i', 'ι'),
                         ('\\*k', 'Κ'), ('k', 'κ'),
                         ('\\*l', 'Λ'), ('l', 'λ'),
                         ('\\*m', 'Μ'), ('m', 'μ'),
                         ('\\*n', 'Ν'), ('n=', 'ν'), ('n', 'ν'),
                         ('\\*c', 'Ξ'), ('c', 'ξ'),
                         ('\\*\\)/o', 'Ὄ'), ('\\*\\(/', 'Ὅ'), ('o\\)/\\+', 'ὄ̈'),
                         ('\\*\\)o', 'Ὀ'), ('\\*\\(o', 'Ὁ'), ('\\*o\\)', 'Ὀ'), ('o\\)/', 'ὄ'), ('o/\\)', 'ὄ'),
                         ('o\\)\\\\', 'ὂ'), ('o\\(/', 'ὅ'), ('o\\(=', 'ὁ῀'), ('o/=', 'ό῀'),
                         ('\\*o', 'Ο'), ('o\\)', 'ὀ'), ('o\\(', 'ὁ'), ('o/', 'ό'), ('o\\\\', 'ὸ'), ('o=', 'ο῀'),
                         ('o\\|', 'οι'), ('o\\+', 'ο̈'),
                         ('o', 'ο'),
                         ('\\*p', 'Π'), ('p', 'π'),
                         ('\\*\\)r', 'Ρ᾿'), ('\\*\\(r', 'Ῥ'), ('r\\)', 'ῤ'), ('r\\(', 'ῥ'), ('r', 'ρ'),
                         ('\\*s', 'Σ'), ('s\\|?$', 'ς'), ('s', 'σ'),
                         ('t=\\|', 't'), ('\\*t', 'Τ'), ('t/', 't'), ('t', 'τ'),
                         ('u\\(==', 'ὗ'),
                         ('\\*\\(u', 'Ὑ'), ('u\\)/', 'ὔ'), ('u\\)\\\\', 'ὒ'), ('u\\)=', 'ὖ'), ('u\\(/', 'ὕ'),
                         ('u\\(=', 'ὗ'), ('u/\\+', 'ΰ'), ('u\\+/', 'ΰ'), ('u\\+=', 'ῧ'), ('u=\\+', 'ῧ'),
                         ('u\\)', 'ὐ'), ('u\\(', 'ὑ'), ('u/', 'ύ'), ('u=', 'ῦ'), ('u\\+', 'ϋ'),
                         ('u', 'υ'),
                         ('\\*f', 'Φ'), ('f', 'φ'),
                         ('\\*x', 'Χ'), ('x', 'χ'),
                         ('\\*y', 'Ψ'), ('y', 'ψ'),
                         ('\\*\\)/w', 'Ὤ'), ('w\\)/\\|', 'ᾤ'), ('w\\)=\\|', 'ᾦ'), ('w\\(=\\|', 'ᾧ'),
                         ('\\*\\)w', 'Ὠ'), ('w\\)/', 'ὤ'), ('w\\)=', 'ὦ'), ('w\\)\\|', 'ᾠ'), ('w\\(/', 'ὥ'),
                         ('w\\(=', 'ὧ'), ('w\\(\\|', 'ᾡ'), ('w/\\|', 'ῴ'), ('w=\\|', 'ῷ'), ('w\\|=', 'ῷ'),
                         ('\\*w', 'Ω'), ('w\\(', 'ὡ'), ('w\\)', 'ὠ'), ('w/', 'ώ'), ('w=', 'ῶ'), ('w\\|', 'ῳ'),
                         ('w', 'ω'),
                         ('^/', ''), ('^=', ''), ('/$', '')]
INT_REGEX = '[0-9]+'
GREEK_REGEX = "'[a-z()\\\\\\/=*+|]+'"
ENGLISH_REGEX = "'[A-Za-z(),;.:?!\"\\\\\\/' ]+'"
MORPH_REGEX = "'[-a-z]{9}'"
POS_CODES = {'l': 'article',
             'p': 'pronoun',
             'd': 'adverb',
             'n': 'noun',
             'a': 'adjective',
             't': 'participle',
             'v': 'verb',
             'm': 'numeral',
             'r': 'preposition',
             'x': 'irregular',
             'c': 'conjunction',
             'g': 'particle',
             'e': 'exclamation'}
NUMBER_CODES = {'s': 'singular',
                'p': 'plural',
                'd': 'dual'}
TENSE_CODES = {'a': 'aorist',
               'p': 'present',
               'f': 'future',
               'r': 'perfect',
               't': 'future perfect',
               'i': 'imperfect',
               'l': 'pluperfect'}
MOOD_CODES = {'n': 'infinitive',
              'm': 'imperative',
              'i': 'indicative',
              's': 'subjunctive',
              'o': 'optative',
              'p': 'participle',
              'g': 'gerundive'}
VOICE_CODES = {'a': 'active',
               'e': 'mediopassive',
               'm': 'middle',
               'p': 'passive',
               'd': 'deponent'}
GENDER_CODES = {'f': 'feminine',
                'm': 'masculine',
                'n': 'neuter'}
CASE_CODES = {'n': 'nominative',
              'v': 'vocative',
              'g': 'genitive',
              'd': 'dative',
              'a': 'accusative',
              'b': 'ablative',
              'l': 'locative',
              'i': 'instrumental'}
DEGREE_CODES = {'c': 'comparative',
                's': 'superlative'}


def ascii_to_unicode(ascii_string):
    """Convert an ASCII representation of Greek to Unicode."""
    unicode = ascii_string
    for a, u in ASCII_UNICODE_MAPPING:
        if bool(re.search(a, unicode)):
            unicode = re.sub(a, u, unicode)
    return unicode


def possible_null(r):
    """Add to a regex to allow the value to be null."""
    return '(?:(?:' + r + ')|NULL)'


def process_lemmas():
    """Parse the MySQL dump of lemmas."""

    # Get the text from the MySQL dump.
    dump = open(RAW_DATA_DIR + 'hib_lemmas.sql', 'r')
    dump_lines = dump.readlines()
    dump.close()

    # Use regexes to parse rows as tuples and insert them into a dataframe.
    regex = re.compile('\\(' + \
                       ','.join([INT_REGEX, possible_null(GREEK_REGEX),
                                 possible_null(GREEK_REGEX),
                                 possible_null(INT_REGEX),
                                 possible_null(INT_REGEX),
                                 possible_null(ENGLISH_REGEX)]) + \
                       '\\)')
    lemmas_df = pd.DataFrame([literal_eval(re.sub('NULL', 'None', row))
                              for line in dump_lines
                              if line.startswith('INSERT INTO')
                              for row in regex.findall(line)],
                             columns=['lemma_id', 'lemma_text_ascii', 'bare_headword', 'lemma_sequence_number',
                                      'lemma_lang_id', 'lemma_short_def'])
    lemmas_df['lemma_text'] = lemmas_df['lemma_text_ascii'].apply(ascii_to_unicode)

    # Remove lemmas from languages other than Greek.  Drop unneeded columns.
    lemmas_df = lemmas_df[lemmas_df.lemma_lang_id == 2]
    lemmas_df.drop(['bare_headword', 'lemma_sequence_number',
                    'lemma_lang_id'], axis=1, inplace=True)

    # Remove lemmas without definitions.
    lemmas_df = lemmas_df[~lemmas_df.lemma_short_def.isnull()]

    # All done; return the dataframe.
    return lemmas_df


def process_parses():
    """Parse the MySQL dump of parsed forms."""

    # Get the text from the MySQL dump.
    dump = open(RAW_DATA_DIR + 'hib_parses.sql', 'r')
    dump_lines = dump.readlines()
    dump.close()

    # Use regexes to parse rows as tuples and insert them into a dataframe.
    regex = re.compile('\\(' + \
                       ','.join([INT_REGEX, INT_REGEX,
                                 possible_null(MORPH_REGEX),
                                 possible_null(GREEK_REGEX), GREEK_REGEX,
                                 possible_null(GREEK_REGEX),
                                 possible_null(ENGLISH_REGEX),
                                 possible_null(ENGLISH_REGEX)]) + \
                       '\\)')
    parses_df = pd.DataFrame([literal_eval(re.sub('NULL', 'None', row))
                              for line in dump_lines
                              if line.startswith('INSERT INTO')
                              for row in regex.findall(line)],
                             columns=['id', 'lemma_id', 'morph_code', 'expanded_form_ascii', 'form', 'bare_form',
                                      'dialects', 'misc_features'])
    parses_df['expanded_form'] = parses_df['expanded_form_ascii'].apply(ascii_to_unicode)

    # Remove parsed forms that aren't in the table of lemmas.  (This mostly
    # removes non-Greek forms; some others might be eliminated as well.)
    lemmas_df = process_lemmas()
    parses_df = parses_df.merge(lemmas_df[['lemma_id']], on=['lemma_id'])

    # Part of speech and parsing codes.
    parses_df['pos'] = parses_df.iloc[:, 2].str[0].map(POS_CODES)
    parses_df['number'] = parses_df.iloc[:, 2].str[2].map(NUMBER_CODES)
    parses_df['tense'] = parses_df.iloc[:, 2].str[3].map(TENSE_CODES)
    parses_df['mood'] = parses_df.iloc[:, 2].str[4].map(MOOD_CODES)
    parses_df['voice'] = parses_df.iloc[:, 2].str[5].map(VOICE_CODES)
    parses_df['gender'] = parses_df.iloc[:, 2].str[6].map(GENDER_CODES)
    parses_df['case'] = parses_df.iloc[:, 2].str[7].map(CASE_CODES)
    parses_df['degree'] = parses_df.iloc[:, 2].str[8].map(DEGREE_CODES)

    # Drop unneeded columns.
    parses_df.drop(['id', 'morph_code', 'form', 'bare_form'],
                   axis=1, inplace=True)

    # All done; return the dataframe.
    return parses_df



if __name__ == '__main__':

    # Get lemmas and parses.
    pd.set_option('display.max_columns', None)
    lemmas_df = process_lemmas()
    # parses_df = process_parses()

    # Connect to the database.
    connection = pymysql.connect(host='localhost', user='root', password=os.environ['MYSQL_PASSWORD'], database='gnt')

    # Get lemmas that are present in the NT.
    sql = "SELECT DISTINCT Lemma FROM words"
    nt_lemmas_df = pd.read_sql(sql, connection)
    lemmas_df = lemmas_df.merge(nt_lemmas_df, left_on=['lemma_text'], right_on=['Lemma'])

    # Get one definition for each lemma.
    lemmas_df = lemmas_df[['lemma_text', 'lemma_short_def']]
    lemmas_df = lemmas_df.groupby('lemma_text').agg('; '.join)
    lemmas_list = list(lemmas_df.to_records())
    lemmas_list = [tuple(ll) for ll in lemmas_list]

    # Write lemmas to the database.
    with connection.cursor() as cur:
        sql = """INSERT INTO lemmas
                 (Lemma, ShortDefinition)
                 VALUES
                 (%s, %s)"""
        cur.executemany(sql, lemmas_list)
    connection.commit()

    # Close the database connection.
    connection.close()
