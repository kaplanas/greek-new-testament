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

    def __init__(self, lhs, rhs, rel, position):
        """
        Construct a new ``TypedDependencyProduction``.
        """
        DependencyProduction.__init__(self, lhs, rhs)
        self._rel = rel
        self._position = position

    def __str__(self):
        """
        Return a verbose string representation of the
         ``TypedDependencyProduction``.
        """
        return super().__str__() + ' (' + self._rel + ', ' + self._position + ')'

    def matches(self, head, dep):
        """
        Check whether the production matches the head and dependent provided.
        """
        if self._lhs == head[0]:
            for rhs in self._rhs:
                if rhs == dep[0] and \
                        ((self._position == 'any') or \
                         (self._position == 'before' and dep[1] < head[1]) or \
                         (self._position == 'after' and dep[1] > head[1]) or \
                         (self._position == 'immediately_before' and dep[1] == head[1] - 1) or \
                         (self._position == 'immediately_after' and dep[1] == head[1] + 1)):
                    return True
        return False

    def type_of(self, head, dep):
        """
        Return the type of the production from the head to the dependent (if any).
        """
        if self.matches(head, dep):
            return self._rel
        else:
            return None


# The following is mostly copied from nltk's grammar module, with minimal
# tweaks that allow dependency rules to specify a relation type and a position.

_READ_TDG_RE = re.compile(
    r"""^\s*                # leading whitespace
                              ('[A-Za-z_]+')\s*     # relation type (no quotes); letters and underscore only
                              ('[A-Za-z_]+')\s*     # position (no quotes); letters and underscore only
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
_SPLIT_TDG_RE = re.compile(r"""('[^']'|[-=]+>|"[^"]+"|'[^']+'|\|)""")


def _read_typed_dependency_production(s):
    if not _READ_TDG_RE.match(s):
        raise ValueError("Bad production string")
    pieces = _SPLIT_TDG_RE.split(s)
    pieces = [p for i, p in enumerate(pieces) if i % 2 == 1]
    rel = pieces[0].strip("'\" ")
    position = pieces[1].strip("'\" ")
    lhside = pieces[2].strip("'\"")
    rhsides = [[]]
    for piece in pieces[4:]:
        if piece == "|":
            rhsides.append([])
        else:
            rhsides[-1].append(piece.strip("'\""))
    return [TypedDependencyProduction(lhside, rhside, rel, position)
            for rhside in rhsides]


class TypedDependencyGrammar(DependencyGrammar):
    """
    Adds typed relations to nltk's DependencyGrammar.
    """

    @classmethod
    def fromstring(cls, input):
        productions = []
        for linenum, line in enumerate(input.split("\n")):
            line = line.strip()
            if line.startswith("#") or line == "":
                continue
            try:
                productions += _read_typed_dependency_production(line)
            except ValueError as e:
                raise ValueError(f"Unable to parse line {linenum}: {line}") from e
        if len(productions) == 0:
            raise ValueError("No productions found!")
        return cls(productions)

    def contains(self, head, dep):
        """
        Return whether the grammar contains the specified dependency.
        """
        for production in self._productions:
            if production.matches(head, dep):
                return True
        return False

    def type_of(self, head, dep):
        """
        Return the types of the productions from the head to the dependent (if any).
        """
        rels = [production.type_of(head, dep)
                for production in self._productions
                if production.matches(head, dep)]
        if len(rels) > 0:
            return rels
        return None

    def position_of(self, head, dep):
        """
        Return the type of the production from the head to the mod (if any).
        """
        positions = [production._pos
                     for production in self._productions
                     for possible_dep in production._rhs
                     if production._lhs == head and possible_dep == dep]
        if len(positions) > 0:
            return positions
        return None


class TypedNonprojectiveDependencyParser(NonprojectiveDependencyParser):
    """
    Adds typed relations to nltk's NonprojectiveDependencyParser.
    """

    def get_possible_heads_deps(self, tokens):
        """
        Get all possible heads and dependents of each token.
        """

        # Collect the nodes and edges of the dependency graph.
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
        return((possible_heads, possible_deps))

    def parse(self, tokens):
        """
        Use the algorithm described by Gabow & Myers (1978) to find all
        spanning trees of the graph of dependencies.
        https://publications.mpi-cbg.de/Gabow_1978_5452.pdf
        """

        # For each node, find all analyses with that node as root.
        possible_heads, possible_deps = self.get_possible_heads_deps(tokens)
        n_tokens = len(tokens)
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
                    done_growing = True
                    if len([edge for edge in F if edge[0] == e[0] and edge[1] > v]) > 0:
                        done_growing = False
                    elif len(F) == 0:
                        done_growing = True
                    elif len(current_analyses) > 0:
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
                graph.nodes[i].update({'address': i})
            root_address = root_node + 1
            graph.root = graph.nodes[root_address]
            graph.nodes[0]['deps']['ROOT'].append(root_address)
            for edge in tree:
                address = edge[0] + 1
                dep_address = edge[1] + 1
                graph.nodes[dep_address].update({'head': address})
                graph.nodes[address]['deps'][''].append(dep_address)
            for address in range(len(graph.nodes)):
                if address > 0:
                    graph.nodes[address].update({'word': tokens[address - 1]})
            graphs = [graph]
            for address in range(len(graph.nodes)):
                if address > 0:
                    for dep_address in graph.nodes[address]['deps']['']:
                        rel_types = self._grammar.type_of((tokens[address - 1], address - 1),
                                                          (tokens[dep_address - 1], dep_address - 1))
                        if len(rel_types) == 1:
                            for g in graphs:
                                g.nodes[dep_address].update({'rel': rel_types[0]})
                        else:
                            orig_count = len(graphs)
                            for i in range(orig_count):
                                for rel_type in rel_types[1:]:
                                    graphs.append(deepcopy(graphs[i]))
                                    graphs[-1].nodes[dep_address].update({'rel': rel_type})
                                graphs[i].nodes[dep_address].update({'rel': rel_types[0]})
            for graph in graphs:
                yield graph
