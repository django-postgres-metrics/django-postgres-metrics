# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

import django
from pkg_resources import get_distribution

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------


sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("../../example/"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")
django.setup()


# -- Project information -----------------------------------------------------

project = "django-postgres-metrics"
copyright = "2017-2020, Markus Holtermann and others"
author = "Markus Holtermann and others"

version = release = get_distribution("django-postgres-metrics").version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "ext",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


# -- Extensions configuration ------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "django": ("http://django.readthedocs.org/en/latest/", None),
    "rich": ("http://rich.readthedocs.org/en/latest/", None),
}
