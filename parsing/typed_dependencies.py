import re
from copy import deepcopy
from nltk.sem.logic import Variable
from nltk.featstruct import FeatStructReader
from nltk.parse import NonprojectiveDependencyParser
from nltk.parse.dependencygraph import DependencyGraph
from nltk.grammar import DependencyProduction, DependencyGrammar, read_grammar


class SavedParse:

    def __init__(self, reference, sent_str, tokens, parses):
        self.reference = reference
        self.sent_str = sent_str
        self.tokens = tokens
        self.parse = None
        self.other_parses = parses

    def set_best_parse(self, index):
        if self.parse is not None:
            self.other_parses = self.other_parses + [self.parse]
        self.parse = self.other_parses[index]
        self.other_parses.pop(index)



class TypedDependencyProduction(DependencyProduction):
    """
    Adds relation types to nltk's DependencyProduction.
    """

    def __init__(self, lhs, rhs, rel):
        """
        Construct a new ``TypedDependencyProduction``.
        """
        DependencyProduction.__init__(self, lhs, rhs)
        self._rel = rel

    def __str__(self):
        """
        Return a verbose string representation of the
         ``TypedDependencyProduction``.
        """
        return super().__str__() + ' (' + self._rel + ')'


# The following is mostly copied from nltk's grammar module, with minimal
# tweaks that allow dependency rules to specify a relation type.

_READ_TDG_RE = re.compile(
    r"""^\s*                # leading whitespace
                              ([A-Za-z_]+)\s*     # relation type (no quotes); letters and underscore only
                              ('[^']+')\s*        # single-quoted lhs
                              (?:[-=]+>)\s*        # arrow
                              (?:(                 # rhs:
                                   "[^"]+"         # doubled-quoted terminal
                                 | '[^']+'         # single-quoted terminal
                                 | \|              # disjunction
                                 )
                                 \s*)              # trailing space
                                 *$""",  # zero or more copies
    re.VERBOSE,
)
_SPLIT_TDG_RE = re.compile(r"""('^[A-Za-z_]+|'[^']'|[-=]+>|"[^"]+"|'[^']+'|\|)""")


def _read_typed_dependency_production(s):
    if not _READ_TDG_RE.match(s):
        raise ValueError("Bad production string")
    pieces = _SPLIT_TDG_RE.split(s)
    pieces = [p for i, p in enumerate(pieces) if i == 0 or i % 2 == 1]
    rel = pieces[0].strip("'\" ")
    lhside = pieces[1].strip("'\"")
    rhsides = [[]]
    for piece in pieces[3:]:
        if piece == "|":
            rhsides.append([])
        else:
            rhsides[-1].append(piece.strip("'\""))
    return [TypedDependencyProduction(lhside, rhside, rel) for rhside in rhsides]


class TypedDependencyGrammar(DependencyGrammar):
    """
    Adds typed relations to nltk's DependencyGrammar.
    """

    @classmethod
    def fromstring(cls, input):
        fsr = FeatStructReader()
        start, productions = read_grammar(input, fsr.read_partial)
        return cls(productions)

    def load_lexicon(self, lexicon_input):
        """
        Read a lexicon file and store it as a dict.
        """
        fsr = FeatStructReader()
        start, lexicon = read_grammar(lexicon_input, fsr.read_partial)
        self._lexicon = {p._rhs[0]: p._lhs
                         for p in lexicon}

    def contains(self, head, dep):
        """
        Return whether the grammar contains the specified dependency.
        """
        return len(self.type_of(head, dep)) > 0

    def type_of(self, head, dep):
        """
        Return the type of the production from the head to the mod (if any).
        """
        rels = []
        for p in self._productions:
            fs_left = p._lhs.unify(self._lexicon[dep[0]])
            if fs_left is not None:
                bindings_left = {item[1].name: fs_left[item[0]]
                                 for item in p._lhs.items()
                                 if isinstance(item[1], Variable)}
                fs_right = p._rhs[0].unify(self._lexicon[head[0]])
                if fs_right is not None:
                    wrong_position = False
                    if 'POSITION' in p._lhs:
                        if p._lhs['POSITION'] == 'before' and dep[1] > head[1]:
                            wrong_position = True
                        elif p._lhs['POSITION'] == 'immediately_before' and dep[1] != head[1] - 1:
                            wrong_position = True
                        elif p._lhs['POSITION'] == 'after' and dep[1] < head[1]:
                            wrong_position = True
                        elif p._lhs['POSITION'] == 'immediately_after' and dep[1] != head[1] + 1:
                            wrong_position = True
                    found_mismatch = False
                    for item in p._rhs[0].items():
                        if isinstance(item[1], Variable) and \
                                item[1].name not in ['REL_TYPE', 'POSITION'] and \
                                item[1].name in bindings_left.keys() and \
                                not isinstance(bindings_left[item[1].name], Variable) and \
                                bindings_left[item[1].name] != fs_right[item[0]]:
                            found_mismatch = True
                    if not wrong_position and not found_mismatch:
                        rels.append(fs_left['REL_TYPE'])
        return rels


class TypedNonprojectiveDependencyParser(NonprojectiveDependencyParser):
    """
    Adds typed relations to nltk's NonprojectiveDependencyParser.
    """

    def parse(self, tokens):
        """
        Use the algorithm described by Gabow & Myers (1978) to find all
        spanning trees of the graph of dependencies.
        """

        # Collect the nodes and edges of the dependency graph.
        n_tokens = len(tokens)
        possible_heads = []
        possible_deps = [[] for i in enumerate(tokens)]
        for i, word in enumerate(tokens):
            heads = []
            for j, head in enumerate(tokens):
                if i != j and self._grammar.contains((head, j), (word, i)):
                    heads.append(j)
                    possible_deps[j].append(i)
            possible_heads.append(heads)
        for j in range(len(possible_deps)):
            possible_deps[j].sort(reverse=True)

        # For each node, find all analyses with that node as root.
        analyses = []
        for r in range(n_tokens):
            temp_possible_heads = deepcopy(possible_heads)
            temp_possible_deps = deepcopy(possible_deps)
            current_analyses = []
            T = set()
            tree_stack = []
            T_vertices = set()
            tree_vertices_stack = []
            edge_stack = []
            FF_stack = []
            F = [(r, dep) for dep in temp_possible_deps[r]]
            done_growing = False
            init = True
            while len(F) > 0 and (init or len(tree_stack) > 0 or len(FF_stack) > 0):
                init = False
                while len(T_vertices) < n_tokens and len(F) > 0 and not done_growing:
                    done_growing = False
                    e = F.pop()
                    edge_stack.append(e)
                    v = e[1]
                    if len(FF_stack) < len(edge_stack):
                        FF_stack.append([])
                    T.add(e)
                    tree_stack.append(deepcopy(T))
                    T_vertices = set([r] + [edge[1] for edge in T])
                    tree_vertices_stack.append(deepcopy(T_vertices))
                    for w in sorted(temp_possible_deps[v], reverse=True):
                        if w not in T_vertices:
                            F.append((v, w))
                    F = [edge for edge in F if not (edge[1] == v and edge[0] in T_vertices)]
                if len(T_vertices) == n_tokens:
                    current_analyses.append(tree_stack[-1])
                if len(edge_stack) > 0:
                    e = edge_stack.pop()
                    v = e[1]
                    F = [edge for edge in F
                         if not (edge[0] == v and edge[1] not in T_vertices)]
                    for w in sorted(temp_possible_heads[v], reverse=True):
                        if w in T_vertices and (w, v) != e:
                            F.append((w, v))
                    F.sort(reverse=True)
                    T.remove(e)
                    tree_stack.pop()
                    T_vertices.remove(v)
                    tree_vertices_stack.pop()
                    if e[0] in temp_possible_heads[v]:
                        temp_possible_heads[v].remove(e[0])
                    if v in temp_possible_deps[e[0]]:
                        temp_possible_deps[e[0]].remove(v)
                    FF_stack[-1].append(e)
                    if len(current_analyses) > 0:
                        done_growing = True
                        for head in temp_possible_heads[v]:
                            current_node = head
                            v_is_ancestor = False
                            found_root = current_node == r
                            while not v_is_ancestor and not found_root:
                                current_node = [edge[0]
                                                for edge in current_analyses[-1]
                                                if edge[1] == current_node][0]
                                if current_node == v:
                                    v_is_ancestor = True
                                elif current_node == r:
                                    found_root = True
                            if not v_is_ancestor:
                                done_growing = False
                                break
                if done_growing and len(FF_stack) > 0:
                    FF = FF_stack.pop()
                    for edge in FF:
                        F.append(edge)
                        temp_possible_heads[edge[1]].append(edge[0])
                        temp_possible_heads[edge[1]].sort()
                        temp_possible_deps[edge[0]].append(edge[1])
                        temp_possible_deps[edge[1]].sort()
                    F.sort(reverse=True)
            analyses += [(r, ca) for ca in current_analyses]
        if n_tokens == 1:
            analyses = [(0, set())]

        # Create DependencyGraphs for the final parses.
        for root_node, tree in analyses:
            graph = DependencyGraph()
            for i in range(n_tokens + 1):
                graph.nodes[i].update({"address": i})
            root_address = root_node + 1
            graph.root = graph.nodes[root_address]
            graph.nodes[0]["deps"]["ROOT"].append(root_address)
            for edge in tree:
                address = edge[0] + 1
                dep_address = edge[1] + 1
                graph.nodes[address]["deps"][""].append(dep_address)
            for address in range(len(graph.nodes)):
                if address > 0:
                    graph.nodes[address].update({"word": tokens[address - 1]})
            graphs = [graph]
            for address in range(len(graph.nodes)):
                if address > 0:
                    for dep_address in graph.nodes[address]["deps"][""]:
                        rel_types = self._grammar.type_of((tokens[address - 1], address - 1),
                                                          (tokens[dep_address - 1], dep_address - 1))
                        if len(rel_types) == 1:
                            for g in graphs:
                                g.nodes[dep_address].update({"rel": rel_types[0]})
                        else:
                            orig_count = len(graphs)
                            for i in range(orig_count):
                                for rel_type in rel_types[1:]:
                                    graphs.append(deepcopy(graphs[i]))
                                    graphs[-1].nodes[dep_address].update({"rel": rel_type})
                                graphs[i].nodes[dep_address].update({"rel": rel_types[0]})
            for graph in graphs:
                yield graph
