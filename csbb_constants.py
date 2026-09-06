"""Defaults, slider bounds und Presets für die Cutting-Stock-Branch-&-Bound-Demo."""

DEFAULT_N_TYPES = 4
DEFAULT_MAX_DEMAND = 2
DEFAULT_ROLL_WIDTH = 100
DEFAULT_SEED = 7

N_TYPES_MIN, N_TYPES_MAX = 2, 6
MAX_DEMAND_MIN, MAX_DEMAND_MAX = 1, 4
ROLL_WIDTH_MIN, ROLL_WIDTH_MAX = 50, 200

# Auftragsbreiten werden als Anteil der Rollenbreite gezogen - hält die Instanzen
# unabhängig von der absoluten Rollenbreite vergleichbar.
WIDTH_FRACTION_RANGE = (0.15, 0.6)

# Bin-Packing-Suchbäume explodieren ohne Symmetrie-Mitigation (bewusst keine hier,
# siehe README) schon bei winzigen Instanzen - per Stresstest kalibriert: bei
# n_types=6/max_demand=4 wurden bis zu ~50.000 Knoten beobachtet (0.07s, unkritisch),
# 100.000 lässt reichlich Sicherheitsabstand für die volle Reglerspanne.
MAX_NODES_EXPLORED = 100_000
MAX_NODES_RENDERED = 800

PRESETS = {
    "Winzige Instanz (Baum komplett sichtbar)": {
        "n_types": 3, "roll_width": 100, "max_demand": 1, "seed": 1,
    },
    "Spürbare Symmetrie (mehrere gleich breite Aufträge)": {
        "n_types": 5, "roll_width": 100, "max_demand": 3, "seed": 30,
    },
    "Größere Instanz (der Baum wächst deutlich)": {
        "n_types": 6, "roll_width": 100, "max_demand": 4, "seed": 15,
    },
}
