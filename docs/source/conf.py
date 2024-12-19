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
# gui_model_directory = os.path.join(parent_directory, "GUI/model")
# gui_view_directory = os.path.join(parent_directory, "GUI/view")
sys.path.insert(0, parent_directory)
sys.path.insert(0, scripts_directory)
# sys.path.insert(0, gui_model_directory)
# sys.path.insert(0, gui_view_directory)

project = "SousChef"
copyright = "2024, Nicholas Camardo, Shalini Sai Prasad, Rajat Shrivastava, Trinanjan Nandi"
author = "Nicholas Camardo, Shalini Sai Prasad, Rajat Shrivastava, Trinanjan Nandi"
release = "0.2"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.todo",
]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
