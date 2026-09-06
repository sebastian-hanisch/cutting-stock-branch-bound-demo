"""Zwei Schranken für die Bin-Packing-Suche, gemeinsame Signatur
`bound_fn(instance, pieces, depth, bins)` - `bins` ist eine Liste der
Restkapazitäten aller bereits geöffneten Bins. Beide liefern eine gültige
UNTERGRENZE für die INSGESAMT benötigte Bin-Anzahl (bereits geöffnete + mindestens
nötige weitere), nie eine Überschätzung - Voraussetzung dafür, dass Pruning darauf
sicher ist."""


def weak_bound(instance, pieces, depth, bins):
    """L1-Schranke: Restbreite aller noch offenen Stücke, die nicht mehr in die
    Restkapazität bereits geöffneter Bins passt, durch die Rollenbreite geteilt
    (aufgerundet)."""
    remaining_width = sum(pieces[depth:])
    remaining_capacity = sum(bins)
    if remaining_width <= remaining_capacity:
        return len(bins)
    extra = -(-(remaining_width - remaining_capacity) // instance.roll_width)
    return len(bins) + extra


def strong_bound(instance, pieces, depth, bins):
    """Erweitert weak_bound um eine zweite, unabhängig gültige Untergrenze: Stücke
    mit Breite > W/2 können nie zu zweit in einem Bin liegen - jedes braucht ein
    eigenes (kann sich aber mit kleineren Stücken teilen). Nur Bins mit Restkapazität
    > W/2 können überhaupt noch eines aufnehmen; fehlt es an solchen Bins, sind das
    zusätzliche neue Bins, unabhängig von der L1-Schranke. Das Maximum zweier
    gültiger Untergrenzen ist wieder eine gültige (und nie schwächere) Untergrenze.

    Mathematisch korrekt, aber in DIESEM Solver (`csbb_solver.py`) beweisbar ohne
    jeden praktischen Effekt auf die Knotenzahl - siehe
    `tests/test_bounds.py::test_strong_bound_never_changes_node_count_given_descending_order`
    für den Beweis und `app.py`s Formulierungs-Abschnitt für die ausführliche
    Erklärung: bei strikt absteigender Verzweigungsreihenfolge kann ein Stück mit
    Breite > W/2 NIE in ein bereits geöffnetes Bin passen (jedes vorher platzierte
    Stück ist mindestens so breit, lässt also höchstens W/2 Restkapazität übrig) -
    die "existing bin"-Option wird für solche Stücke also nie überhaupt erst
    erzeugt. Die Regel dieser Schranke verhindert exakt das, was die Verzweigung
    strukturell schon unmöglich macht - keine neue Information, kein zusätzliches
    Pruning. Bewusst trotzdem im Code belassen (nicht als toter UI-Umschalter,
    sondern als dokumentierte, getestete Erkenntnis) statt einfach entfernt."""
    base = weak_bound(instance, pieces, depth, bins)
    half = instance.roll_width / 2
    big_count = sum(1 for p in pieces[depth:] if p > half)
    big_capable_open_bins = sum(1 for cap in bins if cap > half)
    big_shortfall = max(0, big_count - big_capable_open_bins)
    return max(base, len(bins) + big_shortfall)
