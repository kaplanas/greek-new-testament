import re
from copy import deepcopy
from nltk.parse import NonprojectiveDependencyParser
from nltk.parse.dependencygraph import DependencyGraph
from nltk.grammar import DependencyProduction, DependencyGrammar


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

    def type_of(self, head, mod):
        """
        Return the type of the production from the head to the mod (if any).
        """
        rels = [production._rel
                for production in self._productions
                for possibleMod in production._rhs
                if production._lhs == head and possibleMod == mod]
        if len(rels) > 0:
            return rels
        return None


class TypedNonprojectiveDependencyParser(NonprojectiveDependencyParser):
    """
    Adds typed relations to nltk's NonprojectiveDependencyParser.
    """

    def parse(self, tokens):
        """
        Use the algorithm described by Takeaki Uno to find all spanning trees
        of the graph of dependencies.
        """
        # http://research.nii.ac.jp/~uno/papers/isaac96web.pdf

        def get_root(tree, n_tokens):
            """Get the unique root node of a tree, if it exists."""
            head_counts = [0] * n_tokens
            for edge in tree:
                head_counts[edge[1]] += 1
            roots = [i for i, hc in enumerate(head_counts) if hc == 0]
            if len(roots) == 1:
                return(roots[0])
            else:
                return(None)

        def get_non_back_arcs(tree, root_node, tree_0, possible_heads):
            """Get the valid back-arcs for a tree."""
            if tree == tree_0:
                min_dep = float('inf')
            else:
                min_dep = min(edge[1] for edge in tree_0 if edge not in tree)
            non_back_arcs = []
            for dep, heads in enumerate(possible_heads):
                if dep < min_dep:
                    for possible_head in heads:
                        if [possible_head, dep] not in tree:
                            found_dep = False
                            found_root = False
                            current_node = possible_head
                            while not (found_dep or found_root):
                                if current_node == root_node:
                                    found_root = True
                                else:
                                    mother = [edge[0] for edge in tree if edge[1] == current_node][0]
                                    if mother == dep:
                                        found_dep = True
                                    else:
                                        current_node = mother
                            if not found_dep:
                                non_back_arcs.append([possible_head, dep])
            return(list(reversed(non_back_arcs)))

        # Collect the nodes and edges of the dependency graph.
        possible_heads = []
        possible_deps = [[] for i in enumerate(tokens)]
        for i, word in enumerate(tokens):
            heads = []
            for j, head in enumerate(tokens):
                if i != j and self._grammar.contains(head, word):
                    heads.append(j)
                    possible_deps[j].append(i)
            possible_heads.append(heads)
        for j in range(len(possible_deps)):
            possible_deps[j].sort(reverse=True)
        possible_deps_stack = deepcopy(possible_deps)

        # Create the initial tree by doing a depth-first search.
        # https://www.cs.cmu.edu/~15451-f17/lectures/lec11-DFS-strong-components.pdf
        T0 = []
        is_dep = [False] * len(tokens)
        num = [0] * len(tokens)
        mark = [False] * len(tokens)
        i = 0
        node_stack = [i for i in range(len(tokens) - 1, -1, -1)]
        while len(node_stack) > 0:
            node_index = node_stack[-1]
            i = i + 1
            num[node_index] = i
            mark[node_index] = True
            if len(possible_deps_stack[node_index]) > 0:
                dep_node_index = possible_deps_stack[node_index].pop()
                if num[dep_node_index] == 0 or not (is_dep[dep_node_index] or mark[dep_node_index]):
                    T0.append([node_index, dep_node_index])
                    is_dep[dep_node_index] = True
                    node_stack.append(dep_node_index)
            else:
                mark[node_index] = False
                node_stack.pop()

        # If the initial tree is a valid tree, add it to the list of analyses
        # and look for more.
        # http://research.nii.ac.jp/~uno/papers/isaac96web.pdf
        analyses = []
        tree_stack = []
        non_back_arc_stack = []
        root_node = get_root(T0, len(tokens))
        if root_node is not None:
            analyses.append((root_node, T0))
            tree_stack.append((root_node, T0))
            non_back_arc_stack.append(get_non_back_arcs(tree_stack[-1][1],
                                                        tree_stack[-1][0],
                                                        T0, possible_heads))
            while len(non_back_arc_stack) > 0:
                while len(non_back_arc_stack[-1]) > 0:
                    new_tree = deepcopy(tree_stack[-1][1])
                    new_tree = [edge for edge in new_tree
                                if edge[1] != non_back_arc_stack[-1][-1][1]]
                    new_tree.append(non_back_arc_stack[-1][-1])
                    new_root = get_root(new_tree, len(tokens))
                    analyses.append((new_root, new_tree))
                    non_back_arc_stack[-1].pop()
                    tree_stack.append((new_root, new_tree))
                    non_back_arc_stack.append(get_non_back_arcs(new_tree,
                                                                new_root, T0,
                                                                possible_heads))
                non_back_arc_stack.pop()
                tree_stack.pop()

        # Create DependencyGraphs for the final parses.
        for root_node, tree in analyses:
            graph = DependencyGraph()
            for i in range(len(tokens) + 1):
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
                        rel_types = self._grammar.type_of(tokens[address - 1],
                                                          tokens[dep_address - 1])
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
