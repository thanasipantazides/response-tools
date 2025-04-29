# `response-tools-py`

A repository to software tools for the response system used for the FOXSI mission in Python (woo, Python). We will include helpful loader functions for the all the response elements and download clients to obtain the files.

The tools being developed in Python should be placed in the `response_tools_py` folder (note the underscores and not dashes).

There is an "examples" and a "tests" folder. The "examples" folder is a great place to include scripts that show how some of the code in the repository works and the "tests" folder is a fantastic place to put code that tests the tools that have been created.

More information will be placed here with regards as to how this package is recommended to be used.

## Install tips

In order to work with some preliminary data, it is instructive to set up a virtual environment (more information below) and install necessary packages. The suggested way to do this is to create an environment with:

- `conda create -n response-tools-env python==3.12`

(recommend using Python 3.12 just because this has been proven to be stable with the software).

The Python code can then be installed with:

- `pip install -e .`

while in this directory (the `response-tools-py` directory) containing the `setup.py` file.

Any time the code is updated and, say, you pull it from Github, make sure to perform the `pip install -e .` line from above. This ensures any new changes, updated versions, etc. take effect.

## Namespace

The base `response_tools_py` namespace includes:

- `~response_tools_py.contextResponseInfo`
  - The information stored in a [YAML file](../response-information/info.yaml) that includes file version information (e.g., the current versions to be used) and can be accessed like a Python dictionary.
- `~response_tools_py.__version__`
  - The version of the code determined by `response-tools-py/setup.py`.
    - `0.0.1`: First rendition of the code.

### Examples using the namespace

```python
# importing the module is as easy as:
>>> import response_tools_py

# can access the YAML file contents in the code as 
>>> print(response_tools_py.contextResponseInfo[""])
...

# then accessing the version as:
>>> print(response_tools_py.__version__)
'0.0.1'
```

## Useful Python tips

Some useful things to keep in mind while using the Python code in this repository.

### Virtual environments

It might be a good idea to look into ([conda](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)) virtual environments if you are not familiar, this includes looking into them yourself or getting in touch with someone to help explain. This requires downloading [miniconda](https://docs.anaconda.com/miniconda/install/#quick-command-line-install) (or just conda if you prefer).
