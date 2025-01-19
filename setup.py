#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="dirscribe",
    version="0.1.0",
    description="A tool to export directory structure and optionally include file contents for selected extensions.",
    long_description="DirScribe is a Python package and CLI that helps you turn a directory's structure into text, with optional file content inclusion.",
    long_description_content_type="text/markdown",
    author="Kazuki Kawamura",
    url="https://github.com/kkwmr/dirscribe",
    packages=find_packages(),
    python_requires=">=3.7",
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
