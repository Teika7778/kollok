from typing import List, Tuple, Optional, Set
from datatypes import Clause, Literal
from unify import unify, Substitution


def find_complementary_literals(clause1: Clause, clause2: Clause) -> List[Tuple[Literal, Literal, Substitution]]:
    complementary_pairs = []

    for lit1 in clause1.literals:
        for lit2 in clause2.literals:
            if (lit1.predicate == lit2.predicate and
                    lit1.negative != lit2.negative):

                substitution = unify(lit1, lit2)
                if substitution is not None:
                    complementary_pairs.append((lit1, lit2, substitution))
                    if len(complementary_pairs) > 1:
                        return complementary_pairs

    return complementary_pairs


def apply_substitution_to_literal(literal: Literal, substitution: Substitution) -> Literal:
    new_terms = tuple(substitution.apply_to_term(term) for term in literal.terms)
    return Literal(literal.predicate, new_terms, literal.negative)


def apply_substitution_to_clause(clause: Clause, substitution: Substitution) -> Clause:
    new_literals = set()
    for literal in clause.literals:
        new_literal = apply_substitution_to_literal(literal, substitution)
        new_literals.add(new_literal)
    return Clause(frozenset(new_literals))


def has_tautology(clause: Clause) -> bool:
    for literal in clause.literals:
        opposite = Literal(literal.predicate, literal.terms, not literal.negative)
        if opposite in clause.literals:
            return True
    return False


def resolve(clause1: Clause, clause2: Clause) -> Set[Clause] | None:
    complementary_pairs = find_complementary_literals(clause1, clause2)

    # Если нет пар или больше одной пары - возвращаем None
    if len(complementary_pairs) == 0:
        return None

    toRet = set()
    for lit1, lit2, substitution in complementary_pairs:

        lit1_applied = apply_substitution_to_literal(lit1, substitution)
        lit2_applied = apply_substitution_to_literal(lit2, substitution)

        clause1_applied = apply_substitution_to_clause(clause1, substitution)
        clause2_applied = apply_substitution_to_clause(clause2, substitution)

        new_literals = set()

        for literal in clause1_applied.literals:
            if literal != lit1_applied:
                new_literals.add(literal)

        for literal in clause2_applied.literals:
            if literal != lit2_applied:
                new_literals.add(literal)

        if not new_literals:
            toRet.add(Clause(frozenset(), parent1=clause1, parent2=clause2))

        candidate = Clause(frozenset(new_literals), parent1=clause1, parent2=clause2)

        if has_tautology(candidate):
            continue

        toRet.add(candidate)

    if len(toRet) == 0:
        return None
    else:
        return toRet
