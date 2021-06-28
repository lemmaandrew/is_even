# is_even

Finds whether an integer is even

---

We start with some pretty standard Church encoding for numbers:

    succ = lambda n: lambda f: lambda x: f(n(f)(x))
    pred = lambda n: lambda f: lambda x: n(lambda g: lambda h: h(g(f)))(lambda _: x)(lambda u: u)
    # we don't need plus for this so we don't define it
    minus = lambda m: lambda n: n(pred)(m)
    
    # the only two numbers we need
    zero = lambda f: lambda x: x
    one = succ(zero)

Next, we need to be able to convert an int to a Church-encoded number:

    # Y combinator, because we aren't allowed to do recursion
    Y = lambda f: (lambda x: x(x))(lambda y: f(lambda a: y(y)(a)))
    
    # conversion to a church number
    # we use abs(n) because we don't care about the sign, just if it's even
    # this is the first deviation from canonical Church encoding
    to_church_num = Y(lambda f: lambda n: zero if n == 0 else succ(f(abs(n) - 1)))

Next, we have our Church booleans and Church logic. There is a major deviation from canonical encoding here:

    true = lambda t: lambda f: t
    false = lambda t: lambda f: f
    from_church_bool = lambda p: p(True)(False)
    if_ = lambda p: p(a)(b)
    
    # this is our major deviation, and I'll explain its reasoning later
    # in short, we need it to be like this for lazy evaluation
    eval_false = lambda t: lambda f: f()
    
    # two types of is_zero, one for canon, and one for eval_false
    is_zero = lambda n: n(lambda _: false)(true)
    eval_is_zero = lambda n: n(lambda _: eval_false)(true)
    
    # only need `eval less than or equal to` for our purposes
    eval_leq = lambda m: lambda n: eval_is_zero(minus(m)(n))
    
    # this is the working body of the `is_even` (we'll call it `ie_body`)
    ie_body = Y(lambda f: lambda n: if_(eval_leq(n)(one))(is_zero(n))(lambda: f(pred(pred(n)))))

Notice that `f(pred(pred(n)))` is hidden behind a parameterless lambda. This makes the expression lazily evaluated.
This is necessary because all of the `if_` expression is evaluated unlike a regular if-else Python expression, which is already lazy.
This means that, even if `n <= 1`, `f(pred(pred(n)))` will be evaluated. *This is a major problem*, because `pred(n)` never bottoms.

That is,

    pred(one) == zero
    pred(zero) == zero

So, the Y combinator, which tries to find a bottom of an expression, never will. Instead, it will forever do `pred(pred(n))`.
The solution to this is to make the expression lazy, but if were to use the canonical false, then we would end up with the result:

    ie_body(to_church_num(10)) -> lambda: lambda: lambda: lambda: lambda: is_zero(zero)

To avoid this nesting, we need `eval_false` to evaluate the lambda if `n > 1`

Finally, we wrap `ie_body` in a function to convert an int, then to evaluate a Church boolean:

    is_even = lambda n: from_church_bool(ie_body(to_church_num(n)))

Decomposing this, we get the abomination of a one liner.
