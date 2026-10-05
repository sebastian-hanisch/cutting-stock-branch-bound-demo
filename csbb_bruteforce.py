"""Erschöpfende Referenzlösung für Bin Packing - unabhängig von der Branch-&-Bound-
Suche, nur für kleine Instanzen praktikabel. Öffnet an jedem Schritt höchstens EIN
neues Bin (statt symmetrisch mehrere identische leere Bins durchzuprobieren) - das
hält die Enumeration bei kleinem n handhabbar, ohne die Korrektheit zu beeinträchtigen.

`max_calls` begrenzt die Zahl der Rekursionsaufrufe (Standard: unbegrenzt, wie in den
Tests); wird sie überschritten, gibt die Funktion `None` zurück statt minutenlang zu
rechnen."""

from csbb_scenario import expand_pieces


class _BudgetExceeded(Exception):
    pass


def solve_bruteforce(instance, max_calls=None):
    pieces = expand_pieces(instance)
    n = len(pieces)
    best = {"count": n}  # triviale obere Schranke: ein Bin pro Stück
    calls = [0]

    def assign(idx, bins):
        calls[0] += 1
        if max_calls is not None and calls[0] > max_calls:
            raise _BudgetExceeded
        if len(bins) >= best["count"]:
            return
        if idx == n:
            best["count"] = min(best["count"], len(bins))
            return
        piece = pieces[idx]
        for i, cap in enumerate(bins):
            if cap >= piece:
                bins[i] -= piece
                assign(idx + 1, bins)
                bins[i] += piece
        bins.append(instance.roll_width - piece)
        assign(idx + 1, bins)
        bins.pop()

    try:
        assign(0, [])
    except _BudgetExceeded:
        return None
    return best["count"]
