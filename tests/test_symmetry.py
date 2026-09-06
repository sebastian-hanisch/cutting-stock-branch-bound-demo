from csbb_bounds import strong_bound
from csbb_evaluation import symmetry_comparison
from csbb_scenario import desymmetrized_instance, generate_instance
from csbb_solver import solve


def test_desymmetrized_instance_preserves_optimal_bin_count():
    for seed in range(10):
        instance = generate_instance(n_types=3, roll_width=100, max_demand=2, seed=seed)
        normal = solve(instance, strong_bound)
        desym = solve(desymmetrized_instance(instance), strong_bound)
        assert normal.best_value == desym.best_value, f"seed={seed}"


def test_symmetry_comparison_reports_fewer_or_equal_nodes_after_desymmetrizing():
    # Nicht garantiert IMMER weniger (bei winzigen Instanzen kann der Unterschied
    # verschwinden), aber über mehrere Seeds sollte die entsymmetrisierte Variante
    # im Schnitt klar weniger Knoten brauchen - der Kern der "Was kostet Symmetrie
    # wirklich?"-Aussage in der App.
    total_normal, total_desym = 0, 0
    for seed in range(10):
        instance = generate_instance(n_types=3, roll_width=100, max_demand=3, seed=seed)
        cmp = symmetry_comparison(instance, strong_bound)
        assert cmp["normal_best"] == cmp["desym_best"]
        total_normal += cmp["normal_nodes"]
        total_desym += cmp["desym_nodes"]
    assert total_desym <= total_normal
