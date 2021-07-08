#!/bin/env python
"""A file which contains only what is strictly necessary for completion of the is_even function"""

# Y combinator, used for recursion
Y = lambda f: (lambda x: x(x))(lambda y: f(lambda a: y(y)(a)))

# Church arithmetic
succ = lambda n: lambda f: lambda x: f(n(f)(x))
pred = lambda n: lambda f: lambda x: n(lambda g: lambda h: h(g(f)))(lambda _: x)(lambda u: u)
minus = lambda m: lambda n: n(pred)(m)

zero = lambda f: lambda x: x
one = succ(zero)

# abs because we don't care about sign, only about magnitude
to_church_num = Y(lambda f: lambda n: zero if n == 0 else succ(f(abs(n) - 1)))
from_church_num = lambda n: n(lambda x: x + 1)(0)

# Church booleans
# Making both true and false eval version for consistency
true = lambda t: lambda f: t()
false = lambda t: lambda f: f()
if_ = lambda p: lambda a: lambda b: p(a)(b)

# Church comparisons
is_zero = lambda n: n(lambda _: false)(true)
leq = lambda m: lambda n: is_zero(minus(m)(n))

to_church_bool = lambda p: true if p else false
from_church_bool = lambda p: p(lambda: True)(lambda: False)

# the working part of the function
is_even_body = Y(lambda f: lambda n: if_(leq(n)(one))(lambda: is_zero(n))(lambda: f(pred(pred(n)))))

# the full is_even function
is_even = lambda n: from_church_bool(is_even_body(to_church_num(n)))
