import re
import pandas as pd
import numpy as np
from file_locations import TEXT_DATA_DIR
from text_and_vocab import load_text_df


def pull_unique_lemmas(pos):
    """Get unique lemmas from the NT text."""
    # Load the text.
    nt_df = load_text_df('nt')
    vocab_df = nt_df[['lemma', 'pos', 'gender']].copy()
    # Filter to the specified part of speech.
    vocab_df = vocab_df[vocab_df.pos == pos]
    if pos != 'noun':
        vocab_df.drop('gender', axis=1, inplace=True)
    vocab_df.drop('pos', axis=1, inplace=True)
    # Get unique lemmas.
    vocab_df.drop_duplicates(inplace=True)
    # Return the dataframe.
    return vocab_df


def get_noun_forms(lemmas_df, pos):
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
    # Get hand-coded data.
    key_cols = ['lemma']
    if pos == 'noun':
        key_cols = key_cols + ['gender']
    df_cols = key_cols
    hand_df = pd.read_csv(TEXT_DATA_DIR + 'hand_coded_data/' +
                          pos.replace(' ', '_').replace('/', '_') +
                          '_supp_data.csv')
    nouns_df = nouns_df.merge(hand_df, how='left', on=key_cols, indicator=True)
    nouns_df['gs'] = np.select([(~nouns_df.gs_y.isnull().to_numpy()),
                                ((nouns_df._merge == 'both') &
                                 (nouns_df.gs_x == 'NEEDED'))],
                               [nouns_df.gs_y,
                                nouns_df.gs_y],
                               default=nouns_df.gs_x)
    if pos == 'noun':
        nouns_df['declension'] = nouns_df.declension_y.combine_first(nouns_df.declension_x)
        df_cols = df_cols + ['declension']
    # All done; return the dataframe.
    return nouns_df[df_cols + ['gs', 'gs_other']]


def get_adjective_forms(lemmas_df, pos):
    """Add the genitive singular form to each noun."""
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
    # Get hand-coded data.
    key_cols = ['lemma']
    hand_df = pd.read_csv(TEXT_DATA_DIR + 'hand_coded_data/' +
                          pos.replace(' ', '_') + '_supp_data.csv')
    adjectives_df = adjectives_df.merge(hand_df, how='left', on=key_cols,
                                        indicator=True)
    adjectives_df['declension'] = adjectives_df.declension_y.combine_first(adjectives_df.declension_x)
    for g in ['fem', 'neut']:
        adjectives_df[g] = np.select([(~adjectives_df[g + '_y'].isnull().to_numpy()),
                                      ((adjectives_df._merge == 'both') &
                                       (adjectives_df[g + '_x'] == 'NEEDED'))],
                                     [adjectives_df[g + '_y'],
                                      adjectives_df[g + '_y']],
                                     default=adjectives_df[g + '_x'])
    # All done; return the dataframe.
    df_cols = key_cols + ['declension']
    return adjectives_df[df_cols + [g + suffix
                                    for g in ['fem', 'neut']
                                    for suffix in ['', '_other']]]


def get_verb_forms(lemmas_df):
    """Add the genitive singular form to each noun."""
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
    # Get hand-coded data.
    key_cols = ['lemma']
    hand_df = pd.read_csv(TEXT_DATA_DIR + 'hand_coded_data/verb_supp_data.csv')
    verbs_df = verbs_df.merge(hand_df, how='left', on=key_cols, indicator=True)
    verbs_df['verb_type'] = verbs_df.verb_type_y.combine_first(verbs_df.verb_type_x)
    for pp in ['pp' + str(p + 2) for p in range(5)]:
        verbs_df[pp] = np.select([(~verbs_df[pp + '_y'].isnull().to_numpy()),
                                  ((verbs_df._merge == 'both') &
                                   (verbs_df[pp + '_x'] == 'NEEDED'))],
                                 [verbs_df[pp + '_y'],
                                  verbs_df[pp + '_y']],
                                 default=verbs_df[pp + '_x'])
    # All done; return the dataframe.
    df_cols = key_cols + ['verb_type']
    return verbs_df[df_cols + [pp + suffix
                               for pp in ['pp' + str(p + 2) for p in range(5)]
                               for suffix in ['', '_other']]]


def process_vocab(pos):
    """Process vocab, combining data sources as needed."""
    # Get the unique lemmas for this POS.
    lemmas_df = pull_unique_lemmas(pos)
    # Get additional data for certain POSs.
    if pos in ['noun', 'personal pronoun', 'interrogative/indefinite pronoun']:
        lemmas_df = get_noun_forms(lemmas_df, pos)
    elif pos in ['relative pronoun', 'definite article', 'adjective',
                 'demonstrative pronoun']:
        lemmas_df = get_adjective_forms(lemmas_df, pos)
    elif pos == 'verb':
        lemmas_df = get_verb_forms(lemmas_df)
    # All done; return the dataframe.
    return lemmas_df


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    nouns_df = process_vocab('noun')
    nouns_df.to_csv(TEXT_DATA_DIR + 'noun_data.csv', index=False)
    relative_pronouns_df = process_vocab('relative pronoun')
    relative_pronouns_df.to_csv(TEXT_DATA_DIR + 'relative_pronoun_data.csv',
                                index=False)
    verbs_df = process_vocab('verb')
    verbs_df.to_csv(TEXT_DATA_DIR + 'verb_data.csv', index=False)
    personal_pronouns_df = process_vocab('personal pronoun')
    personal_pronouns_df.to_csv(TEXT_DATA_DIR + 'personal_pronoun_data.csv',
                                index=False)
    definite_articles_df = process_vocab('definite article')
    definite_articles_df.to_csv(TEXT_DATA_DIR + 'definite_article_data.csv',
                                index=False)
    prepositions_df = process_vocab('preposition')
    prepositions_df.to_csv(TEXT_DATA_DIR + 'preposition_data.csv', index=False)
    conjunctions_df = process_vocab('conjunction')
    conjunctions_df.to_csv(TEXT_DATA_DIR + 'conjunction_data.csv', index=False)
    adjectives_df = process_vocab('adjective')
    adjectives_df.to_csv(TEXT_DATA_DIR + 'adjective_data.csv', index=False)
    adverbs_df = process_vocab('adverb')
    adverbs_df.to_csv(TEXT_DATA_DIR + 'adverb_data.csv', index=False)
    particles_df = process_vocab('particle')
    particles_df.to_csv(TEXT_DATA_DIR + 'particle_data.csv', index=False)
    demonstrative_pronouns_df = process_vocab('demonstrative pronoun')
    demonstrative_pronouns_df.to_csv(TEXT_DATA_DIR +
                                     'demonstrative_pronoun_data.csv',
                                     index=False)
    interrogative_indefinite_pronouns_df = process_vocab('interrogative/indefinite pronoun')
    interrogative_indefinite_pronouns_df.to_csv(TEXT_DATA_DIR +
                                                'interrogative_indefinite_pronoun_data.csv',
                                                index=False)
    interjections_df = process_vocab('interjection')
    interjections_df.to_csv(TEXT_DATA_DIR + 'interjection_data.csv',
                            index=False)
