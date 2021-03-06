import re
import pandas as pd
from text_and_vocab.utils import TEXT_DATA_DIR, TAGGED_CORPUS_DIR, BOOK_MAPPING
from text_and_vocab.utils import get_morph_codes


# Load the text as a pandas dataframe.
def load_text_df(text):
    """Load the text as a dataframe from the csv."""
    if text == 'nt':
        return pd.read_csv(TEXT_DATA_DIR + 'morphgnt_text.csv')
    elif text == 'lxx':
        return pd.read_csv(TEXT_DATA_DIR + 'lxx_text.csv')


# Write the NT text in a format to be read by the NTTaggedCorpusReader.
def write_text_tagged():
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
                if re.match('.*,', r['wordform']):
                    current_sentence = current_sentence + [',_,']
                elif re.match('.*[.;·]', r['wordform']):
                    if r['lemma'] in ['le/gw', 'fhmi/', 'gra/fw', 'kai/',
                                      'h)/', 'ga/r', 'menou=nge'] \
                            and re.match('.*·', r['wordform']):
                        current_sentence = current_sentence + [',_,']
                    else:
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
    write_text_tagged()
