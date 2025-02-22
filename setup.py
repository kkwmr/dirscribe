#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages


this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="dirscribe",
    version="0.1.3",
    description="A tool to export directory structure and optionally include file contents for selected extensions.",
    long_description=long_description,
    long_description_content_type="text/markdown", 
    author="Kazuki Kawamura",
    url="https://github.com/kkwmr/dirscribe",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "pyperclip",
    ],
    entry_points={
        "console_scripts": [
            "dirscribe=dirscribe.core:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    license="MIT"
)