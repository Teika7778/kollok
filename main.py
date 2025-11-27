from datatypes import func, var, const, literal
from strategy import sos_resolution
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


def guilt():
    A = const("A")
    B = const("B")
    C = const("C")
    D = const("D")

    guilty = lambda t: literal("Виновен", t)
    nguilty = lambda t: negate(guilty(t))

    p1 = clause(nguilty(A), nguilty(B), guilty(C))
    p2 = clause(nguilty(A), guilty(B), guilty(C))
    p3 = clause(nguilty(C), guilty(D))
    p4 = clause(guilty(A), guilty(D))

    T = clause(nguilty(D))

    res = sos_resolution({p1, p2, p3, p4}, T)
    print(res)

def ex():
    x = var("x")
    y = var("y")
    a = const("a")

    E = lambda t: literal("E", t)
    nE = lambda t: literal("E", t, negative=True)

    V = lambda t: literal("V", t)
    nV = lambda t: literal("V", t, negative=True)

    C = lambda t: literal("C", t)
    nC = lambda t: literal("C", t, negative=True)

    S = lambda t, u: literal("S", t, u)
    nS = lambda t, u: literal("S", t, u, negative=True)

    P = lambda t: literal("S", t)
    nP = lambda t: literal("S", t, negative=True)

    f = lambda t: func("f", t)
    g = lambda t: func("g", t)

    D1 = clause(E(x), V(y), C(f(x)))
    D2 = clause(E(x), S(x, f(x)))
    D3 = clause(nE(a))
    D4 = clause(P(a))
    D5 = clause(P(f(x)), nS(y, x))
    D6 = clause(nP(x), nV(g(x)), nV(y))
    D7 = clause(nP(x), nC(y))

    D = {D1, D2, D3, D4, D5, D6, D7}
    D.remove(D3)

    res = sos_resolution(D, D3)

    print(res)

if __name__ == "__main__":
    ex()
