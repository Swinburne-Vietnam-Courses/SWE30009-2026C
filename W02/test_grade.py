# pip install pytest-cov
# pytest test_grade.py --cov=grade --cov-branch --cov-report=term-missing
# pytest test_grade.py --cov=grade --cov-branch --cov-report=html

from grade import grade


def test_hd():
    assert grade(85) == "HD"


def test_p():
    assert grade(55) == "P"


# Test Coverage >= 80%
