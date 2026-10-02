import random

from series import total_correct, total_buggy

SOURCE = [3, 7, 12, 6, 8]
TARGET = total_buggy


# The usual kind of test: We know the expected output.
def test_traditional_unit_test():
    assert TARGET([1, 2, 3]) == 6


# Reordering the input must not change the sum.
# a + b + c = a + c + b = b + c + a = …
def test_mr1_permutation():
    follow_up = SOURCE[:]
    random.shuffle(follow_up)
    assert TARGET(follow_up) == TARGET(SOURCE)


# Adding k to every element adds k * len(L) to the sum.
# k * 3 + (1 + 2 + 3) = (1+k) + (2+k) + (3+k)
def test_mr2_add_constant_to_every_element():
    k = 10
    follow_up = [n + k for n in SOURCE]
    assert TARGET(follow_up) == TARGET(SOURCE) + k * len(SOURCE)


# Appending a zero must not change the sum.
def test_mr3_append_zero():
    follow_up = SOURCE + [0]
    assert TARGET(follow_up) == TARGET(SOURCE)


# Negating every element negates the sum.
def test_mr4_negate_every_element():
    follow_up = [-n for n in SOURCE]
    assert TARGET(follow_up) == -TARGET(SOURCE)


# Concatenating the series with itself doubles the sum.
def test_mr5_duplicate_the_series():
    follow_up = SOURCE + SOURCE
    assert TARGET(follow_up) == 2 * TARGET(SOURCE)
