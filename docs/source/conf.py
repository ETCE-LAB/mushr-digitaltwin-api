# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'MushR DigitalTwin API'
copyright = '2023, Anant Sujatanagarjuna'
author = 'Anant Sujatanagarjuna'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import os, sys

# Add source directory to sys.path
sys.path.insert(0, os.path.abspath("../../mushr_digitaltwin_api"))

# Add sphinxcontrib_django to installed extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinxcontrib_django",
]
autosummary_generate = True

# Configure the path to the Django settings module
django_settings = "mushr_digitaltwin_api.settings"

# Include the database table names of Django models
django_show_db_tables = True

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
