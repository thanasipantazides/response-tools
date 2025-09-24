"""
Top level of the `response-tools` package.

Namespace
---------

The base `response_tools` namespace includes:

`~response_tools.contextResponseInfo`
    The information stored in a YAML file that includes information from
    the flight.

`~response_tools.__version__`
    The current version of the code as stated in the setup script.

Examples
--------
# importing the module is as easy as:
>>> import response_tools

# then accessing, e.g., the context information for the flight/flare
>>> print(response_tools.contextResponseInfo)
...

# that can be accessed like a native Python dictionary
>>> print(response_tools.contextResponseInfo["..."])
...
"""

from .version import __version__
from response_tools.io.load_yaml import load_response_context

# for global context info
contextResponseInfo = load_response_context()
