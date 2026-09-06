"""Kennzahlen aus einem Suchlauf, plus der "Was kostet Symmetrie wirklich?"-
Vergleich: dieselbe Instanz einmal normal, einmal mit künstlich aufgebrochener
Symmetrie (siehe csbb_scenario.desymmetrized_instance) gelöst."""

from collections import Counter

from csbb_constants import MAX_NODES_EXPLORED
from csbb_scenario import desymmetrized_instance
from csbb_solver import solve


def compute_stats(result):
    counts = Counter(node.status for node in result.nodes)
    return {
        "nodes_explored": len(result.nodes),
        "pruned_bound": counts["prune_bound"],
        "leaves_evaluated": counts["leaf_new_best"] + counts["leaf_not_best"],
        "best_value": result.best_value,
        "truncated": result.truncated,
    }


def stats_up_to_step(result, step):
    counts = Counter(node.status for node in result.nodes if node.id <= step)
    current_best = None
    for nid, v in result.incumbent_history:
        if nid <= step:
            current_best = v
    return {
        "nodes_so_far": counts.total(),
        "pruned_bound": counts["prune_bound"],
        "current_best": current_best,
    }


def symmetry_comparison(instance, bound_fn, max_nodes=MAX_NODES_EXPLORED):
    normal_result = solve(instance, bound_fn, max_nodes=max_nodes)
    desym_instance = desymmetrized_instance(instance)
    desym_result = solve(desym_instance, bound_fn, max_nodes=max_nodes)
    return {
        "normal_nodes": len(normal_result.nodes),
        "normal_best": normal_result.best_value,
        "normal_truncated": normal_result.truncated,
        "desym_nodes": len(desym_result.nodes),
        "desym_best": desym_result.best_value,
        "desym_truncated": desym_result.truncated,
    }
