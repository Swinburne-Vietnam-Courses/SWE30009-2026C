# Metamorphic testing of a sine function without a test oracle.
import math


def correct_sin_deg(x_deg):
    return math.sin(math.radians(x_deg))


# Taylor series sine.
# Fault: No range reduction, so large angles go wrong.
def buggy_sin_deg(x_deg):
    x = math.radians(x_deg)
    term = total = x
    for n in range(1, 8):
        term *= -x * x / ((2 * n) * (2 * n + 1))
        total += term
    return total


def run_metamorphic_tests(sin_deg, x):
    source_output = sin_deg(x)  # We cannot verify this value directly.
    mr1_holds = math.isclose(sin_deg(x + 360), source_output, abs_tol=1e-9)
    mr2_holds = math.isclose(sin_deg(-x), -source_output, abs_tol=1e-9)
    print(f"{sin_deg.__name__}: sin({x}) = {source_output:.5f}")
    print(f"  MR1 sin(x) = sin(x + 360): {'satisfied' if mr1_holds else 'VIOLATED'}")
    print(f"  MR2 sin(-x) = -sin(x):     {'satisfied' if mr2_holds else 'VIOLATED'}")


for implementation in (correct_sin_deg, buggy_sin_deg):
    run_metamorphic_tests(implementation, 29.8)

# Floating-point caveat: A correct sum can change when the order changes.
print(1 + 2 + 3 == 3 + 2 + 1)  # True
print(0.1 + 0.2 + 0.3 == 0.3 + 0.2 + 0.1)  # False
