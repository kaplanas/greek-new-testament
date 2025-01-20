import requests
import re
import pandas as pd
from bs4 import BeautifulSoup

RAW_DATA_DIR = 'katabiblon/'
TEXT_DATA_DIR = '../text_data/'
CHAPTER_ABBR_COUNTS = {
    'Genesis': ('Gn', 50),
    'Exodus': ('Ex', 40),
    'Leviticus': ('Lv', 27),
    'Numbers': ('Nm', 36),
    'Deuteronomy': ('Dt', 34),
    'Joshua': ('JoB', 24),
    'Judges A': ('JgsA', 21),
    'Judges B': ('JgsB', 21),
    'Ruth': ('Ru', 4),
    '1 Samuel': ('1Kgs', 31),
    '2 Samuel': ('2Kgs', 24),
    '1 Kings': ('3Kgs', 22),
    '2 Kings': ('4Kgs', 25),
    '1 Chronicles': ('1Chr', 29),
    '2 Chronicles': ('2Chr', 36),
    'Ezra-Nehemiah': ('2Esd', 23),
    'Esther': ('Est', 10),
    'Job': ('Jb', 42),
    'Psalms': ('Ps', 151),
    'Proverbs': ('Prv', 31),
    'Ecclesiastes': ('Qoh', 12),
    'Song of Solomon': ('Cant', 8),
    'Isaiah': ('Is', 66),
    'Jeremiah': ('Jer', 52),
    'Lamentations': ('Lam', 5),
    'Ezekiel': ('Ez', 48),
    'Daniel OG': ('DnOG', 12),
    'Daniel Th': ('DnTh', 12),
    'Hosea': ('Hos', 14),
    'Joel': ('Jl', 4),
    'Amos': ('Am', 9),
    'Obadiah': ('Ob', 1),
    'Jonah': ('Jon', 4),
    'Micah': ('Mi', 7),
    'Nahum': ('Na', 3),
    'Habakkuk': ('Hb', 3),
    'Zephaniah': ('Zep', 3),
    'Haggai': ('Hg', 2),
    'Zechariah': ('Zec', 14),
    'Malachi': ('Mal', 3),
    '1 Esdras': ('1Esd', 9),
    'Judith': ('Jdt', 16),
    'Tobit BA': ('TbBA', 14),
    '1 Maccabees': ('1Mc', 16),
    '2 Maccabees': ('2Mc', 15),
    '3 Maccabees': ('3Mc', 7),
    '4 Maccabees': ('4Mc', 18),
    'Odes': ('Ode', 14),
    'Wisdom of Solomon': ('Wsd', 19),
    'Sirach': ('Sir', 51),
    'Psalms of Solomon': ('PsSol', 18),
    'Baruch': ('Bar', 5),
    'Letter of Jeremiah': ('EpJer', 1),
    'Susanna OG': ('SusOG', 1),
    'Susanna Th': ('SusTh', 1),
    'Bel and the Dragon OG': ('BelOG', 1),
    'Bel and the Dragon Th': ('BelTh', 1)
}
POS_CODES = {'A-': 'adjective',
             'C-': 'conjunction',
             'D-': 'adverb',
             'I-': 'interjection',
             'N-': 'noun',
             'P-': 'preposition',
             'RA': 'definite article',
             'RD': 'demonstrative pronoun',
             'RI': 'interrogative/indefinite pronoun',
             'RP': 'personal pronoun',
             'RR': 'relative pronoun',
             'V-': 'verb',
             'X-': 'particle'}
PERSON_CODES = {'1st': 'first',
                '2nd': 'second',
                '3rd': 'third'}
TENSE_CODES = {'pres': 'present',
               'impf': 'imperfect',
               'fut': 'future',
               'aor': 'aorist',
               'perf': 'perfect',
               'plup': 'pluperfect'}
VOICE_CODES = {'act': 'active',
               'mp': 'middle',
               'θη': 'passive'}
MOOD_CODES = {'ind': 'indicative',
              'imp': 'imperative',
              'sub': 'subjunctive',
              'opt': 'optative',
              'inf': 'infinitive',
              'ptcp': 'participle'}
CASE_CODES = {'nom': 'nominative',
              'gen': 'genitive',
              'dat': 'dative',
              'acc': 'accusative',
              'voc': 'vocative'}
NUMBER_CODES = {'sg': 'singular',
                'pl': 'plural'}
GENDER_CODES = {'mas': 'masculine',
                'fem': 'feminine',
                'neu': 'neuter'}
DEGREE_CODES = {'Comp': 'comparative',
                'Superl': 'superlative'}


def download_katabiblon():
    """Download raw html of the LXX from katabiblon.com."""

    base_url = 'https://en.katabiblon.com/us/index.php?text=LXX'
    for book, (abbr, chaps) in CHAPTER_ABBR_COUNTS.items():
        for chapter in range(chaps):
            raw_html = requests.get(base_url + '&book=' + abbr + '&ch=' + str(chapter + 1))
            raw_html.encoding = 'utf-8'
            with open(RAW_DATA_DIR + book + '_' + str(chapter + 1) + '.html',
                      'w', encoding='utf8') as file:
                file.write(raw_html.text)


def process_one_chapter(book, chapter):
    """Load the text of one LXX chapter as a pandas dataframe."""

    with open(RAW_DATA_DIR + book + '_' + chapter + '.html',
              encoding='utf8') as file:

        # Extract verse, wordform, and morphological codes from the raw html.
        raw_html = BeautifulSoup(file, 'html.parser')
        lxx_df = pd.DataFrame([(int(verse['id'][1:]),
                                word.find('span', {'onclick': True}).string,
                                word_data.contents[3],
                                word_sub_data[0].find('strong').text.lower(),
                                word_sub_data[1].contents[0])
                               for verse in raw_html.find_all('tr', id=re.compile('^v[0-9]+$'))
                               for word in verse.find_all('span', {'class': 'interlinear'})
                               for word_data in [word.find('span', {'class': 'popup'})]
                               for word_sub_data in [tuple(word_data.find_all('span', {'lang': 'en'})[0:2])]],
                              columns=['verse', 'wordform', 'lemma', 'pos', 'morph'])

        # Add chapter, book, and verse.
        lxx_df['book'] = book
        lxx_df['chapter'] = int(chapter)
        lxx_df['word_order'] = lxx_df.groupby(['verse']).cumcount() + 1

        # Clean up lemma and morphological codes.
        lxx_df['lemma'] = lxx_df.apply(lambda row: row['lemma'][0:re.search('[,; ]|$', row['lemma']).start()],
                                       axis=1)
        lxx_df['morph'] = lxx_df.apply(lambda row: row['morph'][0:re.search('[,;]| or|$', row['morph']).start()],
                                       axis=1)
        lxx_df['person'] = lxx_df.morph.str.extract('(1st|2nd|3rd)')
        lxx_df['person'] = lxx_df['person'].map(PERSON_CODES)
        lxx_df['tense'] = lxx_df.morph.str.extract('(pres|fut|impf|aor|perf|plup)')
        lxx_df['tense'] = lxx_df['tense'].map(TENSE_CODES)
        lxx_df['voice'] = lxx_df.morph.str.extract('(act|mp|θη)')
        lxx_df['voice'] = lxx_df['voice'].map(VOICE_CODES)
        lxx_df['mood'] = lxx_df.morph.str.extract('(ind|inf|imp|sub|opt|ptcp)')
        lxx_df['mood'] = lxx_df['mood'].map(MOOD_CODES)
        lxx_df['case'] = lxx_df.morph.str.extract('(nom|gen|dat|acc|voc)')
        lxx_df['case'] = lxx_df['case'].map(CASE_CODES)
        lxx_df['number'] = lxx_df.morph.str.extract('(sg|pl)')
        lxx_df['number'] = lxx_df['number'].map(NUMBER_CODES)
        lxx_df['gender'] = lxx_df.morph.str.extract('(mas|fem|neu)')
        lxx_df['gender'] = lxx_df['gender'].map(GENDER_CODES)
        lxx_df['degree'] = lxx_df.morph.str.extract('(Comp|Superl)')
        lxx_df['degree'] = lxx_df['degree'].map(DEGREE_CODES)
        lxx_df.drop(['morph'], axis=1, inplace=True)

        # All done; return the dataframe.
        return lxx_df


def process_one_book(book):
    """Save the parsed LXX text as a csv."""

    print(book)
    text = pd.concat([process_one_chapter(book, str(chapter + 1))
                      for chapter in range(CHAPTER_ABBR_COUNTS[book][1])])
    return(text)


if __name__ == '__main__':
    lxx_df = pd.concat([process_one_book(book)
                        for book in CHAPTER_ABBR_COUNTS.keys()])
    lxx_df.to_csv(TEXT_DATA_DIR + 'lxx_text.csv', index=False)
