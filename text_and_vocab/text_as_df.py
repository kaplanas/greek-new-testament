import re
import pandas as pd
from text_and_vocab.utils import TEXT_DATA_DIR


# Load the text as a pandas dataframe.
def load_text_df(text):
    """Load the text as a dataframe from the csv."""
    if text == 'nt':
        return pd.read_csv(TEXT_DATA_DIR + 'morphgnt_text.csv')
    elif text == 'lxx':
        return pd.read_csv(TEXT_DATA_DIR + 'lxx_text.csv')


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    nt_df = load_text_df('nt')
    lxx_df = load_text_df('lxx')
