import re
import pandas as pd
from file_locations import TEXT_DATA_DIR, TAGGED_CORPUS_DIR, BOOK_MAPPING
from file_locations import PERSON_CODES, TENSE_CODES, VOICE_CODES, MOOD_CODES
from file_locations import CASE_CODES, NUMBER_CODES, GENDER_CODES


# Load the text as a pandas dataframe.
def load_text_df(text):
    """Load the text as a dataframe from the csv."""
    if text == 'nt':
        return pd.read_csv(TEXT_DATA_DIR + 'morphgnt_text.csv')
    elif text == 'lxx':
        return pd.read_csv(TEXT_DATA_DIR + 'lxx_text.csv')


# Get parsing codes for a wordform.
def get_morph_codes(df_row):
    """Add morphological parsing codes to a wordform."""
    morph_codes = PERSON_CODES.get(df_row['person'], '-') +\
                  TENSE_CODES.get(df_row['tense'], '-') +\
                  VOICE_CODES.get(df_row['voice'], '-') +\
                  MOOD_CODES.get(df_row['mood'], '-') +\
                  CASE_CODES.get(df_row['case'], '-') +\
                  NUMBER_CODES.get(df_row['number'], '-') +\
                  GENDER_CODES.get(df_row['gender'], '-')
    return morph_codes


# Write the NT text in a format to be read by the NTTaggedCorpusReader.
def write_text_plain():
    """Save the text in a tagged corpus format."""
    # Load the text as a dataframe.
    nt_df = load_text_df('nt')
    # Iterate over books.
    for book in BOOK_MAPPING.keys():
        # Open the file for this book.
        file = open(TEXT_DATA_DIR + TAGGED_CORPUS_DIR +
                    BOOK_MAPPING[book] + '.txt', 'w')
        # Iterate over chapters.
        for chapter in nt_df[nt_df.book_name == book].chapter.unique():
            # Get just the text for this chapter.
            chapter_df = nt_df[(nt_df.book_name == book) &
                               (nt_df.chapter == chapter)].copy()
            # Write each word in the chapter.  Each sentence is its own line,
            # prefaced with the chapter:verse reference.
            current_verses = []
            current_sentence = []
            for i, r in chapter_df.iterrows():
                if r['verse'] not in current_verses:
                    current_verses = current_verses + [r['verse']]
                current_sentence = current_sentence + [r['standardized_wordform'] +
                                                       '_' +
                                                       get_morph_codes(r)]
                if re.match('.*[.;·]', r['wordform']) and \
                        r['standardized_wordform'] != 'le/gwn':
                    file.write(str(chapter) + ':' + str(current_verses[0]))
                    if len(current_verses) > 1:
                        file.write('-' + str(current_verses[-1]))
                    file.write(' ' + ' '.join(current_sentence) + '\n')
                    current_verses = []
                    current_sentence = []
        file.close()


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    nt_df = load_text_df('nt')
    lxx_df = load_text_df('lxx')
    # write_text_plain()
