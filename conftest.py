"""Make the ``asktheboard`` package importable when pytest runs without an install.

Running bare ``pytest`` on a fresh clone (no ``pip install -e .``) collects
``tests/`` with the package dir off ``sys.path``. Inserting it here -- auto-loaded
for any test in this tree, regardless of the invocation directory -- lets
``from asktheboard import ...`` resolve so the suite works with zero setup.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
