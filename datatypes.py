from enum import Enum
from dataclasses import dataclass
from typing import Tuple, FrozenSet


class TermType(Enum):
    VARIABLE = "variable"
    CONSTANT = "constant"
    FUNCTION = "function"


@dataclass(frozen=True)
class Term:
    type: TermType
    name: str
    args: Tuple['Term', ...] = ()

    def __str__(self):
        if self.args:
            args_str = ", ".join(str(arg) for arg in self.args)
            return f"{self.name}({args_str})"
        return self.name

    def __hash__(self):
        # Хэш вычисляется на основе типа, имени и кортежа аргументов
        return hash((self.type, self.name, self.args))

@dataclass(frozen=True)
class Literal:
    predicate: str
    terms: Tuple[Term, ...]
    negative: bool = False

    def __str__(self):
        sign = "¬" if self.negative else ""
        terms_str = ", ".join(str(term) for term in self.terms)
        return f"{sign}{self.predicate}({terms_str})"

    def negate(self):
        return Literal(self.predicate, self.terms, not self.negative)

    def __hash__(self):
        # Хэш вычисляется на основе предиката, кортежа терминов и отрицания
        return hash((self.predicate, self.terms, self.negative))


@dataclass(frozen=True)
class Clause:
    literals: FrozenSet[Literal]
    parent1: "Clause" = None
    parent2: "Clause" = None

    def __str__(self):
        if len(self.literals) == 0:
            return "□"
        return " ∨ ".join(str(lit) for lit in self.literals)


    def __hash__(self):
        # Хэш зависит только от множества литералов
        return hash(self.literals)

    def __eq__(self, other):
        # Сравнение зависит только от множества литералов
        if not isinstance(other, Clause):
            return False

        if len(self.literals) == 0 and  len(other.literals) == 0:
            return True

        return self.literals == other.literals


# Вспомогательные функции
def var(name: str) -> Term:
    return Term(TermType.VARIABLE, name)


def const(name: str) -> Term:
    return Term(TermType.CONSTANT, name)


def func(name: str, *args: Term) -> Term:
    return Term(TermType.FUNCTION, name, args)


def literal(predicate: str, *terms: Term, negative: bool = False) -> Literal:
    return Literal(predicate, terms, negative)


def clause(*literals: Literal) -> Clause:
    return Clause(frozenset(literals))
