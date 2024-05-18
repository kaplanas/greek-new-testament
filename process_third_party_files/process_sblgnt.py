import pandas as pd
import numpy as np
import pymysql
import re
import unicodedata
from xml.etree import ElementTree
from collections import defaultdict

SBL_DIR = 'sblgnt'
SBL_FILES = ['01-matthew.xml', '02-mark.xml', '03-luke.xml', '04-john.xml', '05-acts.xml', '06-romans.xml',
             '07-1corinthians.xml', '08-2corinthians.xml', '09-galatians.xml', '10-ephesians.xml', '11-philippians.xml',
             '12-colossians.xml', '13-1thessalonians.xml', '14-2thessalonians.xml', '15-1timothy.xml',
             '16-2timothy.xml', '17-titus.xml', '18-philemon.xml', '19-hebrews.xml', '20-james.xml', '21-1peter.xml',
             '22-2peter.xml', '23-1john.xml', '24-2john.xml', '25-3john.xml', '26-jude.xml', '27-revelation.xml']
HEAD_EDITS = pd.read_csv(SBL_DIR + '/head_edits.csv',
                         dtype=defaultdict(lambda: str,
                                           {'chapter': np.float64, 'verse': np.float64, 'position': np.float64,
                                            'new_head_verse': np.float64, 'new_head_position': np.float64}))
POS_EDITS = pd.read_csv(SBL_DIR + '/pos_edits.csv', dtype=str)
GENITIVE_EDITS = pd.read_csv(SBL_DIR + '/genitive_edits.csv',
                             dtype=defaultdict(lambda: str,
                                               {'chapter': np.float64, 'verse': np.float64, 'position': np.float64}))
DATIVE_EDITS = pd.read_csv(SBL_DIR + '/dative_edits.csv',
                           dtype=defaultdict(lambda: str,
                                             {'chapter': np.float64, 'verse': np.float64, 'position': np.float64}))
OTHER_RELATION_EDITS = pd.read_csv(SBL_DIR + '/other_relation_edits.csv',
                                   dtype=defaultdict(lambda: str,
                                                     {'chapter': np.float64, 'verse': np.float64,
                                                      'position': np.float64}))
RELATION_EDITS = {'genitive': GENITIVE_EDITS, 'dative': DATIVE_EDITS, 'other': OTHER_RELATION_EDITS}

BOOKS_OF_THE_BIBLE = ['Matt', 'Mark', 'Luke', 'John', 'Acts', 'Rom', '1Cor', '2Cor', 'Gal', 'Eph', 'Phil', 'Col',
                      '1Thess', '2Thess', '1Tim', '2Tim', 'Titus', 'Phlm', 'Heb', 'Jas', '1Pet', '2Pet', '1John',
                      '2John', '3John', 'Jude', 'Rev']
PRETTY_BOOKS_OF_THE_BIBLE = ['Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans', '1 Corinthians', '2 Corinthians',
                             'Galatians', 'Ephesians', 'Philippians', 'Colossians', '1 Thessalonians',
                             '2 Thessalonians', '1 Timothy', '2 Timothy', 'Titus', 'Philemon', 'Hebrews', 'James',
                             '1 Peter', '2 Peter', '1 John', '2 John', '3 John', 'Jude', 'Revelation']
GREEK_CAPITALS = '^[' + ''.join(set(chr(cp)
                                    for cp in range(0x0370, 0x1FFF)
                                    if "GREEK CAPITAL" in unicodedata.name(chr(cp), ""))) + ']'
SECOND_POSITION_CLITICS = ['δέ', 'οὖν', 'γάρ', 'μέν']
SON_OF_WORDS = ['υἱός', 'θυγάτηρ', 'τέκνον', 'ἀδελφός', 'ἀδελφή', 'ἀνήρ', 'γυνή', 'πατήρ', 'μήτηρ']
SON_OF_POS = ['noun', 'personal pronoun', 'personal pronoun with kai', 'demonstrative pronoun',
              'demonstrative pronoun with kai', 'reflexive pronoun', 'interrogative pronoun', 'relative pronoun']
KEEP_DETERMINER_POS = ['noun', 'verb', 'adj']
KEEP_DETERMINER_LEMMAS = ['Ἀθηναῖος', 'Ἀδραμυττηνός', 'Αἰγύπτιος', 'Ἀλεξανδρῖνος', 'Ἄλφα', 'Ἀσιανός', 'Ἀσιάρχης',
                          'Ἀχαϊκός', 'Βεροιαῖος', 'Γαδαρηνός', 'Γαλατικός', 'Γερασηνός', 'Δαμασκηνός', 'Δερβαῖος',
                          'Διάβολος', 'Ἑβραῖος', 'Ἐλαμίτης', 'Ἕλλην', 'Ἑλληνικός', 'Ἑλληνιστής', 'Ἐπικούρειος',
                          'Ἐφέσιος', 'Ζηλωτής', 'Ἡρῳδιανοί', 'Θάλασσα', 'Θεσσαλονικεύς', 'Ἱεροσολυμίτης', 'Ἰορδάνης',
                          'Ἰουδαϊκός', 'Ἰουδαῖος', 'Ἰταλικός', 'Ἰτουραῖος', 'Καναναῖος', 'Κορίνθιος', 'Κόρινθος',
                          'Κύπριος', 'Κυρηναῖος', 'Κυρήνιος', 'Λαοδικεύς', 'Λευίτης', 'Λευιτικός', 'Λιβερτῖνος',
                          'Μῆδος', 'Ναζαρηνός', 'Ναζωραῖος', 'Νινευίτης', 'Πάρθος', 'Ποντικός', 'Ῥωμαῖος',
                          'Σαδδουκαῖος', 'Σαμαρίτης', 'Σαμαρῖτις', 'Σεβαστός', 'Σιδώνιος', 'Σύρος', 'Συροφοινίκισσα',
                          'Τύριος', 'Φαρισαῖος', 'Φιλιππήσιος', 'Χαλδαῖος', 'Χαναναῖος', 'Χριστιανός', 'Ὦ']
NEGATION = ['μή', 'οὐ', 'οὐδαμῶς']
PSEUDO_PREPOSITIONS = ['ὡσεί', 'ἕως']
COPULA = ['εἰμί']
CONJUNCTIONS = ['καί', 'ἤ', 'ἀλλὰ', 'μήτε', 'οὐδέ']


def get_tree_structure(sentence):
    # Initialize the list of words as list of words.
    words = []

    # Counter for missing node IDs.
    missing_node_id = 1

    # Walk down the tree and get all the nodes.  Add pointers to parents, children, and heads.
    all_nodes = dict()
    path_to_node = []
    node_stack = [sentence[2]]
    while len(node_stack) > 0:
        node = node_stack[-1]
        if len(path_to_node) > 0 and node is path_to_node[-1]:
            path_to_node.pop()
            node_stack.pop()
            node_dict = node.attrib
            if 'head' in node_dict:
                node_dict['is_head'] = True
            else:
                node_dict['is_head'] = False
            node_dict['tag'] = node.tag
            node_dict['text'] = node.text
            if 'osisId' in node_dict:
                reference_parts = re.split('[.!]', node_dict['osisId'])
                node_dict['book'] = reference_parts[0]
                node_dict['chapter'] = int(reference_parts[1])
                node_dict['verse'] = int(reference_parts[2])
                node_dict['position'] = int(reference_parts[3])
            if len(path_to_node) > 0:
                if 'n' not in path_to_node[-1].attrib:
                    path_to_node[-1].attrib['n'] = str(missing_node_id)
                    missing_node_id += 1
                node_dict['parent_n'] = path_to_node[-1].attrib['n']
                if len(path_to_node[-1]) == 1:
                    node_dict['is_head'] = True
            if 'n' not in node.attrib:
                node.attrib['n'] = str(missing_node_id)
                missing_node_id += 1
            all_nodes[node.attrib['n']] = node_dict
        else:
            path_to_node += [node]
            for child in reversed(node):
                node_stack += [child]

    # Add a pointer to each node's head child.
    for key, node in all_nodes.items():
        if node['is_head']:
            all_nodes[node['parent_n']]['head_child_n'] = key

    # Various edits.
    #   - Some nodes have no head child.  In these cases, call the first child the head.
    #   - Copula verbs are consistently not coded as heads.  I want them to be heads.
    #   - Objects of prepositions are consistently not coded as heads.  I want them to be heads.
    #   - In conjoined phrases, the first conjoined element is usually coded as the head.  I want the conjunction itself
    #     to be the head.
    for key, node in all_nodes.items():
        if node['tag'] != 'w' and 'head_child_n' not in node:
            all_children = [(n['position'], k)
                            for k, n in all_nodes.items() if 'parent_n' in n and n['parent_n'] == key]
            all_children = sorted(all_children)
            node['head_child_n'] = all_children[0][1]
            all_nodes[all_children[0][1]]['is_head'] = True
        if 'role' in node and node['role'] == 'vc':
            node['is_head'] = True
            all_nodes[node['parent_n']]['head_child_n'] = key
            for k, n in all_nodes.items():
                if 'parent_n' in n and n['parent_n'] == node['parent_n'] and k != key:
                    n['is_head'] = False
        if ('class' in node and node['class'] == 'prep') or \
                ('lemma' in node and node['lemma'] in CONJUNCTIONS and
                 node['position'] == min(n['position']
                                         for k, n in all_nodes.items()
                                         if 'lemma' in n and n['lemma'] in CONJUNCTIONS and
                                            'position' in n and n['parent_n'] == node['parent_n']) and
                 node['class'] != 'adv'):
            node['is_head'] = True
            all_nodes[node['parent_n']]['head_child_n'] = key
            for k, n in all_nodes.items():
                if 'parent_n' in n and n['parent_n'] == node['parent_n'] and k != key:
                    n['is_head'] = False
    #   - If we find a phrase whose role is "predicate", send that role all the way down to the lowest head.
    path_to_node = []

    # Propagate nodes' roles to their head children.  Make some edits along the way.
    node_stack = [(k, n) for k, n in all_nodes.items() if 'parent_n' not in n]
    while len(node_stack) > 0:
        node = node_stack[-1]
        if len(path_to_node) > 0 and node is path_to_node[-1]:
            path_to_node.pop()
            node_stack.pop()
        else:
            path_to_node += [node]
            for child in reversed([(k2, n2) for k2, n2 in all_nodes.items()
                                   if 'parent_n' in n2 and n2['parent_n'] == node[0]]):
                if 'head_child_n' in node[1] and node[1]['head_child_n'] == child[0] and \
                        'role' in node[1] and ('role' not in child[1] or node[1]['role'] == 'p'):
                    child[1]['role'] = node[1]['role']
                node_stack += [child]

    # Get just the words.  For each word, get a pointer to its head (if any).  Add ID, morphological, and syntactic
    # information.
    for node_id, node in all_nodes.items():
        if node['tag'] == 'w':

            # Start a dictionary with the word's properties.
            word_dict = {'id': node['n'], 'book': node['book'], 'chapter': node['chapter'], 'verse': node['verse'],
                         'position': node['position'], 'lemma': node['lemma'], 'wordform': node['text'],
                         'pos': node['class']}

            # Edit some properties by hand.
            if word_dict['lemma'] in list(POS_EDITS.lemma):
                word_dict['pos'] = POS_EDITS.loc[POS_EDITS.lemma == word_dict['lemma'],].iloc[0]['pos']

            # Add properties that might or might not be present.
            for field in ['number', 'gender', 'case', 'person', 'tense', 'voice', 'mood', 'degree', 'noun_class',
                          'verb_class']:
                if field in node:
                    word_dict[field] = node[field]
                else:
                    word_dict[field] = None

            # Set noun class.
            if word_dict['pos'] == 'noun':
                if word_dict['lemma'] == 'Ἰησοῦς':
                    word_dict['noun_class'] = 'Ihsous'
                elif word_dict['lemma'].endswith('μα'):
                    word_dict['noun_class'] = 'third declension'
                elif word_dict['lemma'].endswith('ος') or word_dict['lemma'].endswith('ός') \
                        or word_dict['lemma'].endswith('ον') or word_dict['lemma'].endswith('όν'):
                    word_dict['noun_class'] = 'second declension'
                elif word_dict['lemma'].endswith('η') or word_dict['lemma'].endswith('ή') or \
                        word_dict['lemma'].endswith('α') or word_dict['lemma'].endswith('ά'):
                    word_dict['noun_class'] = 'first declension'
                elif word_dict['lemma'].endswith('ης'):
                    word_dict['noun_class'] = 'second declension with hs'
                else:
                    word_dict['noun_class'] = 'third declension'

            # Set verb class.
            if word_dict['pos'] == 'verb':
                if word_dict['lemma'] == 'εἰμί':
                    word_dict['verb_class'] = 'eimi'
                elif word_dict['lemma'].endswith('έω') or word_dict['lemma'].endswith('έομαι') or \
                        word_dict['lemma'].endswith('άω') or word_dict['lemma'].endswith('άομαι') or \
                        word_dict['lemma'].endswith('όω') or word_dict['lemma'].endswith('όομαι'):
                    word_dict['verb_class'] = 'contract'
                elif word_dict['lemma'].endswith('ω') or word_dict['lemma'].endswith('ομαι'):
                    word_dict['verb_class'] = 'omega'
                elif word_dict['lemma'].endswith('μι'):
                    word_dict['verb_class'] = 'mi'
                else:
                    word_dict['verb_class'] = 'other'

            # Add fields that we'll populate later.
            word_dict['head'] = None
            word_dict['deps'] = []
            word_dict['relation'] = 'unknown'
            if 'role' in node:
                word_dict['relation'] = node['role']

            # Get the head of this word, if any.
            walking_up = True
            word_is_root = False
            current_node = node
            while walking_up:
                walking_up = current_node['is_head'] and 'parent_n' in all_nodes[current_node['parent_n']]
                word_is_root = current_node['is_head'] and not walking_up
                current_node = all_nodes[current_node['parent_n']]
            if not word_is_root:
                found_head = False
                while not found_head:
                    current_node = all_nodes[current_node['head_child_n']]
                    found_head = current_node['tag'] == 'w'
                word_dict['head_id'] = current_node['n']

            # Add the word to the list of words.
            words += [word_dict]

    # Hand-entered head edits.
    edits_df = pd.DataFrame(words)
    edits_df = edits_df.merge(HEAD_EDITS, left_on=['book', 'chapter', 'verse', 'position'],
                              right_on=['book', 'chapter', 'verse', 'position'])
    all_words = [(word['book'], word['chapter'], word['verse'], word['position']) for word in words]
    edit_targets = list(zip(edits_df['book'], edits_df['chapter'], edits_df['verse'], edits_df['position']))
    if edits_df.shape[0] > 0:
        for word in words:
            if (word['book'], word['chapter'], word['verse'], word['position']) in edit_targets:
                edit_index = edit_targets.index((word['book'], word['chapter'], word['verse'], word['position']))
                if np.isnan(edits_df['new_head_verse'][edit_index]):
                    del word['head_id']
                else:
                    new_head_index = all_words.index((word['book'], word['chapter'], edits_df['new_head_verse'][edit_index],
                                                      edits_df['new_head_position'][edit_index]))
                    word['head_id'] = words[new_head_index]['id']

    # Sort the words.
    words = sorted(words, key=lambda d: (d['chapter'], d['verse'], d['position']))

    # Get the position indices of the head and deps of each word.
    for i, word in enumerate(words):
        if 'head_id' in word:
            for j, possible_head in enumerate(words):
                if possible_head['id'] == word['head_id']:
                    word['head'] = j
                    possible_head['deps'] += [i]
        else:
            root = i

    # For each word, add a list that represents the path from the root to the word.
    for i, w in enumerate(words):
        w['path'] = []
    paths = [[root]]
    while len(paths) > 0:
        current_path = paths.pop()
        words[current_path[-1]]['path'] = current_path
        paths += [current_path + [dep] for dep in words[current_path[-1]]['deps']]

    # Code some syntactic relations.
    for word in words:
        if word['head'] is not None:
            if word['relation'] == 's':
                if words[word['head']]['pos'] != 'verb':
                    word['relation'] = 'subject of verbless predicate'
                elif word['case'] == 'accusative' and words[word['head']]['mood'] == 'infinitive':
                    word['relation'] = 'accusative subject of infinitive'
                elif words[word['head']]['mood'] == 'participle':
                    word['relation'] = 'subject of participle'
                elif word['gender'] == 'neuter' and word['number'] == 'plural':
                    if words[word['head']]['number'] == 'singular':
                        word['relation'] = 'subject, neuter plural'
                    else:
                        word['relation'] = 'subject, neuter plural, regular agreement'
                elif word['number'] != words[word['head']]['number']:
                    word['relation'] = 'subject, irregular agreement'
                else:
                    word['relation'] = 'subject'
            elif word['relation'] == 'p':
                if 'case' in word and word['case'] == 'nominative':
                    word['relation'] = 'predicate, nominative'
                elif 'case' in word and word['case'] == 'genitive':
                    word['relation'] = 'predicate, genitive'
                elif 'case' in word and word['case'] == 'dative':
                    word['relation'] = 'predicate, dative'
                else:
                    word['relation'] = 'predicate, other'
            else:
                if 'case' in word and 'case' in words[word['head']] \
                        and (word['case'] is not None or words[word['head']]['case'] is not None) \
                        and (word['case'] == words[word['head']]['case']
                             or word['case'] is None or words[word['head']]['case'] is None) \
                        and (('gender' in word and 'gender' in words[word['head']]
                              and word['gender'] == words[word['head']]['gender'])
                             or word['gender'] is None or words[word['head']]['gender'] is None) \
                        and (('number' in word and 'number' in words[word['head']] \
                              and word['number'] == words[word['head']]['number'])
                             or word['number'] is None or words[word['head']]['number'] is None) \
                        and (word['pos'] in ['adj', 'demonstrative pronoun', 'interrogative pronoun', 'pron', 'verb']
                             or word['lemma'] in ['Καῖσαρ']):
                    if word['pos'] == 'adj':
                        word['relation'] = 'nominal modifier, adjective'
                    elif word['pos'] == 'demonstrative pronoun':
                        word['relation'] = 'nominal modifier, demonstrative'
                    elif word['pos'] == 'interrogative pronoun':
                        word['relation'] = 'nominal modifier, interrogative'
                    elif word['pos'] == 'pron':
                        word['relation'] = 'nominal modifier, pronoun'
                    elif word['pos'] == 'verb':
                        word['relation'] = 'nominal modifier, participle'
                    elif word['lemma'] in ['Καῖσαρ']:
                        word['relation'] = 'title'
                elif word['pos'] == 'noun' and words[word['head']]['pos'] in ['noun', 'demonstrative pronoun',
                                                                              'personal pronoun']:
                    word['relation'] = 'appositive'
                elif 'case' in word and word['case'] == 'genitive':
                    if words[word['head']]['pos'] == 'verb':
                        word['relation'] = 'object, genitive'
                    elif words[word['head']]['pos'] == 'adj' and words[word['head']]['degree'] == 'comparative':
                        word['relation'] = 'genitive, comparison'
                    elif words[word['head']]['pos'] == 'adj':
                        word['relation'] = 'argument of adjective, genitive'
                elif 'case' in word and word['case'] == 'dative':
                    if words[word['head']]['pos'] == 'verb':
                        word['relation'] = 'dative, indirect object'

    # Hand-entered edits to syntactic relations.
    for relation_type, relation_edits_df in RELATION_EDITS.items():
        edits_df = pd.DataFrame(pd.DataFrame(words))
        edits_df = edits_df.merge(relation_edits_df, left_on=['book', 'chapter', 'verse', 'position'],
                                  right_on=['book', 'chapter', 'verse', 'position'])
        edit_targets = list(zip(edits_df['book'], edits_df['chapter'], edits_df['verse'], edits_df['position']))
        if edits_df.shape[0] > 0:
            for word in words:
                if (word['book'], word['chapter'], word['verse'], word['position']) in edit_targets:
                    edit_index = edit_targets.index((word['book'], word['chapter'], word['verse'], word['position']))
                    if relation_type == 'other':
                        word['relation'] = edits_df['new_relation'][edit_index]
                    else:
                        word['relation'] = relation_type + ', ' + edits_df['new_relation'][edit_index]

    # Return the words.
    return words


def get_path(words, node):
    # Start with an empty path.
    path_to_root = []

    # If this word has a head, add its path to this path.
    head_node = words[node]['head']
    if head_node is not None:
        path_to_root += [head_node]
        path_to_root += get_path(words, head_node)

    # Return the path from this node to the root.
    return path_to_root


def get_mandatory_pairs(words):
    # Start with an empty list.
    pairs = []

    # Iterate over words, looking for words that require some other word to be present.
    for i, word in enumerate(words):

        # If the word is a negation, its head requires its presence.
        if word['lemma'] in NEGATION and word['head'] is not None:
            pairs += [(word['head'], i)]

        # If the word is a determiner, its head must be present.
        if word['pos'] == 'det' and word['head'] is not None:
            pairs += [(i, word['head'])]

        # If the word has a determiner, the determiner must be present (for certain parts of speech, and not for names).
        if word['pos'] in KEEP_DETERMINER_POS and \
                not bool(re.match(GREEK_CAPITALS, word['lemma'])) and \
                word['lemma'] not in KEEP_DETERMINER_LEMMAS:
            pairs += [(i, dep) for dep in word['deps'] if words[dep]['pos'] == 'det']

        # If the word is the head of a "son of"-like relation, the relevant dependent must be present.
        if word['lemma'] in SON_OF_WORDS:
            pairs += [(i, dep) for dep in word['deps'] if words[dep]['pos'] in SON_OF_POS]

        # If the word is a preposition, its argument must be present.
        if word['pos'] == 'prep' or word['lemma'] in PSEUDO_PREPOSITIONS:
            pairs += [(i, dep) for dep in word['deps']]

        # If the word is copula-like and has a predicate, its predicate must be present.
        if word['lemma'] in COPULA:
            pairs += [(i, dep) for dep in word['deps'] if 'predicate' in words[dep]['relation']]

    # Return the result.
    return pairs


def get_licit_strings(words):
    # Initialize the licit strings with all the individual words.
    licit_strings = [(i, i) for i in range(len(words))]

    # Get all mandatory pairs of words (where, if the first is present, the second must be present as well or else the
    # string is not licit).
    mandatory_pairs = get_mandatory_pairs(words)

    # Iterate over all possible start positions.
    for first_word in range(len(words) - 1):

        # Iterate over all possible end positions.
        for last_word in range(first_word + 1, len(words)):

            # print(get_pretty_string(words, (first_word, last_word)))

            # Assume this is a licit string until proven otherwise.
            licit_string = True

            # If the string starts with a second-position clitic, it's not licit.
            if words[first_word]['lemma'] in SECOND_POSITION_CLITICS:
                licit_string = False
                # print('second-position clitic')

            # If the string ends with a second-position clitic, it's not licit, unless that's the last word in the
            # sentence.
            elif words[last_word]['lemma'] in SECOND_POSITION_CLITICS and last_word != len(words) - 1:
                licit_string = False
                # print('final second-position clitic')

            # If the string ends with a conjunction, it's not licit.
            elif words[last_word]['pos'] == 'conj':
                licit_string = False
                # print('conjunction')

            # If the string contains only part of a mandatory pair, it's not licit.
            else:
                for w1, w2 in mandatory_pairs:
                    if first_word <= w1 <= last_word and (w2 < first_word or w2 > last_word):
                        licit_string = False
                        # print('partial mandatory pair')

            # Find the lowest node shared by the paths of all the nodes in the string.  Check all the paths from non-
            # trace nodes to the root: are there any paths with any non-trace nodes that are not in the string?  (I.e.,
            # is there any path between node and lowest common root with "gaps" outside the string?)  If so, the string
            # is not licit.
            if licit_string:
                shared_nodes = set.intersection(*[set(w['path'])
                                                  for w in words[first_word:(last_word + 1)]
                                                  if 'lemma' in w and w['lemma']])
                # print(shared_nodes)
                shared_nodes = [(node, len(words[node]['path'])) for node in shared_nodes]
                # print(shared_nodes)
                # for i, w in enumerate(words):
                #     print(str(i) + ' ' + w['wordform'] + ' ' + str(w['head']))
                lowest_node = [node for node, path_length in shared_nodes
                               if path_length == max(pl for _, pl in shared_nodes)][0]
                # print(lowest_node)
                for word in range(first_word, last_word + 1):
                    if 'lemma' in words[word]:
                        lowest_node_index = words[word]['path'].index(lowest_node)
                        partial_path = words[word]['path'][lowest_node_index:]
                        gaps = [node for node in partial_path
                                if 'lemma' in words[node]
                                and (node < first_word or node > last_word)]
                        if len(gaps) > 0:
                            licit_string = False
                            # print('gap')
                            break

            # If this is a licit string, add it to the list.
            if licit_string:
                licit_strings += [(first_word, last_word)]

    # Return the list of licit strings.
    return sorted(licit_strings)


def get_citation(words):
    citations = [(BOOKS_OF_THE_BIBLE.index(word['book']), word['chapter'], word['verse']) for word in words]
    citations = list(set(citations))
    citations = sorted(citations)
    citation = PRETTY_BOOKS_OF_THE_BIBLE[citations[0][0]] + ' ' + str(citations[0][1]) + ':' + str(citations[0][2])
    if len(citations) > 1:
        last_citation = citations[len(citations) - 1]
        if last_citation[0] != citations[0][0]:
            citation += ' - ' + PRETTY_BOOKS_OF_THE_BIBLE[last_citation[0]] + ' ' + str(last_citation[1]) + ':' + str(
                last_citation[2])
        else:
            citation += '-'
            if last_citation[1] != citations[0][1]:
                citation += str(last_citation[1]) + ':' + str(last_citation[2])
            else:
                citation += str(last_citation[2])
    return citation


def get_pretty_string(sentence, limits):
    return ' '.join(sentence[1].text.split(' ')[limits[0]:(limits[1] + 1)])


if __name__ == '__main__':

    # Get all sentences from all books.
    sentences = [sentence
                 for sbl_file in SBL_FILES
                 for sentence in ElementTree.parse(SBL_DIR + '/' + sbl_file).findall('.//sentence')]

    # Connect to the database.
    con = pymysql.connect(host='localhost', user='root', password='', database='gnt')

    for s_i, sentence in enumerate(sentences):
        # Get the words in the sentence and their associated tree structure.
        words = get_tree_structure(sentence)

        # Print the sentence we're currently processing.
        print('(' + str(s_i) + ') ' + get_citation(words) + ' ' + sentence[1].text)

        # Find strings of consecutive words that all connect to a single head (with no missing intermediate heads).
        licit_strings = get_licit_strings(words)
        print('    ' + str(len(words)) + ' words, ' + str(len(licit_strings)) + ' licit strings')

        # for ls in licit_strings:
        #     print(get_pretty_string(sentence, ls))
        # print('')

        # Get the sentence ID (written to multiple tables in the database).
        sentence_id = words[0]['book'] + ' ' + str(words[0]['chapter']) + ':' + str(words[0]['verse']) + '.' + \
                      str(words[0]['position']) + ' - ' + words[-1]['book'] + ' ' + str(words[-1]['chapter']) + ':' + \
                      str(words[-1]['verse']) + '.' + str(words[-1]['position'])

        # Write the words to the database.
        with con.cursor() as cur:
            sql = """INSERT INTO words
                     (Book, Chapter, Verse, VersePosition, SentenceID, SentencePosition, Lemma, Wordform, POS, Gender,
                      Number, NCase, Person, Tense, Voice, Mood, NounClass, VerbClass)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cur.executemany(sql,
                            [(w['book'], w['chapter'], w['verse'], w['position'], sentence_id, j, w['lemma'],
                              w['wordform'], w['pos'], w['gender'], w['number'], w['case'], w['person'], w['tense'],
                              w['voice'], w['mood'], w['noun_class'], w['verb_class'])
                             for j, w in enumerate(words)])
            con.commit()

        # Write the strings to the database.
        with con.cursor() as cur:
            sql = """INSERT INTO strings (SentenceID, Citation, Start, Stop, String)
                     VALUES (%s, %s, %s, %s, %s)"""
            cur.executemany(sql,
                            [(sentence_id, get_citation(words[s[0]:(s[1] + 1)]), s[0], s[1],
                              get_pretty_string(sentence, s))
                             for s in licit_strings])
            con.commit()

        # Write the relations to the database.
        with con.cursor() as cur:
            sql = """INSERT INTO relations (SentenceID, HeadPos, DependentPos, FirstPos, LastPos, Relation)
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            cur.executemany(sql,
                            [(sentence_id, word['head'], i, min(word['head'], i), max(word['head'], i),
                              word['relation'])
                             for i, word in enumerate(words)
                             if word['head'] is not None])
            con.commit()

    # Close the database connection.
    con.close()
