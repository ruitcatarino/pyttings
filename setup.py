import os

from setuptools import find_packages, setup

version = os.getenv("PACKAGE_VERSION", "0.0.1")

setup(
    name="pyttings",
    version=version,
    author="Rui Catarino",
    description="Python settings management with namespacing and modular files. Inspired by Django.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ruitcatarino/pyttings",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[],
)