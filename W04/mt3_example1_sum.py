"""
Metamorphic testing demo for MT III, Example 1: The sum of a series of integers.

The script checks the MRs from the summary table against one correct program and two
faulty versions of it, then shows which MR reveals which fault.
"""

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


def sum_correct(numbers):
    total = 0
    for number in numbers:
        total += number
    return total


# Fault: the running total starts at 1 instead of 0.
def sum_starts_at_one(numbers):
    total = 1
    for number in numbers:
        total += number
    return total


# Fault: the loop starts at index 1, so the first element is never added.
def sum_skips_first(numbers):
    total = 0
    for index in range(1, len(numbers)):
        total += numbers[index]
    return total


PROGRAMS = [sum_correct, sum_starts_at_one, sum_skips_first]


# The result of checking one MR on one metamorphic group.
@dataclass
class Check:
    relation: str  # The relation that FO and SO must satisfy.
    rows: list  # One (input label, input, output label, output) tuple per execution.
    holds: bool


# Metamorphic relations. Each one builds the follow-up input from SI.
# It runs the program on every input of the group and checks the relation between the outputs.


def mr1_add_k_to_first_element(program, si):
    fi = [si[0] + K_ADD] + si[1:]
    so, fo = program(si), program(fi)
    return Check(
        f"FO == SO + k, k = {K_ADD}",
        [("SI", si, "SO", so), ("FI", fi, "FO", fo)],
        fo == so + K_ADD,
    )


def mr2_add_k_to_every_element(program, si):
    n = len(si)
    fi = [number + K_ADD for number in si]
    so, fo = program(si), program(fi)
    return Check(
        f"FO == SO + n * k, n = {n}, k = {K_ADD}",
        [("SI", si, "SO", so), ("FI", fi, "FO", fo)],
        fo == so + n * K_ADD,
    )


def mr3_permutation(program, si):
    fi = list(reversed(si))  # Reversing is one permutation, any reordering would do.
    so, fo = program(si), program(fi)
    return Check("FO == SO", [("SI", si, "SO", so), ("FI", fi, "FO", fo)], fo == so)


def mr4_duplication(program, si):
    fi = si + si
    so, fo = program(si), program(fi)
    return Check(
        "FO == 2 * SO", [("SI", si, "SO", so), ("FI", fi, "FO", fo)], fo == 2 * so
    )


def mr5_concatenation(program, si):
    si_1, si_2 = si, SECOND_SOURCE_INPUT
    fi = si_1 + si_2
    so_1, so_2, fo = program(si_1), program(si_2), program(fi)
    return Check(
        "FO == SO-1 + SO-2",
        [
            ("SI-1", si_1, "SO-1", so_1),
            ("SI-2", si_2, "SO-2", so_2),
            ("FI", fi, "FO", fo),
        ],
        fo == so_1 + so_2,
    )


def mr6_splitting(program, si):
    middle = len(si) // 2
    fi_1, fi_2 = si[:middle], si[middle:]
    so, fo_1, fo_2 = program(si), program(fi_1), program(fi_2)
    return Check(
        "FO-1 + FO-2 == SO",
        [
            ("SI", si, "SO", so),
            ("FI-1", fi_1, "FO-1", fo_1),
            ("FI-2", fi_2, "FO-2", fo_2),
        ],
        fo_1 + fo_2 == so,
    )


def mr7_multiply_by_k(program, si):
    fi = [K_MULTIPLY * number for number in si]
    so, fo = program(si), program(fi)
    return Check(
        f"FO == k * SO, k = {K_MULTIPLY}",
        [("SI", si, "SO", so), ("FI", fi, "FO", fo)],
        fo == K_MULTIPLY * so,
    )


def mr8_remove_last_element(program, si):
    removed = si[-1]
    fi = si[:-1]
    so, fo = program(si), program(fi)
    return Check(
        f"FO == SO - {removed} (the removed element)",
        [("SI", si, "SO", so), ("FI", fi, "FO", fo)],
        fo == so - removed,
    )


def mr9_append_minus_so(program, si):
    so = program(si)
    fi = si + [-so]  # The follow-up input depends on the source output.
    fo = program(fi)
    return Check("FO == 0", [("SI", si, "SO", so), ("FI", fi, "FO", fo)], fo == 0)


MRS = [
    ("MR1 Add k to the first element", mr1_add_k_to_first_element),
    ("MR2 Add k to every element", mr2_add_k_to_every_element),
    ("MR3 Permutation", mr3_permutation),
    ("MR4 Duplication", mr4_duplication),
    ("MR5 Concatenation", mr5_concatenation),
    ("MR6 Splitting", mr6_splitting),
    ("MR7 Multiply every element by k", mr7_multiply_by_k),
    ("MR8 Remove the last element", mr8_remove_last_element),
    ("MR9 Append -SO", mr9_append_minus_so),
]


# Printing.


def show(value):
    return str(value)


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
    print("MT III, Example 1: The sum of a series of integers\n")
    show_step_1()
    print()
    show_step_2()
    print()
    show_step_3()
