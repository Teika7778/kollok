

from datatypes import func, var, const, literal
from strategy import unit_preference_resolution, sos_resolution



def test_group_commutativity():
    """
    Жесткий тест: доказательство коммутативности группы, где каждый элемент является своим обратным.
    Аксиомы группы + x*x = e => группа коммутативна (x*y = y*x)
    """
    # Константы и переменные
    e = const("e")
    a = const("a")
    b = const("b")
    x = var("x")
    y = var("y")
    z = var("z")



    # Функции: умножение и обратный элемент
    def mul(t1, t2):
        return func("mul", t1, t2)

    def inv(t):
        return func("inv", t)

    # Аксиомы группы
    # Ассоциативность: (x*y)*z = x*(y*z)
    from datatypes import clause
    associativity = clause(literal("Eq", mul(mul(x, y), z), mul(x, mul(y, z))))

    # Единичный элемент слева: e*x = x
    identity_left = clause(
        literal("Eq", mul(e, x), x)
    )

    # Единичный элемент справа: x*e = x
    identity_right = clause(
        literal("Eq", mul(x, e), x)
    )

    # Обратный элемент слева: inv(x)*x = e
    inverse_left = clause(
        literal("Eq", mul(inv(x), x), e)
    )

    # Обратный элемент справа: x*inv(x) = e
    inverse_right = clause(
        literal("Eq", mul(x, inv(x)), e)
    )

    # Дополнительное условие: x*x = e
    square_e = clause(
        literal("Eq", mul(x, x), e)
    )

    # Аксиомы равенства
    # Рефлексивность
    refl = clause(literal("Eq", x, x))

    # Симметричность: x=y => y=x
    sym = clause(
        literal("Eq", x, y, negative=True),
        literal("Eq", y, x)
    )

    # Транзитивность: x=y & y=z => x=z
    trans = clause(
        literal("Eq", x, y, negative=True),
        literal("Eq", y, z, negative=True),
        literal("Eq", x, z)
    )

    # Конгруэнтность для умножения (слева): x=y => x*z = y*z
    cong_mul_left = clause(
        literal("Eq", x, y, negative=True),
        literal("Eq", mul(x, z), mul(y, z))
    )

    # Конгруэнтность для умножения (справа): x=y => z*x = z*y
    cong_mul_right = clause(
        literal("Eq", x, y, negative=True),
        literal("Eq", mul(z, x), mul(z, y))
    )

    # Конгруэнтность для обратного: x=y => inv(x)=inv(y)
    cong_inv = clause(
        literal("Eq", x, y, negative=True),
        literal("Eq", inv(x), inv(y))
    )

    # Лемма: inv(x) = x (следует из x*x = e и единственности обратного)
    # Формально: ¬Eq(mul(x,y),e) ∨ ¬Eq(mul(x,z),e) ∨ Eq(y,z)
    uniqueness = clause(
        literal("Eq", mul(x, y), e, negative=True),
        literal("Eq", mul(x, z), e, negative=True),
        literal("Eq", y, z)
    )

    # Лемма: inv(x*y) = inv(y)*inv(x) (свойство обращения произведения)
    inv_product = clause(
        literal("Eq", inv(mul(x, y)), mul(inv(y), inv(x)))
    )

    # Отрицание цели: a*b != b*a
    goal_negation = clause(
        literal("Eq", mul(a, b), mul(b, a), negative=True)
    )

    # Все клаузы
    clauses = {
        associativity,
        identity_left, identity_right,
        inverse_left, inverse_right,
        square_e,
        refl, sym, trans,
        cong_mul_left, cong_mul_right, cong_inv,
        uniqueness,
        inv_product
    }

    print("Начальные клаузы:")
    for i, clause in enumerate(clauses, 1):
        print(f"{i:2}. {clause}")

    # Запускаем стратегию
    result = sos_resolution(clauses, goal_negation)

    # Проверяем результат
    if result is not None and len(result.literals) == 0:
        print("✓ Противоречие найдено! Коммутативность доказана.")
        return True
    else:
        print("✗ Противоречие не найдено")
        return False


if __name__ == "__main__":
    test_group_commutativity()
