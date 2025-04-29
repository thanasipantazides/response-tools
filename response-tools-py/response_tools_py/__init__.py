"""
Top level of the `response-tools-py` package.

Namespace
---------

The base `response_tools_py` namespace includes:

`~response_tools_py.contextResponseInfo`
    The information stored in a YAML file that includes information from
    the flight.

`~response_tools_py.__version__`
    The current version of the code as stated in the setup script.

Examples
--------
# importing the module is as easy as:
>>> import response_tools_py

# then accessing, e.g., the context information for the flight/flare
>>> print(response_tools_py.contextResponseInfo)
...

# that can be accessed like a native Python dictionary
>>> print(response_tools_py.contextResponseInfo[""])
...
"""

from .version import __version__
from response_tools_py.io.load_yaml import load_response_context

# for global context info
contextResponseInfo = load_response_context()
