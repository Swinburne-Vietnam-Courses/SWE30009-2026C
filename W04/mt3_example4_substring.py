"""
Metamorphic testing demo for MT III, Example 4: How many times St1 appears in St2.

The specification counts overlapping occurrences: "aaa" appears 4 times in "aaaaaab...".
The script checks the MRs from the summary table against one correct program and two
faulty versions, then shows which MR reveals which fault.
"""

from dataclasses import dataclass

# Five source inputs (St1, St2), so every MR gets five metamorphic groups.
# The first two are the lecture examples.
SOURCE_INPUTS = [
    ("aaa", "aaaaaabaaddaabcabdcdaabacccdbabaddc"),
    ("abac", "abadcabacddaabcabdcdaabacccdbabaddc"),
    ("bb", "bbb"),
    ("abac", "ddcabac"),
    ("aba", "ababa"),
]


# Programs under test. The first one is correct, the other two contain one fault each.


def count_correct(st1, st2):
    count = 0
    for start in range(len(st2) - len(st1) + 1):
        if st2[start : start + len(st1)] == st1:
            count += 1
    return count


# Fault: Python's str.count skips overlapping occurrences.
def count_with_str_count(st1, st2):
    return st2.count(st1)


# Fault: the loop stops one position too early, so a match at the very end is missed.
def count_off_by_one(st1, st2):
    count = 0
    for start in range(len(st2) - len(st1)):
        if st2[start : start + len(st1)] == st1:
            count += 1
    return count


PROGRAMS = [count_correct, count_with_str_count, count_off_by_one]


# The result of checking one MR on one metamorphic group.
@dataclass
class Check:
    relation: str  # The relation that FO and SO must satisfy.
    rows: list  # One (input label, input, output label, output) tuple per execution.
    holds: bool


# Metamorphic relations. SI = (SI-St1, SI-St2) and FI = (FI-St1, FI-St2).


def mr1_delete_first_char_of_st1(program, si):
    st1, st2 = si
    fi = (st1[1:], st2)
    so, fo = program(*si), program(*fi)
    return Check("FO >= SO", [("SI", si, "SO", so), ("FI", fi, "FO", fo)], fo >= so)


def mr2_delete_last_char_of_st1(program, si):
    st1, st2 = si
    fi = (st1[:-1], st2)
    so, fo = program(*si), program(*fi)
    return Check("FO >= SO", [("SI", si, "SO", so), ("FI", fi, "FO", fo)], fo >= so)


def mr3_double_st2(program, si):
    st1, st2 = si
    fi = (st1, st2 + st2)
    so, fo = program(*si), program(*fi)
    return Check(
        "FO >= 2 * SO", [("SI", si, "SO", so), ("FI", fi, "FO", fo)], fo >= 2 * so
    )


def mr4_reverse_both(program, si):
    st1, st2 = si
    fi = (st1[::-1], st2[::-1])
    so, fo = program(*si), program(*fi)
    return Check("FO == SO", [("SI", si, "SO", so), ("FI", fi, "FO", fo)], fo == so)


def mr5_delete_first_char_of_st2(program, si):
    st1, st2 = si
    fi = (st1, st2[1:])
    so, fo = program(*si), program(*fi)
    if st2.startswith(st1):
        relation, expected = "FO == SO - 1 (SI-St2 starts with SI-St1)", so - 1
    else:
        relation, expected = "FO == SO (SI-St2 does not start with SI-St1)", so
    return Check(relation, [("SI", si, "SO", so), ("FI", fi, "FO", fo)], fo == expected)


MRS = [
    ("MR1 Delete the first character of St1", mr1_delete_first_char_of_st1),
    ("MR2 Delete the last character of St1", mr2_delete_last_char_of_st1),
    ("MR3 Double St2", mr3_double_st2),
    ("MR4 Reverse both strings", mr4_reverse_both),
    ("MR5 Delete the first character of St2", mr5_delete_first_char_of_st2),
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


def show_not_an_mr():
    print("Not an MR: delete a middle character of St1, correct program")
    for si in [("abc", "abc"), ("abc", "acac")]:
        fi = ("ac", si[1])
        so, fo = count_correct(*si), count_correct(*fi)
        print(
            f"      SI   = {show(si):<16}    SO   = {so}    FI   = {show(fi):<16}    FO   = {fo}"
        )
    print("      FO went down once and up once, so FO and SO have no fixed relation")


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
    print("MT III, Example 4: How many times St1 appears in St2\n")
    show_step_1()
    print()
    show_not_an_mr()
    print()
    show_step_2()
    print()
    show_step_3()
