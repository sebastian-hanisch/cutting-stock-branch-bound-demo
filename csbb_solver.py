"""Tiefensuche für Bin Packing (die kompakte Formulierung von Cutting Stock mit
einem Rollentyp) - n-äre statt binäre Verzweigung wie in branch-bound-demo: an
jedem Knoten wird das nächste Stück entweder in eines der bereits geöffneten Bins
gelegt, in das es noch passt, oder ein neues Bin wird geöffnet.

Bewusst KEINE Symmetrie-Mitigation (z. B. keine Regel, die zwei Bins mit
identischer Restkapazität als redundante Optionen erkennt und zusammenfasst) -
austauschbare Bins sind Bin Packings notorische, ehrliche Schwäche und sollen hier
sichtbar bleiben, nicht vorab wegoptimiert werden. Siehe README für die Begründung
und den direkten Aufhänger für das nächste Stück dieser Linie (Symmetrie-Schnitte)."""

from dataclasses import dataclass

from csbb_constants import MAX_NODES_EXPLORED
from csbb_scenario import expand_pieces


@dataclass(frozen=True)
class Node:
    id: int
    parent_id: int
    depth: int  # Anzahl bislang platzierter Stücke
    piece_width: int  # das gerade platzierte Stück, None für die Wurzel
    target: object  # ("existing", bin_index) oder ("new", bin_index), None für die Wurzel
    bins_open: int  # Anzahl offener Bins NACH dieser Entscheidung
    bound: object  # Schranke an diesem Knoten, None an Blättern
    status: str  # root | branch | prune_bound | leaf_new_best | leaf_not_best


@dataclass(frozen=True)
class SolveResult:
    best_value: int
    best_bins: tuple  # Restkapazitäten der Bins der besten gefundenen Lösung
    nodes: tuple
    incumbent_history: tuple
    truncated: bool
    pieces: tuple


def solve(instance, bound_fn, max_nodes=MAX_NODES_EXPLORED):
    pieces = expand_pieces(instance)
    n = len(pieces)
    nodes = []
    incumbent_history = []
    best = {"count": None, "bins": None}
    truncated = {"flag": False}
    next_id = [0]

    def new_node(parent_id, depth, piece_width, target, bins_open, bound, status):
        node = Node(next_id[0], parent_id, depth, piece_width, target, bins_open, bound, status)
        next_id[0] += 1
        nodes.append(node)
        return node

    root_bound = bound_fn(instance, pieces, 0, [])
    root = new_node(None, 0, None, None, 0, root_bound, "root")

    def explore(node, depth, bins):
        piece = pieces[depth]

        options = []
        for i, cap in enumerate(bins):
            if cap >= piece:
                new_bins = list(bins)
                new_bins[i] -= piece
                options.append((("existing", i), new_bins))
        options.append((("new", len(bins)), list(bins) + [instance.roll_width - piece]))

        for target, new_bins in options:
            if truncated["flag"] or len(nodes) >= max_nodes:
                truncated["flag"] = True
                return

            new_depth = depth + 1
            bins_open = len(new_bins)

            if new_depth == n:
                is_new_best = best["count"] is None or bins_open < best["count"]
                status = "leaf_new_best" if is_new_best else "leaf_not_best"
                child = new_node(node.id, new_depth, piece, target, bins_open, None, status)
                if is_new_best:
                    best["count"] = bins_open
                    best["bins"] = tuple(new_bins)
                    incumbent_history.append((child.id, bins_open))
                continue

            bound = bound_fn(instance, pieces, new_depth, new_bins)
            if best["count"] is not None and bound >= best["count"]:
                new_node(node.id, new_depth, piece, target, bins_open, bound, "prune_bound")
                continue

            child = new_node(node.id, new_depth, piece, target, bins_open, bound, "branch")
            explore(child, new_depth, new_bins)

    explore(root, 0, [])

    return SolveResult(
        best_value=best["count"],
        best_bins=best["bins"],
        nodes=tuple(nodes),
        incumbent_history=tuple(incumbent_history),
        truncated=truncated["flag"],
        pieces=pieces,
    )
