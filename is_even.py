"""Some lambda calculus, building to is_even"""

succ  = lambda n: lambda f: lambda x: f(n(f)(x))
pred  = lambda n: lambda f: lambda x: n(lambda g: lambda h: h(g(f)))(lambda _: x)(lambda u: u)
minus = lambda m: lambda n: n(pred)(m)

zero  = lambda f: lambda x: x
one   = succ(zero)

Y = lambda f: (lambda x: x(x))(lambda y: f(lambda a: y(y)(a)))

from_church_num = lambda n: n(lambda x: x + 1)(0)
to_church_num = Y(lambda f: lambda n: zero if n == 0 else succ(f(n - 1)))

from_church_bool = lambda p: p(True)(False)
to_church_bool = lambda p: true if p else false

true  = lambda t: lambda f: t
false = lambda t: lambda f: f

and_ = lambda p: lambda q: p(q)(p)
if_  = lambda p: lambda a: lambda b: p(a)(b)

is_zero = lambda n: n(lambda _: false)(true)
leq     = lambda m: lambda n: is_zero(minus(m)(n))

# is_even(zero) = Y(\f n -> if_(leq(n)(one))(is_zero(n))(f(pred(pred(n)))))
# -> true(is_zero(n))(b)
# -> (\t f -> t)(\t f -> t)(b)
# -> (\t f -> t) -> true
# So we don't have to worry about is_zero resulting in b, because b is consumed by leq(n)(one).
# The problem is that pred(n) doesn't bottom, and that f(pred(pred(n))) is eagerly evaluated:
# pred(one) -> zero
# pred(zero) -> zero
#
# Solution: We need to make if_(a)(b) to have b lazily evaluated.
#
# Attempt one: if_(a)(lambda: b)
# Problem with attempt one: results in heavily nested lambdas:
# lazy_is_even(ten) -> f()()()()() -> church_bool
# So, we need to have b lazily evaluated without nesting.
#
# Attempt two: eval lazy false
# true = \t f -> t
# eval_false = \t f -> f()
# eval_is_zero = lambda n: n(lambda: eval_false)(true)
# eval_leq = lambda m: lambda n: eval_is_zero(minus(m)(n))
# eval_is_even = Y(lambda f: lambda n: if_(eval_leq(n)(one))(is_zero(n))(lambda: f(pred(pred(n)))))
# SUCCESS
eval_false = lambda t: lambda f: f()
eval_is_zero = lambda n: n(lambda _: eval_false)(true)
eval_leq = lambda m: lambda n: eval_is_zero(minus(m)(n))
eval_is_even = Y(lambda f: lambda n: if_(eval_leq(n)(one))(is_zero(n))(lambda: f(pred(pred(n)))))

# whole thing in one lambda
# takes in an int and spits out a bool (neither church encoded
# is_even = lambda n: from_church_bool(Y(lambda f: lambda n: if_(eval_leq(n)(one))(is_zero(n))(lambda: f(pred(pred(n)))))(to_church_num(n)))
# = lambda n: Y(...)(to_church_num(n))(True)(False)
# = lambda n: Y(...)(Y(lambda f: lambda n: zero if n == 0 else succ(f(n - 1)))(n))(True)(False)
# = lambda n: Y(...)(Y(lambda f: lambda n: zero if n == 0 else (lambda n: lambda f: lambda x: f(n(f)(x)))(f(n - 1)))(n))(True)(False)
# = lambda n: (lambda f: (lambda x: x(x))(lambda y: f(lambda a: y(y)(a))))(...)((lambda f: (lambda x: x(x))(lambda y: f(lambda a: y(y)(a))))(lambda f: lambda n: zero if n == 0 else (lambda n: lambda f: lambda x: f(n(f)(x)))(f(n - 1)))(n))(True)(False)
# = lambda n: (lambda f: (lambda x: x(x))(lambda y: f(lambda a: y(y)(a))))(...)((lambda f: (lambda x: x(x))(lambda y: f(lambda a: y(y)(a))))(lambda f: lambda n: (lambda f: lambda x: x) if n == 0 else (lambda n: lambda f: lambda x: f(n(f)(x)))(f(n - 1)))(n))(True)(False)
#
# (...) = lambda f: lambda n: if_(eval_leq(n)(one))(is_zero(n))(lambda: f(pred(pred(n))))
# = lambda f: lambda n: (lambda p: lambda a: lambda b: p(a)(b))(eval_leq(n)(one))(is_zero(n))(lambda: f(pred(pred(n))))
# = lambda f: lambda n: (lambda p: lambda a: lambda b: p(a)(b))((lambda m: lambda n: eval_is_zero(minus(m)(n)))(n)(one))(is_zero(n))(lambda: f(pred(pred(n))))
# = lambda f: lambda n: (lambda p: lambda a: lambda b: p(a)(b))((lambda m: lambda n: (lambda n: n(lambda _: (lambda t: lambda f: f()))(true))(minus(m)(n)))(n)(one))(is_zero(n))(lambda: f(pred(pred(n))))
# = lambda f: lambda n: (lambda p: lambda a: lambda b: p(a)(b))((lambda m: lambda n: (lambda n: n(lambda _: (lambda t: lambda f: f()))((lambda t: lambda f: t)))(minus(m)(n)))(n)(one))(is_zero(n))(lambda: f(pred(pred(n))))
# = lambda f: lambda n: (lambda p: lambda a: lambda b: p(a)(b))((lambda m: lambda n: (lambda n: n(lambda _: (lambda t: lambda f: f()))((lambda t: lambda f: t)))((lambda m: lambda n: n(pred)(m))(m)(n)))(n)(one))(is_zero(n))(lambda: f(pred(pred(n))))
# = lambda f: lambda n: (lambda p: lambda a: lambda b: p(a)(b))((lambda m: lambda n: (lambda n: n(lambda _: (lambda t: lambda f: f()))((lambda t: lambda f: t)))((lambda m: lambda n: n(pred)(m))(m)(n)))(n)(lambda f: lambda x: f(x)))(is_zero(n))(lambda: f(pred(pred(n))))
# = lambda f: lambda n: (lambda p: lambda a: lambda b: p(a)(b))((lambda m: lambda n: (lambda n: n(lambda _: (lambda t: lambda f: f()))((lambda t: lambda f: t)))((lambda m: lambda n: n(lambda n: lambda f: lambda x: n(lambda g: lambda h: h(g(f)))(lambda _: x)(lambda u: u))(m))(m)(n)))(n)(lambda f: lambda x: f(x)))(is_zero(n))(lambda: f((lambda n: lambda f: lambda x: n(lambda g: lambda h: h(g(f)))(lambda _: x)(lambda u: u))((lambda n: lambda f: lambda x: n(lambda g: lambda h: h(g(f)))(lambda _: x)(lambda u: u))(n))))
# = lambda f: lambda n: (lambda p: lambda a: lambda b: p(a)(b))((lambda m: lambda n: (lambda n: n(lambda _: (lambda t: lambda f: f()))((lambda t: lambda f: t)))((lambda m: lambda n: n(lambda n: lambda f: lambda x: n(lambda g: lambda h: h(g(f)))(lambda _: x)(lambda u: u))(m))(m)(n)))(n)(lambda f: lambda x: f(x)))((lambda n: n(lambda _: false)(true))(n))(lambda: f((lambda n: lambda f: lambda x: n(lambda g: lambda h: h(g(f)))(lambda _: x)(lambda u: u))((lambda n: lambda f: lambda x: n(lambda g: lambda h: h(g(f)))(lambda _: x)(lambda u: u))(n))))

is_even = lambda n: (lambda f: (lambda x: x(x))(lambda y: f(lambda a: y(y)(a))))(lambda f: lambda n: (lambda p: lambda a: lambda b: p(a)(b))((lambda m: lambda n: (lambda n: n(lambda _: (lambda t: lambda f: f()))((lambda t: lambda f: t)))((lambda m: lambda n: n(lambda n: lambda f: lambda x: n(lambda g: lambda h: h(g(f)))(lambda _: x)(lambda u: u))(m))(m)(n)))(n)(lambda f: lambda x: f(x)))((lambda n: n(lambda _: false)(true))(n))(lambda: f((lambda n: lambda f: lambda x: n(lambda g: lambda h: h(g(f)))(lambda _: x)(lambda u: u))((lambda n: lambda f: lambda x: n(lambda g: lambda h: h(g(f)))(lambda _: x)(lambda u: u))(n)))))((lambda f: (lambda x: x(x))(lambda y: f(lambda a: y(y)(a))))(lambda f: lambda n: (lambda f: lambda x: x) if n == 0 else (lambda n: lambda f: lambda x: f(n(f)(x)))(f(abs(n) - 1)))(n))(True)(False)
