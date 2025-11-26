from typing import Dict, Optional

from datatypes import *


class Substitution:

    def __init__(self, mapping: Dict[Term, Term] = None):
        # Подстановка это отображений множества термов на себя же
        self._mapping = mapping if mapping is not None else {}
        # Для применения подстановки
        self._cache: Dict[Term, Term] = {}

    def apply_to_term(self, term: Term) -> Term:
        if term in self._cache:
            return self._cache[term]

        result = self._apply_to_term_uncached(term)
        # добавляем ответ, но это не должно много весить
        self._cache[term] = result
        return result

    def _apply_to_term_uncached(self, term: Term) -> Term:

        # Если терм - переменная и есть подстановка
        if term.type == TermType.VARIABLE and term in self._mapping:
            return self.apply_to_term(self._mapping[term])

        # Если терм - функция, рекурсивно применяем к аргументам
        if term.type == TermType.FUNCTION and term.args:
            new_args = tuple(self.apply_to_term(arg) for arg in term.args)
            return Term(term.type, term.name, new_args)

        return term

    def add_binding(self, variable: Term, value: Term) -> None:
        # Обертка с очисткой
        if variable.type != TermType.VARIABLE:
            raise ValueError("Can only bind variables")

        self._mapping[variable] = value
        self._cache.clear()

    def get_binding(self, variable: Term) -> Optional[Term]:
        return self._mapping.get(variable)  # Обертка

    def contains(self, variable: Term) -> bool:
        return variable in self._mapping

    def __len__(self):
        return len(self._mapping)

    def __contains__(self, variable):
        return variable in self._mapping

    def copy(self) -> 'Substitution':
        return Substitution(self._mapping.copy())

    def __str__(self):
        return "Substitution(" + ", ".join(f"{k} -> {v}" for k, v in self._mapping.items()) + ")"


def occurs_check(variable: Term, term: Term, subst: Substitution) -> bool:
    # Входил ли переменная var в терм term
    # поиск в ширину
    stack = [term]
    visited = set()

    while stack:
        current = stack.pop()

        if id(current) in visited:
            continue
        visited.add(id(current))

        if subst.apply_to_term(current) == variable:
            return True

        if current.type == TermType.FUNCTION:
            stack.extend(current.args)

    return False


def unify_terms(t1: Term, t2: Term, subst: Substitution) -> bool:
    t1_applied = subst.apply_to_term(t1)
    t2_applied = subst.apply_to_term(t2)

    # СРАВНЕНИЕ ВСЕХ ПОЛЕЙ
    if t1_applied == t2_applied:
        return True

    """
    Если имеем переменную или две переменные то корректную работу обеспечивают случаи A, B.
    Если имеем две функции, то случай С покрывает его
    Если имеем две константы, то они либо базовго равны, либо унификация невозможна
    Если имеем функцию и константу, то унификация тоже невозможна заведомо
    """
    # A
    if t1_applied.type == TermType.VARIABLE:
        # избегаем попытки унифицировать f(x) = x
        if occurs_check(t1_applied, t2_applied, subst):
            return False
        subst.add_binding(t1_applied, t2_applied)
        return True
    # B
    if t2_applied.type == TermType.VARIABLE:
        if occurs_check(t2_applied, t1_applied, subst):
            return False
        subst.add_binding(t2_applied, t1_applied)
        return True

    # С
    if (t1_applied.type == TermType.FUNCTION and
            t2_applied.type == TermType.FUNCTION):

        # Проверка сигнатуры
        if (t1_applied.name != t2_applied.name or
                len(t1_applied.args) != len(t2_applied.args)):
            return False

        # Рекурсивно унифицируем аргументы
        for arg1, arg2 in zip(t1_applied.args, t2_applied.args):
            if not unify_terms(arg1, arg2, subst):
                return False
        return True

    # D
    return False


def unify(L1: Literal, L2: Literal) -> Optional[Substitution]:
    if L1.predicate != L2.predicate or len(L1.terms) != len(L2.terms):
        return None

    # Создаем одну подстановку для всего процесса
    subst = Substitution()

    # Унифицируем термины попарно
    for term1, term2 in zip(L1.terms, L2.terms):
        if not unify_terms(term1, term2, subst):
            return None

    return subst
