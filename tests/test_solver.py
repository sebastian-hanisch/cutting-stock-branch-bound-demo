import pytest

from csbb_bounds import strong_bound, weak_bound
from csbb_bruteforce import solve_bruteforce
from csbb_constants import PRESETS
from csbb_scenario import CuttingStockInstance, expand_pieces, generate_instance
from csbb_solver import solve


def _check_solution_feasible(instance, result):
    pieces = expand_pieces(instance)
    assert sum(instance.roll_width - cap for cap in result.best_bins) == sum(pieces)
    for cap in result.best_bins:
        assert 0 <= cap <= instance.roll_width


def test_matches_hand_computed_example():
    instance = CuttingStockInstance(roll_width=10, item_widths=(6,), item_demands=(3,))
    result = solve(instance, strong_bound)
    assert result.best_value == 3
    true_min = solve_bruteforce(instance)
    assert true_min == 3


@pytest.mark.parametrize("bound_fn", [weak_bound, strong_bound])
def test_matches_bruteforce_across_random_small_instances(bound_fn):
    for seed in range(20):
        instance = generate_instance(n_types=3, roll_width=100, max_demand=2, seed=seed)
        result = solve(instance, bound_fn)
        true_min = solve_bruteforce(instance)
        assert result.best_value == true_min, f"seed={seed}"
        _check_solution_feasible(instance, result)


def test_strong_bound_never_changes_node_count_given_descending_order():
    # Nicht nur "nie schlechter", sondern PROVABLY identisch: bei strikt
    # absteigender Verzweigungsreihenfolge kann ein Stück mit Breite > W/2 nie in
    # ein bereits geöffnetes Bin passen (jedes vorher platzierte Stück ist
    # mindestens so breit, lässt also höchstens W/2 Restkapazität übrig) - die
    # "existing bin"-Option für solche Stücke wird strukturell nie erzeugt, die
    # zusätzliche Information der starken Schranke kommt also nie zum Tragen. Ein
    # überraschender Fund beim Kalibrieren (breite Sweeps + gezielt konstruierte
    # Gegenbeispiele fanden ausnahmslos identische Knotenzahlen), siehe
    # csbb_bounds.strong_bound's Docstring für den vollständigen Beweis.
    for seed in range(30):
        instance = generate_instance(
            n_types=6, roll_width=100, max_demand=4, seed=seed
        )
        weak_result = solve(instance, weak_bound, max_nodes=100_000)
        strong_result = solve(instance, strong_bound, max_nodes=100_000)
        if weak_result.truncated or strong_result.truncated:
            continue
        assert weak_result.best_value == strong_result.best_value, f"seed={seed}"
        assert len(strong_result.nodes) == len(weak_result.nodes), f"seed={seed}"


def test_max_nodes_cap_is_honored_and_flagged_as_truncated():
    instance = generate_instance(n_types=6, roll_width=100, max_demand=4, seed=1)
    result = solve(instance, weak_bound, max_nodes=30)
    assert len(result.nodes) <= 30 + 30  # Sicherheitsmarge für den letzten unvollständigen Options-Batch
    assert result.truncated


@pytest.mark.parametrize("name", list(PRESETS.keys()))
def test_presets_solve_correctly(name):
    instance = generate_instance(**PRESETS[name])
    result = solve(instance, strong_bound)
    true_min = solve_bruteforce(instance)
    assert result.best_value == true_min, name
