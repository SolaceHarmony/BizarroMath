# setup.py
from setuptools import setup, find_packages

setup(
    name="bizarromath",
    version="0.1.0",
    description="High-performance chunk-based big-int and fraction library (Bizarro style).",
    packages=find_packages(),
    install_requires=[
        # or whichever versions
    ],
    python_requires=">=3.7",
)