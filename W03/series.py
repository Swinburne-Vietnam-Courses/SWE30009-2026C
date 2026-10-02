"""
Program Under Test: Sum of a series of integers.

Two implementations are provided.
You can run the same metamorphic relations against both.
"""


# A correct implementation.
def total_correct(numbers):
    result = 0
    for n in numbers:
        result += n
    return result


# A faulty implementation.
def total_buggy(numbers):
    """
    Someone used a set "for efficiency" and silently dropped duplicates.
    Note that total_buggy([1, 2, 3]) still returns 6,
    so the obvious unit test passes,
    and there is no branch at all,
    so statement and branch coverage both reach 100%.
    """
    return sum(set(numbers))
