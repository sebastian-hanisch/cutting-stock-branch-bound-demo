from csbb_bounds import strong_bound, weak_bound
from csbb_constants import PRESETS
from csbb_evaluation import symmetry_comparison
from csbb_scenario import CuttingStockInstance, expand_pieces, generate_instance
from csbb_solver import solve


def _dp_optimum(pieces, roll_width):
    """Unabhängige Referenz: exaktes Bin Packing per Bitmasken-DP (minimale Bin-Anzahl,
    bei Gleichstand minimale Füllung des letzten Bins) - teilt keinen Code mit der Suche."""
    n = len(pieces)
    inf = (10**9, 10**9)
    dp = [inf] * (1 << n)
    dp[0] = (1, 0)
    for mask in range(1 << n):
        bins, fill = dp[mask]
        if bins >= 10**9:
            continue
        for i in range(n):
            if mask >> i & 1:
                continue
            cand = (bins, fill + pieces[i]) if fill + pieces[i] <= roll_width else (bins + 1, pieces[i])
            nm = mask | (1 << i)
            if cand < dp[nm]:
                dp[nm] = cand
    return dp[(1 << n) - 1][0] if n else 0


def _width_twin(instance):
    """Die frühere "Zwillingsinstanz" (jede Bedarfseinheit ein eigener Typ mit winzig
    verschobener Breite), diesmal passungserhaltend: Rollenbreite um die Summe aller
    Verschiebungen erweitert, Skalierung groß genug. Sie hat dieselbe Zulässigkeit
    jeder Teilmenge und dieselben Schranken - und dient hier nur als Beleg, dass das
    Aufbrechen gleicher Breiten die Bin-Symmetrie NICHT berührt."""
    pieces = sorted(expand_pieces(instance), reverse=True)
    n = len(pieces)
    shift = n * (n - 1) // 2
    scale = 10**6
    widths = tuple(w * scale + (n - 1 - k) for k, w in enumerate(pieces))
    return CuttingStockInstance(
        roll_width=instance.roll_width * scale + shift,
        item_widths=widths,
        item_demands=tuple(1 for _ in widths),
    )


def test_merging_equivalent_bins_preserves_optimum_and_root_bound_against_dp():
    # Regression: der frühere Vergleich lieferte auf ~1,5 % der Zufallsinstanzen ein anderes
    # Optimum als die Originalinstanz (und verschob die Wurzelschranke). Jetzt: Optimum
    # identisch zur unabhängigen DP-Referenz, Wurzelschranke unverändert, nie mehr Knoten.
    checked = 0
    for n_types in (2, 3, 4):
        for roll_width in (50, 60, 100, 200):
            for max_demand in (1, 2, 3):
                for seed in range(12):
                    instance = generate_instance(n_types, roll_width, max_demand, seed)
                    pieces = expand_pieces(instance)
                    if len(pieces) > 11:
                        continue
                    checked += 1
                    reference = _dp_optimum(pieces, roll_width)
                    normal = solve(instance, weak_bound)
                    merged = solve(instance, weak_bound, skip_equivalent_bins=True)
                    label = (n_types, roll_width, max_demand, seed)
                    assert normal.best_value == reference, label
                    assert merged.best_value == reference, label
                    assert merged.nodes[0].bound == normal.nodes[0].bound, label
                    assert len(merged.nodes) <= len(normal.nodes), label
    assert checked > 200


def test_known_failure_instances_of_the_old_twin_keep_their_optimum():
    # Beispiele, bei denen die alte Zwillingsinstanz ein anderes Optimum lieferte
    # (2 statt 1 bzw. 4 statt 3 Rollen).
    for n_types, roll_width, max_demand, seed, expected in [(2, 60, 3, 11, 1), (4, 50, 2, 1, 3)]:
        instance = generate_instance(n_types, roll_width, max_demand, seed)
        assert _dp_optimum(expand_pieces(instance), roll_width) == expected
        assert solve(instance, weak_bound, skip_equivalent_bins=True).best_value == expected


def test_passungserhaltender_zwilling_hat_identischen_suchbaum():
    # Belegt, warum der Vergleich über verschobene Breiten verworfen wurde: Sobald
    # Passungen und Schranken erhalten bleiben, ist der Baum isomorph (gleiche
    # Knotenzahl) - gleiche Breiten aufzubrechen verändert die Bin-Symmetrie nicht.
    for name in PRESETS:
        instance = generate_instance(**PRESETS[name])
        twin = _width_twin(instance)
        a = solve(instance, weak_bound)
        b = solve(twin, weak_bound)
        assert a.nodes[0].bound == b.nodes[0].bound, name
        assert a.best_value == b.best_value, name
        assert len(a.nodes) == len(b.nodes), name


def test_symmetry_comparison_on_presets_pins_measured_effect():
    # Gemessen: Winzig 5 -> 5 Knoten (kein Effekt), "Spürbare Symmetrie" 218 -> 20,
    # "Größere Instanz" 1338 -> 239.
    results = {}
    for name in PRESETS:
        instance = generate_instance(**PRESETS[name])
        cmp = symmetry_comparison(instance, weak_bound)
        assert cmp["normal_best"] == cmp["desym_best"], name
        assert not cmp["normal_truncated"] and not cmp["desym_truncated"], name
        results[name] = (cmp["normal_nodes"], cmp["desym_nodes"])
    names = list(PRESETS)
    assert results[names[0]][0] == results[names[0]][1]
    assert results[names[1]][0] >= 10 * results[names[1]][1]
    assert results[names[2]][0] >= 4 * results[names[2]][1]


def test_symmetry_comparison_reports_same_optimum_and_never_more_nodes():
    for seed in range(10):
        instance = generate_instance(n_types=3, roll_width=100, max_demand=3, seed=seed)
        cmp = symmetry_comparison(instance, strong_bound)
        assert cmp["normal_best"] == cmp["desym_best"]
        assert cmp["desym_nodes"] <= cmp["normal_nodes"]
