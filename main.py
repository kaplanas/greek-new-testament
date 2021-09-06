import pandas as pd
from text_and_vocab import load_text_df

if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    nt_df = load_text_df('nt')
