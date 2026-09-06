import pytest

from csbb_bounds import strong_bound, weak_bound
from csbb_scenario import expand_pieces, generate_instance


def _true_min_bins_for_completion(instance, pieces, depth, bins):
    """Bruteforce: minimale ZUSÄTZLICHE Bins, um pieces[depth:] in die gegebenen
    (teilweise gefüllten) bins unterzubringen - Referenz, um zu prüfen, dass eine
    Schranke niemals überschätzt."""
    best = {"count": len(bins) + (len(pieces) - depth)}  # triviale obere Schranke

    def assign(idx, cur_bins):
        if len(cur_bins) >= best["count"]:
            return
        if idx == len(pieces):
            best["count"] = min(best["count"], len(cur_bins))
            return
        piece = pieces[idx]
        for i, cap in enumerate(cur_bins):
            if cap >= piece:
                cur_bins[i] -= piece
                assign(idx + 1, cur_bins)
                cur_bins[i] += piece
        cur_bins.append(instance.roll_width - piece)
        assign(idx + 1, cur_bins)
        cur_bins.pop()

    assign(depth, list(bins))
    return best["count"]


@pytest.mark.parametrize("bound_fn", [weak_bound, strong_bound])
def test_bound_never_overestimates_true_minimum(bound_fn):
    for seed in range(10):
        instance = generate_instance(n_types=3, roll_width=100, max_demand=2, seed=seed)
        pieces = expand_pieces(instance)
        # Ein paar zufällige Teilzustände durchprobieren (Depth + ein paar offene Bins)
        for depth in range(0, len(pieces) + 1, 2):
            bins = [] if depth == 0 else [instance.roll_width // 2]
            bound = bound_fn(instance, pieces, depth, bins)
            true_min = _true_min_bins_for_completion(instance, pieces, depth, bins)
            assert bound <= true_min, f"seed={seed} depth={depth} bound={bound} true_min={true_min}"


def test_strong_bound_never_weaker_than_weak_bound():
    for seed in range(15):
        instance = generate_instance(n_types=4, roll_width=100, max_demand=2, seed=seed)
        pieces = expand_pieces(instance)
        for depth in range(len(pieces) + 1):
            w = weak_bound(instance, pieces, depth, [])
            s = strong_bound(instance, pieces, depth, [])
            assert s >= w, f"seed={seed} depth={depth}"


def test_bounds_match_hand_computed_example():
    # 3 Stücke der Breite 6, Rollenbreite 10: je zwei Stücke passen NICHT zusammen
    # in ein Bin (6+6=12>10), jedes braucht ein eigenes -> wahres Optimum 3.
    # Die schwache Schranke sieht nur die Gesamtbreite (18/10 aufgerundet = 2) und
    # unterschätzt hier bewusst - genau das rechtfertigt die starke Schranke, die
    # große Stücke (>W/2) erkennt und hier exakt auf 3 kommt.
    from csbb_scenario import CuttingStockInstance

    instance = CuttingStockInstance(roll_width=10, item_widths=(6,), item_demands=(3,))
    pieces = expand_pieces(instance)
    assert weak_bound(instance, pieces, 0, []) == 2
    assert strong_bound(instance, pieces, 0, []) == 3
