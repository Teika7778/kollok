from datatypes import *
from resolution import resolve
from typing import Set, Optional, Deque
from collections import deque


def sos_resolution(clauses: Set[Clause], target: Clause) -> Optional[Clause]:
    current = clauses.copy()
    current.add(target)
    drived = set()
    changed = True
    while changed:
        for x in current:
            for y in current:
                if x in clauses and y in clauses:
                    continue
                res = resolve(x, y)
                if res is None:
                    continue
                if Clause(frozenset()) in res:
                    for z in res:
                        if z == Clause(frozenset()):
                            return z
                drived.update(res)
        pre = len(current)
        current.update(drived)
        post = len(current)
        changed = (pre != post)
        drived = set()


def unit_preference_resolution(clauses: Set[Clause]) -> Optional[Clause]:
    current = clauses.copy()
    current.add(target)
    drived = set()
    changed = True
    while changed:
        for x in current:
            for y in current:
                if x in clauses and y in clauses:
                    continue
                res = resolve(x, y)
                if res is None:
                    continue
                if Clause(frozenset()) in res:
                    for z in res:
                        if z == Clause(frozenset()):
                            return z
                drived.update(res)
        pre = len(current)
        current.update(drived)
        post = len(current)
        changed = (pre != post)
        drived = set()