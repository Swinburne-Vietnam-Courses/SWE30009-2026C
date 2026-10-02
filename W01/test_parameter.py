"""
3 types:
- Positive: 20, 60
- Negative: -15, 0, 15
- Boundary: 17, 18, 19
"""

import pytest
from sample import can_enter


@pytest.mark.parametrize(
    "age, expected",
    [
        (20, True),
        (60, True),
        (15, False),
        (-15, False),
        (18, True),
        (17, False),
    ],
)
def test_can_enter(age, expected):
    assert can_enter(age) == expected
