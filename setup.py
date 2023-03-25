import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

VERSION = "1.0.2"
NAME = "pyplAI"
DESCRIPTION = "Biblioteca para Python con algoritmos de resolución de juegos de mesa (minimax, MCTS, SO-ISMCTS y MO-ISMCTS)"
LONG_DESCRIPTION = (HERE / "README.md").read_text(encoding='utf-8')
LONG_DESC_TYPE = "text/markdown"

AUTHOR = "Pedro Luis Soto Santos"
EMAIL = "pepoluis712@gmail.com"
URL = "https://github.com/plss12/pyplAI"
LICENSE = "MIT"

INSTALL_REQUIRES = []

KEYWORDS = ["python", "articial intelligence", "AI", "games", "board games", "minimax", "alpha-beta", "monte carlo", "monte carlo tree search", "UCT", "game theory", "information set", "perfect information", "imperfect information"]
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "Intended Audience :: Education",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: Spanish",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Topic :: Games/Entertainment :: Board Games",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Typing :: Typed"
]

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    license=LICENSE,
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    include_package_data=True,
    keywords= KEYWORDS,
    classifiers= CLASSIFIERS
)