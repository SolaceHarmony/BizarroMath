# setup.py
from setuptools import setup, find_packages

setup(
    name="bizarromath",
    version="0.1.0",
    description="High-performance chunk-based big-int and fraction library (Bizarro style).",
    author="Sydney Renee",
    author_email="sydney@solace.ofharmony.ai", 
    packages=find_packages(where='python/bizarromath',include=['bizarromath', 'bizarromath.*']),
    package_dir={'': 'python'},
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0"
    ],
    python_requires=">=3.12",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)