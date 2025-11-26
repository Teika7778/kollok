

from datatypes import func, var, const, literal
from strategy import unit_preference_resolution, sos_resolution
from datatypes import clause, negate


def sokrat():
    x = var("x")
    mortal = lambda t: literal("Mortal", t)
    human = lambda t: literal("Human", t)
    s = const("Sokrat")
    # human -> mortal
    p1 = clause(mortal(x), negate(human(x)))
    p2 = clause(human(s))
    T = clause(negate(mortal(s)))
    res = sos_resolution({p1, p2}, T)
    print(res)

if __name__ == "__main__":
    sokrat()
