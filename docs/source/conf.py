# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

current_directory = os.path.abspath(__file__)
parent_directory = os.path.dirname(os.path.dirname(os.path.dirname(current_directory)))
scripts_directory = os.path.join(parent_directory, "scripts")
gui_directory = os.path.join(parent_directory, "GUI")
sys.path.insert(0, scripts_directory)
sys.path.insert(0, gui_directory)

project = "USC-DR-RAWCOOKED"
copyright = "2024, Shalini Sai Prasad, Rajat Shrivastava, Trinanjan Nandi"
author = "Shalini Sai Prasad, Rajat Shrivastava, Trinanjan Nandi"
release = "0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.todo",
    "myst_parser"
]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
