import re
import pandas as pd
import numpy as np
from utils import TEXT_DATA_DIR
from text_and_vocab import load_text_df


HAND_DATA_DIR = 'hand_coded_data/'
PROCESSED_DATA_DIR = 'processed_data/'
POS_PROCESSING = {
    'noun': {'id_cols': ['gender'],
             'form_cols': ['gs'],
             'class_cols': ['declension'],
             'feature_cols': ['distant_determiner']},
    'relative pronoun': {'id_cols': [],
                         'form_cols': ['fem', 'neut'],
                         'class_cols': ['declension']},
    'verb': {'id_cols': [],
             'form_cols': ['pp' + str(i + 2) for i in range(5)],
             'class_cols': ['verb_type'],
             'feature_cols': ['arg_nom', 'arg_gen', 'arg_dat', 'arg_acc',
                              'arg_inf', 'determiner', 'distant_determiner']},
    'personal pronoun': {'id_cols': [],
                         'form_cols': ['gs'],
                         'feature_cols': ['person']},
    'definite article': {'id_cols': [],
                         'form_cols': ['fem', 'neut'],
                         'class_cols': ['declension']},
    'preposition': {'id_cols': []},
    'conjunction': {'id_cols': [],
                    'feature_cols': ['second_position']},
    'adjective': {'id_cols': [],
                  'form_cols': ['fem', 'neut'],
                  'class_cols': ['declension'],
                  'feature_cols': ['standalone', 'distant_determiner']},
    'adverb': {'id_cols': []},
    'interjection': {'id_cols': []},
    'particle': {'id_cols': []},
    'demonstrative pronoun': {'id_cols': [],
                              'form_cols': ['fem', 'neut'],
                              'class_cols': ['declension']},
    'interrogative/indefinite pronoun': {'id_cols': [],
                                         'form_cols': ['gs']}
}


def get_unique_forms(pos, lemma_or_wordform='lemma'):
    """Get unique lemmas or wordforms from the NT text."""
    # Load the text and filter to the specified part of speech.
    nt_df = load_text_df('nt')
    nt_df = nt_df[nt_df.pos == pos]
    # Which columns do we need to uniquely identify the lemma/wordform?
    id_cols = ['lemma'] + POS_PROCESSING[pos]['id_cols']
    if lemma_or_wordform == 'wordform':
        id_cols = id_cols + ['standardized_wordform']
    vocab_df = nt_df[id_cols].copy()
    # Get unique lemmas/wordforms.
    vocab_df.drop_duplicates(inplace=True)
    # Return the dataframe.
    return vocab_df


def get_genitive_forms(lemmas_df, pos):
    """Add the genitive singular form to each noun."""
    # Get unique noun wordforms from the NT and LXX.
    nt_df = load_text_df('nt')
    nt_df = nt_df[(nt_df.pos == pos)]
    lxx_df = load_text_df('lxx')
    lxx_df = lxx_df[(lxx_df.pos == pos) &
                    (lxx_df.case == 'genitive') &
                    (lxx_df.number == 'singular')]
    # Find a genitive singular form for each noun and guess at its declension.
    nouns_df = lemmas_df.copy()
    for i, r in nouns_df.iterrows():
        # Get the lemma.
        lemma = nouns_df.loc[i, 'lemma']
        # Get the genitive singular, if attested.  Try NT first, then LXX.  Not
        # needed if the word is attested only in the nominative singular.
        non_ns_df = nt_df[(nt_df.lemma == lemma) &
                          ((nt_df.case != 'nominative') |
                           (nt_df.number != 'singular'))]
        if non_ns_df.shape[0] > 0:
            gs = non_ns_df[(non_ns_df.case == 'genitive') &
                           (non_ns_df.number == 'singular')]['standardized_wordform'].unique()
            if len(gs) > 0:
                nouns_df.loc[i, 'gs'] = gs[0]
            else:
                gs = lxx_df[(lxx_df.lemma == lemma)]['wordform'].unique()
                if len(gs) > 0:
                    nouns_df.loc[i, 'gs'] = gs[0]
                else:
                    nouns_df.loc[i, 'gs'] = 'NEEDED'
                    nouns_df.loc[i, 'gs_other'] = ', '.join(non_ns_df['standardized_wordform'].unique())
        # Guess at the declension of the noun.
        if pos == 'noun':
            if len(gs) > 0 and re.match('.*o[/\\\\]?s$', gs[0]):
                declension = 3
            elif re.match('.*(a|h)[/=|]?s?$', lemma):
                declension = 1
            elif re.match('.*os$', lemma) and nouns_df.loc[i, 'gender'] == 'neuter':
                declension = 3
            elif re.match('.*o/?[sn]$', lemma):
                declension = 2
            else:
                declension = 3
            nouns_df.loc[i, 'declension'] = declension
    # All done; return the dataframe.
    return nouns_df


def get_gender_forms(lemmas_df, pos):
    """Add the feminine and neuter forms for each adjective."""
    # Get unique adjective wordforms from the NT and LXX.
    nt_df = load_text_df('nt')
    nt_df = nt_df[(nt_df.pos == pos)]
    lxx_df = load_text_df('lxx')
    lxx_df = lxx_df[(lxx_df.pos == pos) &
                    (lxx_df.case == 'nominative') &
                    (lxx_df.number == 'singular')]
    # Find a form in each gender for each adjective and guess at its
    # declension.
    adjectives_df = lemmas_df.copy()
    adjectives_df[['fem', 'fem_other', 'neut', 'neut_other']] = np.nan
    for i, r in adjectives_df.iterrows():
        # Get the lemma.
        lemma = adjectives_df.loc[i, 'lemma']
        for g, gender in [('fem', 'feminine'),
                          ('neut', 'neuter')]:
            # Get the form in this gender, if attested.  Try NT first, then
            # LXX.  Not needed if the word is not attested in this gender.
            gen_df = nt_df[(nt_df.lemma == lemma) & (nt_df.gender == gender)]
            if gen_df.shape[0] > 0:
                gen = gen_df[(gen_df.case == 'nominative') &
                             (gen_df.number == 'singular')]['standardized_wordform'].unique()
                if len(gen) > 0:
                    adjectives_df.loc[i, g] = gen[0]
                else:
                    gen = lxx_df[(lxx_df.lemma == lemma) &
                                 (lxx_df.gender == gender)]['wordform'].unique()
                    if len(gen) > 0:
                        adjectives_df.loc[i, g] = gen[0]
                    else:
                        adjectives_df.loc[i, g] = 'NEEDED'
                        adjectives_df.loc[i, g + '_other'] = ', '.join(gen_df['standardized_wordform'].unique())
        # Guess at the declension of the adjective.
        if re.match('.*o[/\\\\]?s$', lemma):
            declension = '1/2'
        else:
            declension = '3'
        adjectives_df.loc[i, 'declension'] = declension
    # All done; return the dataframe.
    return adjectives_df


def get_principal_parts(lemmas_df):
    """Add the principal parts for each verb."""
    # Get unique verb wordforms from the NT and LXX.
    nt_df = load_text_df('nt')
    nt_df = nt_df[(nt_df.pos == 'verb')]
    lxx_df = load_text_df('lxx')
    lxx_df = lxx_df[(lxx_df.pos == 'verb') &
                    (lxx_df.person == 1) &
                    (lxx_df.number == 'singular') &
                    (lxx_df.mood == 'indicative') &
                    (((lxx_df.voice == 'active') &
                      ((lxx_df.tense == 'future') |
                       (lxx_df.tense == 'aorist') |
                       (lxx_df.tense == 'perfect'))) |
                     ((lxx_df.voice == 'middle') &
                      (lxx_df.tense == 'perfect')) |
                     ((lxx_df.voice == 'passive') &
                      (lxx_df.tense == 'future')))]
    # Find a form in each principal part for each verb.
    verbs_df = lemmas_df.copy()
    for i, r in verbs_df.iterrows():
        # Get the lemma.
        lemma = verbs_df.loc[i, 'lemma']
        for pp_num in [p + 2 for p in range(5)]:
            # Get the form of this principal part, if attested.  Try NT first,
            # then LXX.  Not needed if the word is not attested in this
            # principal part.
            pp_df = nt_df[(nt_df.lemma == lemma) &
                          (((pp_num == 2) &
                            ((nt_df.voice == 'active') |
                             (nt_df.voice == 'middle')) &
                            (nt_df.tense == 'future')) |
                           ((pp_num == 3) &
                            ((nt_df.voice == 'active') |
                             (nt_df.voice == 'middle')) &
                            (nt_df.tense == 'aorist')) |
                           ((pp_num == 4) &
                            (nt_df.voice == 'active') &
                            ((nt_df.tense == 'perfect') |
                             (nt_df.tense == 'pluperfect'))) |
                           ((pp_num == 5) &
                            ((nt_df.voice == 'middle') |
                             (nt_df.voice == 'passive')) &
                            ((nt_df.tense == 'perfect') |
                             (nt_df.tense == 'pluperfect'))) |
                           ((pp_num == 6) &
                            (nt_df.voice == 'passive') &
                            ((nt_df.tense == 'future') |
                             (nt_df.tense == 'aorist'))))]
            if pp_df.shape[0] > 0:
                pp = pp_df[(pp_df.person == 1) &
                           (pp_df.number == 'singular') &
                           (pp_df.mood == 'indicative')]['standardized_wordform'].unique()
                if len(pp) > 0:
                    verbs_df.loc[i, 'pp' + str(pp_num)] = pp[0]
                else:
                    pp = lxx_df[(lxx_df.lemma == lemma) &
                                (((pp_num == 2) &
                                  (lxx_df.voice == 'active') &
                                  (lxx_df.tense == 'future')) |
                                 ((pp_num == 3) &
                                  (lxx_df.voice == 'active') &
                                  (lxx_df.tense == 'aorist')) |
                                 ((pp_num == 4) &
                                  (lxx_df.voice == 'active') &
                                  (lxx_df.tense == 'perfect')) |
                                 ((pp_num == 5) &
                                  (lxx_df.voice == 'middle') &
                                  (lxx_df.tense == 'perfect')) |
                                 ((pp_num == 6) &
                                  (lxx_df.voice == 'passive') &
                                  (lxx_df.tense == 'aorist')))]['wordform'].unique()
                    if len(pp) > 0:
                        verbs_df.loc[i, 'pp' + str(pp_num)] = pp[0]
                    else:
                        verbs_df.loc[i, 'pp' + str(pp_num)] = 'NEEDED'
                        verbs_df.loc[i, 'pp' + str(pp_num) + '_other'] = ', '.join(pp_df['standardized_wordform'].unique())
        # Guess at the verb type.
        if re.match('.*w$', lemma):
            verb_type = 'w'
        elif re.match('.*omai$', lemma):
            verb_type = 'w'
        elif re.match('.*mi/?$', lemma):
            verb_type = 'mi'
        elif re.match('.*mai$', lemma):
            verb_type = 'mai'
        else:
            verb_type = 'other'
        verbs_df.loc[i, 'verb_type'] = verb_type
    # All done; return the dataframe.
    return verbs_df


def process_vocab(pos):
    """Process vocab, combining data sources as needed."""
    # Get the unique lemmas for this POS.
    lemmas_df = get_unique_forms(pos, 'lemma')
    # Get additional forms for these lemmas, depending on the POS.
    if 'form_cols' in POS_PROCESSING[pos].keys():
        if POS_PROCESSING[pos]['form_cols'] == ['gs']:
            lemmas_df = get_genitive_forms(lemmas_df, pos)
        elif POS_PROCESSING[pos]['form_cols'] == ['fem', 'neut']:
            lemmas_df = get_gender_forms(lemmas_df, pos)
        elif POS_PROCESSING[pos]['form_cols'] == ['pp' + str(i + 2) for i in range(5)]:
            lemmas_df = get_principal_parts(lemmas_df)
        # Get additional hand-coded forms, depending on the POS.
        if POS_PROCESSING[pos]['form_cols']:
            id_cols = ['lemma'] + POS_PROCESSING[pos]['id_cols']
            supp_forms_df = pd.read_csv(TEXT_DATA_DIR + HAND_DATA_DIR +
                                        pos.lower().replace(' ', '_').replace('/', '_') +
                                        '_supp_forms.csv')
            lemmas_df = lemmas_df.merge(supp_forms_df, how='left', on=id_cols,
                                        indicator=True)
            if 'class_cols' in POS_PROCESSING[pos].keys():
                for class_col in POS_PROCESSING[pos]['class_cols']:
                    lemmas_df[class_col] = lemmas_df[class_col + '_y']\
                                           .combine_first(lemmas_df[class_col + '_x'])
            for form_col in POS_PROCESSING[pos]['form_cols']:
                lemmas_df[form_col] = np.select([(~lemmas_df[form_col + '_y'].isnull().to_numpy()),
                                                 ((lemmas_df._merge == 'both') &
                                                  (lemmas_df[form_col + '_x'] == 'NEEDED'))],
                                                [lemmas_df[form_col + '_y'],
                                                 lemmas_df[form_col + '_y']],
                                                default=lemmas_df[form_col + '_x'])
    # All done; return the dataframe.
    cols = ['lemma'] + POS_PROCESSING[pos]['id_cols']
    if 'class_cols' in POS_PROCESSING[pos].keys():
        cols = cols + POS_PROCESSING[pos]['class_cols']
    if 'form_cols' in POS_PROCESSING[pos].keys():
        cols = cols + [f + ending
                       for f in POS_PROCESSING[pos]['form_cols']
                       for ending in ['', '_other']]
    return lemmas_df[cols]


def write_lemmas_df(pos):
    """Write a csv of the lemmas for this POS."""
    lemmas_df = process_vocab(pos)
    lemmas_df.to_csv(TEXT_DATA_DIR + PROCESSED_DATA_DIR +
                     pos.lower().replace(' ', '_').replace('/', '_') +
                     '_data.csv', index=False)


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    # for pos in POS_PROCESSING.keys():
    #     print(pos)
    #     write_lemmas_df(pos)
