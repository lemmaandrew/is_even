"""Translates is_even_src.py into a one-liner"""

import re
from pathlib import Path
from typing import Dict


def basic_definitions(filepath: str) -> Dict[str, str]:
    """Builds a dictionary of definitions from a file.
    Does not reduce definitions to lambdas, only stoes them as they are defined
    """
    definitions = dict()
    with open(filepath) as file:
        for line in file:
            res = re.search(r"^([a-zA-Z_]\w*) *= *(.+)$", line.strip())
            if res is not None:
                definitions[res[1]] = res[2]
    return definitions


def reduce_definitions(basic_defs: Dict[str, str]) -> Dict[str, str]:
    """Reduces definitions to lambda expressions
    Does not work if two names are defined by each other
    """
    reduced_defs = basic_defs.copy()
    names = list(reduced_defs.keys())
    only_lambdas = False
    while not only_lambdas:
        only_lambdas = True
        for name1 in names:
            old_def = reduced_defs[name1]
            new_def = old_def
            for name2 in names:
                # replacing function calls
                # lambda expressions need to be wrapped parentheses
                # but named functioned do not
                definition = reduced_defs[name2]
                if definition.startswith("lambda "):
                    new_def = re.sub(rf"\b{name2}\(", f"({definition})(", new_def)
                else:
                    new_def = re.sub(rf"\b{name2}\(", f"{definition}(", new_def)
                # replacing statements (not calls)
                # statements such as `func(true)` don't need parens because otherwise
                # the result would be `func((lambda t: lambda f: t()))`,
                # which has a redundant set of parens
                # but statments such as `zero if x == 0 else ...` do because otherwise
                # the result would be `lambda f: lambda x: x if x == 0 else ...`,
                # which doesn't parse properly
                new_def = re.sub(rf"\({name2}\)", f"({definition})", new_def)
                new_def = re.sub(rf"\b{name2}\b", f"({definition})", new_def)
                if new_def != old_def:
                    only_lambdas = False
                reduced_defs[name1] = new_def
    return reduced_defs


def main() -> None:
    """Translates src/is_even_src.py and prints it to STDOUT"""
    parent_dir = Path(__file__).parent
    src_path = parent_dir / "is_even_src.py"
    basic = basic_definitions(src_path)
    reduced = reduce_definitions(basic)
    print(reduced["is_even"])


if __name__ == "__main__":
    main()
