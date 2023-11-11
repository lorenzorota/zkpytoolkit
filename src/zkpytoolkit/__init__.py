from __future__ import annotations

import os
from zkpytoolkit.__about__ import __author__, __version__
from zkpytoolkit.hazmat.bindings import compiler

current_directory = os.path.dirname(os.path.abspath(__file__))
stdlib_path = os.path.join(current_directory, 'stdlib')

# Export ZKPyC stdlib path for the compiler
os.environ['ZKPYC_STDLIB_PATH'] = stdlib_path

__all__ = [
    "__version__",
    "__author__",
    "compiler",
]