import pandas as pd
from text_and_vocab import load_text_df
from parsing.utils import GRAMMAR_DIR

HAND_DATA_DIR = 'hand_coded_data/'
DEPENDENCY_TYPES = [('argument', 'arguments'),
                    ('subject', 'subjects'),
                    ('modifier', 'modifiers'),
                    ('conjunction', 'conjunctions'),
                    ('second_position_clitic', 'second_position_clitics'),
                    ('negation', 'negation'),
                    ('determiner', 'determiners'),
                    ('interjection', 'interjections')]

def load_dependencies_df():
    """Load the csvs of dependencies as a dataframe."""
    dependencies_df = pd.concat([pd.read_csv(HAND_DATA_DIR + 'dependencies_' +
                                             dp[1] + '.csv')\
                                   .assign(type=dp[0])
                                 for dp in DEPENDENCY_TYPES])
    return dependencies_df


def write_dependency_rules():
    """Write the lexicon for the feature grammar."""
    # Load the dependencies.
    dependencies_df = load_dependencies_df()
    # Load the mapping between parsing atoms and lemmas.
    atoms_lemmas_df = load_text_df('nt').loc[:, ['pos', 'lemma',
                                                 'parsing_atom']]\
                                        .drop_duplicates()
    dependencies_df = dependencies_df.merge(atoms_lemmas_df,
                                            left_on='parsing_atom_head',
                                            right_on='parsing_atom')
    # Write each dependency type to its own file.
    for dp in DEPENDENCY_TYPES:
        rule_file = open(GRAMMAR_DIR + dp[1] + '.dg', 'w')
        dp_df = dependencies_df[dependencies_df.type == dp[0]]
        for pos in dp_df.pos.unique():
            pos_df = dp_df[dp_df.pos == pos]
            rule_file.write('#### ' + pos + ' ####\n')
            rule_file.write('\n')
            for lemma in pos_df.lemma.unique():
                lemmas_df = pos_df[pos_df.lemma == lemma]
                rule_file.write('# ' + lemma + '\n')
                for head_atom in lemmas_df.parsing_atom_head.unique():
                    dependents_df = lemmas_df[lemmas_df.parsing_atom_head == head_atom]
                    # rule_file.write(dp[0] + " '" + head_atom + "' -> " +
                    rule_file.write("'" + head_atom + "' -> " +
                                    ' | '.join(["'" + dependent_atom + "'"
                                                for dependent_atom
                                                in dependents_df.parsing_atom_dependent.unique()]) +
                                    '\n')
                rule_file.write('\n')
        rule_file.close()


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    write_dependency_rules()
