"""
Create virtual environment:
python3 -m venv .venv

Activate virtual environment:
+ Windows: .venv\Scripts\Activate.ps1
+ macOS: source .venv/bin/activate

After activating virtual environment, install pytest.
pip install pytest
"""


# This bar is for 18+ people.
def can_enter(age):
    if age > 18:
        return True
    else:
        return False
