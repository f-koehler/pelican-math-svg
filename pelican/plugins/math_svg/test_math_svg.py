from . import math_svg


def test_regex_inline():
    m = math_svg.regex_inline.match("$$x^2$$")

    assert m
    assert m.group(1) == "x^2"
