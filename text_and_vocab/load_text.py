import pandas as pd

TEXT_DATA_DIR = '../text_data/'


def load_text(text):
    """Load the text from the csv."""
    if text == 'nt':
        return pd.read_csv(TEXT_DATA_DIR + 'morphgnt_text.csv')
    elif text == 'lxx':
        return pd.read_csv(TEXT_DATA_DIR + 'lxx_text.csv')


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    nt_df = load_text('nt')
    lxx_df = load_text('lxx')
