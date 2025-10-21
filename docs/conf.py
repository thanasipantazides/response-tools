# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import pathlib
import sys
sys.path.insert(0, os.path.abspath(".."))   

this_folder = os.path.dirname(__file__)

# -- Project information -----------------------------------------------------

project = "response-tools"
copyright = "2025, The FOXSI Collaboration"
author = "The FOXSI Collaboration"

# The full version, including alpha/beta/rc tags
release = "1.0.0"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.githubpages",
    "sphinxemoji.sphinxemoji",
    "sphinx_gallery.gen_gallery",
    "myst_parser",
]
myst_enable_extensions = [
    "dollarmath",
    "html_image",
]

source_suffix = [".rst", ".md"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"
html_logo = "Glyph_FOXSI4_text.png"
html_favicon = "Glyph_FOXSI4_favicon.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = [os.path.join(this_folder, "styles")]

html_css_files = [
    os.path.join(this_folder, "styles", "svg_width_style.css")
]

sphinx_gallery_conf = {
     "examples_dirs": "../examples",   # path to your example scripts
     "gallery_dirs": "auto_examples",  # path to where to save gallery generated output
     "default_thumb_file": os.path.join(pathlib.Path(__file__).parent, "foxsi-1sol.png"),
}