from ._rust import compiler

__all__ = ["compiler"]

# It is a common practice in Python packaging to keep the extension modules
# private and use Pure Python modules to wrap them.
# This allows you to have a very fine control over the public API.
