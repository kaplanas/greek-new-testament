import os
import pymysql
import re
import pandas as pd
from bs4 import BeautifulSoup

RAW_DATA_DIR = 'perseus/'
ASCII_UNICODE_MAPPING = [('\\*\\(/a\\|', 'ᾍ'),
                         ('\\*\\)/a', 'Ἄ'), ('\\*\\)=a', 'Ἆ'), ('\\*\\(/a', 'Ἅ'), ('a\\)/=', 'ἄ῀'), ('a\\)=\\|', 'ᾆ'),
                         ('a\\(/=', 'ἅ῀'), ('a\\(/\\|', 'ᾅ'), ('a\\(=\\|', 'ᾇ'), ('a\\)/\\|', 'ᾄ'),
                         ('\\*\\)a', 'Ἀ'), ('\\*a\\)', 'Ἀ'), ('\\*\\(a', 'Ἁ'), ('a\\)/', 'ἄ'), ('a/\\)', 'ἄ'),
                         ('a\\)\\\\', 'ἂ'), ('a\\)=', 'ἆ'), ('a=\\)', 'ἆ'), ('a\\+\\)', 'ἀ̈'), ('a\\(/', 'ἅ'),
                         ('a\\(\\\\', 'ἃ'), ('a\\(=', 'ἇ'), ('a\\)\\|', 'ᾀ'), ('a/\\|', 'ᾴ'), ('a=\\|', 'ᾷ'),
                         ('a\\+/', 'ά̈'), ('a/\\+', 'ά̈'),
                         ('\\*a', 'Ἀ'), ('a\\)', 'ἀ'), ('a\\(', 'ἁ'), ('a/', 'ά'), ('a\\\\', 'ὰ'), ('a=', 'ᾶ'),
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
ASCII_UNICODE_ALPHABETIZATION_MAPPING = {'a': 'α', 'b': 'β', 'g': 'γ', 'd': 'δ', 'e': 'ε', 'z': 'ζ', 'h': 'η', 'q': 'θ',
                                         'i': 'ι', 'k': 'κ', 'l': 'λ', 'm': 'μ', 'n': 'ν', 'c': 'ξ', 'o': 'ο', 'p': 'π',
                                         'r': 'ρ', 's': 'σ', 't': 'τ', 'u': 'υ', 'f': 'φ', 'x': 'χ', 'y': 'ψ', 'w': 'ω'}


def ascii_to_unicode(ascii_string):
    """Convert an ASCII representation of Greek to Unicode."""
    unicode = ascii_string
    for a, u in ASCII_UNICODE_MAPPING:
        if bool(re.search(a, unicode)):
            unicode = re.sub(a, u, unicode)
    return unicode


def process_entries():
    """Load the xml of the LSJ entries."""
    with open(RAW_DATA_DIR + 'lsj_perseus.xml') as lsj:
        soup = BeautifulSoup(lsj, features='lxml')
        e_df = pd.DataFrame([(e['key'],
                              e.form.orth.text,
                              '; '.join([s.text for s in e.find_all('trans')]))
                             for e in soup.find_all('entry')],
                            columns=['lemma_key', 'lemma_ascii', 'definition'])
        e_df['lemma'] = e_df['lemma_ascii'].apply(ascii_to_unicode)
        e_df['lemma_sort'] = e_df['lemma_ascii']
        e_df.lemma_sort = e_df.lemma_sort.replace({'[^abgdezhqiklmncoprstufxyw]': ''}, regex = True)
        e_df.lemma_sort = e_df.lemma_sort.replace(ASCII_UNICODE_ALPHABETIZATION_MAPPING,  regex = True)
        return e_df


if __name__ == '__main__':

    # Get lexicon entries.
    pd.set_option('display.max_columns', None)
    entries_df = process_entries()

    # Connect to the database.
    connection = pymysql.connect(host='localhost', user='root', password=os.environ['MYSQL_PASSWORD'], database='gnt')

    # Get lemmas that are present in the NT.
    sql = "SELECT DISTINCT Lemma FROM words"
    nt_lemmas_df = pd.read_sql(sql, connection)
    entries_df = entries_df.merge(nt_lemmas_df, left_on=['lemma'], right_on=['Lemma'])

    # Get one definition for each lemma.
    entries_df = entries_df[['lemma', 'lemma_sort', 'definition']]
    entries_df = entries_df.groupby(['lemma', 'lemma_sort']).agg('; '.join)
    entries_list = list(entries_df.to_records())
    entries_list = [tuple(el) for el in entries_list]

    # Write lemmas to the database.
    with connection.cursor() as cur:
        sql = """INSERT INTO lemmas
                 (Lemma, LemmaSort, ShortDefinition)
                 VALUES
                 (%s, %s, %s)"""
        cur.executemany(sql, entries_list)
    connection.commit()

    # Close the database connection.
    connection.close()
