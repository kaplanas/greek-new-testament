import re
import dill
import pandas as pd
import termtables
from copy import deepcopy
from yachalk import chalk
from text_and_vocab import load_text_df, load_text_tagged
from parsing.utils import GRAMMAR, PARSER, load_grammar
from typed_dependencies import SavedParse

SAVED_PARSES_DIR = '../parsing/saved_parses/saved_parses'
BOOKS_OF_THE_NT = ['Matthew', 'Mark', 'Luke', 'John', 'Acts', 'Romans',
                   '1 Corinthians', '2 Corinthians', 'Galatians', 'Ephesians',
                   'Philippians', 'Colossians', '1 Thessalonians',
                   '2 Thessalonians', '1 Timothy', '2 Timothy', 'Titus',
                   'Philemon', 'Hebrews', 'James', '1 Peter', '2 Peter',
                   '1 John', '2 John', '3 John', 'Jude', 'Revelation']


def parse_sents(sent_length=1):
    """Parse as many sentences as possible."""
    # Load the text.
    nt = load_text_tagged()
    ts = nt.tagged_sents(refs=True)
    # Filter to sentences of the specified length.
    ts = [sent for sent in ts if len(sent[1]) == sent_length]
    parses = []
    for sent in ts:
        ap = PARSER.parse([w + '_' + m for (w, m) in sent[1]])
        try:
            trees = []
            for tree in ap:
                head_dep_rels = [(node['word'],
                                  [(tree.nodes[dep]['word'],
                                    tree.nodes[dep]['rel'])
                                   for dep in node['deps']['']])
                                 for key, node in tree.nodes.items()
                                 if key != 0]
                plausible_parse = True
                for head_word, rels in head_dep_rels:
                    if len(rels) == 0:
                        if re.match('.*_P.*', head_word) and head_word not in ['e)/cw_P-------',
                                                                               'e)/sw_P-------',
                                                                               'e)ggu/s_P-------']:
                            plausible_parse = False
                        if re.match('.*_[Ccvanplb].*', head_word) and head_word not in ['ou)=n_C-------',
                                                                                        'ga/r_C-------',
                                                                                        'de/_C-------',
                                                                                        'ge/_C-------',
                                                                                        'me/n_C-------',
                                                                                        'te/_C-------',
                                                                                        'a)/ra_C-------',
                                                                                        'me/ntoi_C-------']:
                            plausible_parse = False
                    else:
                        any_subjects = False
                        any_determiners = False
                        any_prep_arguments = False
                        for dep_word, rel in rels:
                            if rel == 'subject' and head_word != 'ou(=_B-------':
                                if any_subjects:
                                    plausible_parse = False
                                    break
                                else:
                                    any_subjects = True
                            elif rel == 'determiner' and dep_word not in ['tou=_D----GSM',
                                                                          'th=s_D----GSF']:
                                if any_determiners:
                                    plausible_parse = False
                                    break
                                else:
                                    any_determiners = True
                            elif rel == 'argument' and re.match('.*_P.*', head_word) and head_word != 'pro/s_P-------':
                                if any_prep_arguments:
                                    plausible_parse = False
                                    break
                                else:
                                    any_prep_arguments = True
                    if not plausible_parse:
                        break
                if plausible_parse:
                    trees.append(tree)
        except UnboundLocalError:
            trees = []
        sp = SavedParse(sent[0],
                        ' '.join(w for w, _ in sent[1]),
                        [w + '_' + m for w, m in sent[1]],
                        trees)
        parses.append(sp)
    return parses


def get_sent_ids(parses):
    """Get a list of just references and wordforms, to uniquely identify a sentence."""
    if len(parses) == 0:
        return []
    else:
        return [(p.reference, p.sent_str) for p in parses]


def get_parses_filename(pathname=SAVED_PARSES_DIR, sent_length=None):
    """Get the filename for saved parses of a given length."""
    parses_pathname = pathname
    if sent_length is not None:
        parses_filename = parses_pathname + '_' + str(sent_length)
    parses_filename = parses_filename + '.dill'
    return parses_filename


def save_parses(parses, pathname=SAVED_PARSES_DIR):
    """Save parses as a dill file."""
    for k, v in parses.items():
        with open(get_parses_filename(pathname, k), 'wb') as file:
            dill.dump(parses[k], file)


def load_parses(pathname=SAVED_PARSES_DIR, sent_length=None):
    """Load the saved parses from a dill file."""
    try:
        with open(get_parses_filename(pathname, sent_length), 'rb') as file:
            parses = dill.load(file)
    except:
        parses = []
    return parses


def print_parse(tree, node_id=None, features=False, margin=70, indent=0,
                top_level=True):
    """Pretty-print parse trees."""
    if node_id is None:
        node_id = tree.root['address']
    nodesep = ""
    parens = "[]"
    parsed_atom = tree.nodes[node_id]['word']
    wordform = re.sub('_.*', '', parsed_atom)
    morph = re.sub('.*_', '', parsed_atom)
    label_to_print = chalk.blue(wordform)
    new_indent = indent + len(wordform) + 2
    if features:
        label_to_print = label_to_print + '_' + chalk.green(morph)
        new_indent = new_indent + len(morph) + 1
    if node_id != tree.root['address']:
        label_to_print = label_to_print + ' ' + tree.nodes[node_id]['rel']
    s = f"{parens[0]}{label_to_print}{nodesep}"
    for child_i in tree.nodes[node_id]['deps']['']:
        if child_i == 0:
            child_sep = " "
        else:
            child_sep = "\n" + " " * new_indent
        s += (
            child_sep + print_parse(tree, child_i, features, margin,
                                    new_indent, top_level=False)
        )
    if top_level:
        print(s + parens[1])
    else:
        return s + parens[1]


def print_parses(parses, first_index=0, features=False):
    """Show the parse trees of a set of parses."""
    for i, parse in enumerate(parses):
        print('*** [' + str(i + first_index) + '] ' + parse.reference + ' - ' + parse.sent_str + ' ***')
        print('')
        trees = parse.other_parses
        if parse.parse is not None:
            print('BEST PARSE')
            print_parse(parse.parse, features=features)
            print('')
        for j, tree in enumerate(trees):
            print('[' + str(j) + ']')
            print_parse(tree, features=features)
            print('')


def find_unused_rules():
    """Find rules in the grammar that aren't being used in any best parses."""
    for production in GRAMMAR._productions:
        found_use_before = False
        found_use_after = False
        if production._position == 'before' or production._position == 'immediately_before':
            found_use_after = True
        elif production._position == 'after' or production._position == 'immediately_after':
            found_use_before = True
        sent_lengths = sorted((k for k in parses.keys()), reverse=True)
        while not (found_use_before and found_use_after) and len(sent_lengths) > 0:
            sl = sent_lengths.pop()
            indexes = [i for i, p in enumerate(parses[sl]) if p.parse is not None]
            while not (found_use_before and found_use_after) and len(indexes) > 0:
                i = indexes.pop()
                parse = parses[sl][i].parse
                current_head = parse.root['address']
                current_heads = [current_head]
                current_deps = [deepcopy(parse.nodes[current_head]['deps'][''])]
                while not (found_use_before and found_use_after) and len(current_heads) > 0:
                    while len(current_heads) > 0 and len(current_deps[-1]) == 0:
                        current_heads.pop()
                        current_deps.pop()
                    if len(current_heads) > 0:
                        current_head = current_heads[-1]
                        current_dep = current_deps[-1].pop()
                        if production.type_of((parse.nodes[current_head]['word'], current_head),
                                              (parse.nodes[current_dep]['word'], current_dep),
                                              GRAMMAR._lexicon) == \
                                parse.nodes[current_dep]['rel']:
                            if current_head > current_dep:
                                found_use_before = True
                            elif current_head < current_dep:
                                found_use_after = True
                        current_heads.append(current_dep)
                        current_deps.append(deepcopy(parse.nodes[current_dep]['deps']['']))
        if not found_use_before:
            print(production)
            if production._position == 'any':
                print('...before')
        if not found_use_after:
            print(production)
            if production._position == 'any':
                print('...after')


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    chalk.enable_full_colors()
    sent_lengths = [i + 1 for i in range(14)]
    # sent_lengths = [14]
    old_parses = {}
    old_parse_counts = {}
    parses = {}
    parse_counts = {}
    changes = {}
    nt = load_text_tagged()
    ts = nt.tagged_sents(refs=True)
    book_completion = {book: [0, 0] for book in BOOKS_OF_THE_NT}
    for sent in ts:
        book = re.sub(r' [0-9]+:[0-9]+(-[0-9]+)?', '', sent[0])
        book_completion[book][1] += len(sent[1])
    for sl in sent_lengths:
        print('parsing sentences of length ' + str(sl) + '...')
        old_parses[sl] = load_parses(sent_length=sl)
        old_sis = get_sent_ids(old_parses[sl])
        parses[sl] = parse_sents(sent_length=sl)
        sis = get_sent_ids(parses[sl])
        old_parse_counts[sl] = {}
        parse_counts[sl] = {}
        changes[sl] = {'parsed': [],
                       'new': [],
                       'same': [],
                       'none': [],
                       'unparsed': []}
        for i, p in enumerate(parses[sl]):
            if len(p.other_parses) > 0:
                book = re.sub(r' [0-9]+:[0-9]+(-[0-9]+)?', '', p.reference)
                book_completion[book][0] += len(p.tokens)
            n_parses = len(p.other_parses)
            if n_parses in parse_counts[sl].keys():
                parse_counts[sl][n_parses] += 1
            else:
                parse_counts[sl][n_parses] = 1
            if sis[i] in old_sis:
                old_parse = old_parses[sl][old_sis.index(sis[i])]
                n_old_parses = len(old_parse.other_parses)
                old_best_parse = old_parse.parse
                if old_best_parse is not None:
                    n_old_parses += 1
                    if old_best_parse.to_conll(4) in [op.to_conll(4)
                                                      for op in p.other_parses]:
                        p.set_best_parse([op.to_conll(4)
                                          for op in p.other_parses].index(old_best_parse.to_conll(4)))
                        changes[sl]['parsed'].append(p)
                    else:
                        changes[sl]['unparsed'].append(p)
                else:
                    if len(set(op.to_conll(4) for op in p.other_parses) -
                           set(op.to_conll(4) for op in old_parse.other_parses)) > 0:
                        changes[sl]['new'].append(p)
                    elif len(p.other_parses) == 0:
                        changes[sl]['none'].append(p)
                    else:
                        changes[sl]['same'].append(p)
                if n_old_parses in old_parse_counts[sl].keys():
                    old_parse_counts[sl][n_old_parses] += 1
                else:
                    old_parse_counts[sl][n_old_parses] = 1
            else:
                if len(p.other_parses) == 0:
                    changes[sl]['none'].append(p)
                else:
                    changes[sl]['new'].append(p)
    print('')
    termtables.print([[book,
                       str(chalk.red('0 %'))
                       if completion[0] == 0
                       else str(chalk.green('100 %'))
                       if completion[0] == completion[1]
                       else str(round((completion[0] / completion[1]) * 100, 1)) + ' %']
                      for book, completion in book_completion.items()],
                     header=['Book', '% Complete'],
                     style=termtables.styles.markdown,
                     padding=(0, 1),
                     alignment='lr')
    print('')
    all_parse_lengths = sorted(set([n_old_parses
                                    for sl in old_parse_counts.keys()
                                    for n_old_parses in old_parse_counts[sl].keys()] +
                                   [n_parses
                                    for sl in parse_counts.keys()
                                    for n_parses in parse_counts[sl].keys()]))
    parse_counts['Total'] = {n_parses: sum(parse_counts[sl][n_parses]
                                           for sl in parse_counts.keys()
                                           if n_parses in parse_counts[sl].keys())
                             for n_parses in all_parse_lengths}
    old_parse_counts['Total'] = {n_parses: sum(old_parse_counts[sl][n_parses]
                                               for sl in old_parse_counts.keys()
                                               if n_parses in old_parse_counts[sl].keys())
                                 for n_parses in all_parse_lengths}
    changes['Total'] = {diff: [c for sl in changes.keys() for c in changes[sl][diff]]
                        for diff in ['parsed', 'new', 'same', 'none', 'unparsed']}
    termtables.print([[str(sl)] +
                      [str(chalk.blue(str(old_parse_counts[sl][n_parses]) + '+' +
                                      str(parse_counts[sl][n_parses] - old_parse_counts[sl][n_parses])))
                       if n_parses in parse_counts[sl].keys() and \
                          n_parses in old_parse_counts[sl].keys() and \
                          parse_counts[sl][n_parses] > old_parse_counts[sl][n_parses]
                       else str(chalk.yellow(str(old_parse_counts[sl][n_parses]) + '-' +
                                             str(old_parse_counts[sl][n_parses] - parse_counts[sl][n_parses])))
                       if n_parses in parse_counts[sl].keys() and \
                          n_parses in old_parse_counts[sl].keys() and \
                          parse_counts[sl][n_parses] < old_parse_counts[sl][n_parses]
                       else str(chalk.blue('0+' + str(parse_counts[sl][n_parses])))
                       if n_parses in parse_counts[sl].keys() and \
                          n_parses not in old_parse_counts[sl].keys()
                       else str(chalk.yellow(str(old_parse_counts[sl][n_parses]) + '-' +
                                             str(old_parse_counts[sl][n_parses])))
                       if n_parses not in parse_counts[sl].keys() and \
                          n_parses in old_parse_counts[sl].keys()
                       else str(parse_counts[sl][n_parses])
                       if n_parses in parse_counts[sl].keys()
                       else ' '
                       for n_parses in all_parse_lengths]
                      for sl in parse_counts.keys()],
                     header=['Length'] + [str(n_parses)
                                          for n_parses in all_parse_lengths],
                     style=termtables.styles.markdown,
                     padding=(0, 1),
                     alignment='l' + ('r' * len(all_parse_lengths)))
    print('')
    termtables.print([[str(sl)] +
                      [str(chalk.red(str(len(changes[sl][diff]))))
                       if diff == 'unparsed' and len(changes[sl][diff]) > 0
                       else str(chalk.yellow(str(len(changes[sl][diff]))))
                       if diff == 'same' and len(changes[sl][diff]) > 0
                       else str(chalk.blue(str(len(changes[sl][diff]))))
                       if diff == 'new' and len(changes[sl][diff]) > 0
                       else str(chalk.green(str(len(changes[sl][diff]))))
                       if diff == 'parsed' and len(changes[sl][diff]) > 0
                       else ' '
                       if len(changes[sl][diff]) == 0
                       else str(len(changes[sl][diff]))
                       for diff in changes[sl].keys()]
                      for sl in changes.keys()],
                     header=['Length', 'Parsed', 'New candidates',
                             'Same candidates', 'No candidates',
                             'Newly unparsed'],
                     style=termtables.styles.markdown,
                     padding=(0, 1),
                     alignment='l' + ('r' * 5))
    print('')
