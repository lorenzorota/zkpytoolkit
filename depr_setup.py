#!/usr/bin/env python

import pathlib
from setuptools import setup, find_packages, find_namespace_packages

# from .zkpytoolkit import compiler

from setuptools_rust import Binding, RustExtension

HERE = pathlib.Path(__file__).parent
VERSION = '0.1.0'
PACKAGE_NAME = 'ZKPyToolkit'
AUTHOR = 'Lorenzo Rota'
AUTHOR_EMAIL = 'lorenzo.rota@tno.nl'
URL = 'https://code.example.com/example-package2'
LICENSE = 'Apache License 2.0'
DESCRIPTION = 'Zero-knowledge proof toolkit for verifiable computing.'
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

# Dependencies for the package
INSTALL_REQUIRES = [
]

# setup is the gateway to the package build process.
# The only required components for a package are
# the name, author and contact, and description.
setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      url=URL,
      install_requires=INSTALL_REQUIRES,
      packages=find_packages(exclude=['compiler']),
      # packages=find_namespace_packages(exclude=['docs', 'tests', 'examples']),
      rust_extensions=[
          RustExtension(
              "zkpytoolkit.compiler._lib",
              # ^-- The last part of the name (e.g. "_lib") has to match lib.name
              #     in Cargo.toml and the function name in the `.rs` file,
              #     but you can add a prefix to nest it inside of a Python package.
              path="zkpytoolkit/compiler/Cargo.toml",  # Default value, can be omitted
              py_limited_api="auto",  # Default value, can be omitted
              binding=Binding.PyO3,  # Default value, can be omitted
          )
      ],
      )
