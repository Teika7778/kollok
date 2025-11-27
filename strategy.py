from datatypes import *
from resolution import resolve
from typing import Set, Optional
from collections import deque


def sos_resolution(clauses: Set[Clause], target: Clause) -> Optional[Clause]:
    initial_clauses = clauses.copy()
    support_set = {target}
    all_clauses = initial_clauses | support_set

    queue = deque(support_set)
    processed = set()

    while queue:
        current_clause = queue.popleft()

        if current_clause in processed:
            continue

        processed.add(current_clause)

        clauses_to_check = list(all_clauses)

        for other_clause in clauses_to_check:
            if other_clause == current_clause:
                continue

            resolvents = resolve(current_clause, other_clause)
            if resolvents is None:
                continue

            for resolvent in resolvents:
                if resolvent == Clause(frozenset()):
                    return resolvent

                if resolvent not in all_clauses:
                    all_clauses.add(resolvent)
                    queue.append(resolvent)

    return None
