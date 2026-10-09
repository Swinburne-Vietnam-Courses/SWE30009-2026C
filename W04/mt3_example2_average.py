"""
Metamorphic testing demo for MT III, Example 2: The average of a series of integers.

Same input as Example 1 but a different program, so each MR is either common with or similar
to an MR of Example 1. The script checks them against one correct program and two faulty versions.
"""

import math
from dataclasses import dataclass

K_ADD = 10  # The k in the "add k" MRs.
K_MULTIPLY = 3  # The k in the "multiply by k" MR.
SECOND_SOURCE_INPUT = [4, -2, 9]  # SI-2 for the concatenation MR.

# Five source inputs, so every MR gets five metamorphic groups. The first one is the lecture example.
SOURCE_INPUTS = [
    [3, 7, 12, 6, 8],
    [5, -2, 9],
    [0, 4, 4, 1, 10, 2],
    [-7, 3],
    [11, 0, -5, 6],
]


# Programs under test. The first one is correct, the other two contain one fault each.


def average_correct(numbers):
    total = 0
    for number in numbers:
        total += number
    return total / len(numbers)


# Fault: // drops the fractional part of the average.
def average_integer_division(numbers):
    total = 0
    for number in numbers:
        total += number
    return total // len(numbers)


# Fault: the loop stops one element too early but still divides by the full length.
def average_skips_last(numbers):
    total = 0
    for index in range(len(numbers) - 1):
        total += numbers[index]
    return total / len(numbers)


PROGRAMS = [average_correct, average_integer_division, average_skips_last]


# Averages are floats, so compare them with a small tolerance instead of ==.
def same(a, b):
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)


# The result of checking one MR on one metamorphic group.
@dataclass
class Check:
    relation: str  # The relation that FO and SO must satisfy.
    rows: list  # One (input label, input, output label, output) tuple per execution.
    holds: bool


# Metamorphic relations. Each one builds the follow-up input from SI.
# It runs the program on every input of the group and checks the relation between the outputs.


def mr1_add_k_to_first_element(program, si):
    n = len(si)
    fi = [si[0] + K_ADD] + si[1:]
    so, fo = program(si), program(fi)
    return Check(
        f"FO == SO + k / n, k = {K_ADD}, n = {n}",
        [("SI", si, "SO", so), ("FI", fi, "FO", fo)],
        same(fo, so + K_ADD / n),
    )


def mr2_add_k_to_every_element(program, si):
    fi = [number + K_ADD for number in si]
    so, fo = program(si), program(fi)
    return Check(
        f"FO == SO + k, k = {K_ADD}",
        [("SI", si, "SO", so), ("FI", fi, "FO", fo)],
        same(fo, so + K_ADD),
    )


def mr3_permutation(program, si):
    fi = list(reversed(si))  # Reversing is one permutation, any reordering would do.
    so, fo = program(si), program(fi)
    return Check("FO == SO", [("SI", si, "SO", so), ("FI", fi, "FO", fo)], same(fo, so))


def mr4_duplication(program, si):
    fi = si + si
    so, fo = program(si), program(fi)
    return Check("FO == SO", [("SI", si, "SO", so), ("FI", fi, "FO", fo)], same(fo, so))


def mr5_concatenation(program, si):
    si_1, si_2 = si, SECOND_SOURCE_INPUT
    n_1, n_2 = len(si_1), len(si_2)
    fi = si_1 + si_2
    so_1, so_2, fo = program(si_1), program(si_2), program(fi)
    return Check(
        f"FO == (n1 * SO-1 + n2 * SO-2) / (n1 + n2), n1 = {n_1}, n2 = {n_2}",
        [
            ("SI-1", si_1, "SO-1", so_1),
            ("SI-2", si_2, "SO-2", so_2),
            ("FI", fi, "FO", fo),
        ],
        same(fo, (n_1 * so_1 + n_2 * so_2) / (n_1 + n_2)),
    )


def mr6_splitting(program, si):
    middle = len(si) // 2
    fi_1, fi_2 = si[:middle], si[middle:]
    n, n_1, n_2 = len(si), len(fi_1), len(fi_2)
    so, fo_1, fo_2 = program(si), program(fi_1), program(fi_2)
    return Check(
        f"SO == (n1 * FO-1 + n2 * FO-2) / n, n1 = {n_1}, n2 = {n_2}, n = {n}",
        [
            ("SI", si, "SO", so),
            ("FI-1", fi_1, "FO-1", fo_1),
            ("FI-2", fi_2, "FO-2", fo_2),
        ],
        same(so, (n_1 * fo_1 + n_2 * fo_2) / n),
    )


def mr7_multiply_by_k(program, si):
    fi = [K_MULTIPLY * number for number in si]
    so, fo = program(si), program(fi)
    return Check(
        f"FO == k * SO, k = {K_MULTIPLY}",
        [("SI", si, "SO", so), ("FI", fi, "FO", fo)],
        same(fo, K_MULTIPLY * so),
    )


def mr8_remove_last_element(program, si):
    n, removed = len(si), si[-1]
    fi = si[:-1]
    so, fo = program(si), program(fi)
    return Check(
        f"FO == (n * SO - {removed}) / (n - 1), n = {n}",
        [("SI", si, "SO", so), ("FI", fi, "FO", fo)],
        same(fo, (n * so - removed) / (n - 1)),
    )


MRS = [
    ("MR1 Add k to the first element", mr1_add_k_to_first_element),
    ("MR2 Add k to every element", mr2_add_k_to_every_element),
    ("MR3 Permutation", mr3_permutation),
    ("MR4 Duplication", mr4_duplication),
    ("MR5 Concatenation", mr5_concatenation),
    ("MR6 Splitting", mr6_splitting),
    ("MR7 Multiply every element by k", mr7_multiply_by_k),
    ("MR8 Remove the last element", mr8_remove_last_element),
]


# Printing.


def show(value):
    return f"{value:.6g}" if isinstance(value, float) else str(value)


def print_check(name, check, indent="  "):
    verdict = "satisfied" if check.holds else "VIOLATED"
    print(f"{indent}{name}, expect {check.relation}: {verdict}")
    width = max(len(show(row[1])) for row in check.rows)
    for input_label, input_value, output_label, output_value in check.rows:
        print(
            f"{indent}    {input_label:<4} = {show(input_value):<{width}}    {output_label:<4} = {show(output_value)}"
        )


def show_step_1():
    correct = PROGRAMS[0]
    print(
        f"Step 1. Every MR holds for the correct program ({correct.__name__}) on the first source input"
    )
    for name, mr in MRS:
        print_check(name, mr(correct, SOURCE_INPUTS[0]))


def show_step_2():
    print(
        f"Step 2. Violated metamorphic groups out of {len(SOURCE_INPUTS)} for each MR (0 = fault not revealed)"
    )
    width = max(len(program.__name__) for program in PROGRAMS) + 2
    print("  " + " " * width + "".join(f"{name.split()[0]:>5}" for name, _ in MRS))
    for program in PROGRAMS:
        counts = [
            sum(not mr(program, si).holds for si in SOURCE_INPUTS) for _, mr in MRS
        ]
        print(
            f"  {program.__name__:<{width}}"
            + "".join(f"{count:>5}" for count in counts)
        )


def first_violation(program):
    for name, mr in MRS:
        for si in SOURCE_INPUTS:
            check = mr(program, si)
            if not check.holds:
                return name, check
    return None


def show_step_3():
    print("Step 3. The first violation found for each faulty program")
    for program in PROGRAMS[1:]:
        print(f"  {program.__name__}:")
        found = first_violation(program)
        if found is None:
            print("      no MR revealed this fault")
        else:
            print_check(*found, indent="    ")


if __name__ == "__main__":
    print("MT III, Example 2: The average of a series of integers\n")
    show_step_1()
    print()
    show_step_2()
    print()
    show_step_3()
