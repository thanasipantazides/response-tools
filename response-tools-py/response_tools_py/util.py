"""Generally useful functions."""

from dataclasses import dataclass
from pprint import pprint

import numpy as np

def native_resolution(native_x, input_x):
    """Providing an input for effective areas, etc., this function can 
    help decide whether to return values to interpolate to or to just 
    interpolate to the original x-points.
    
    The idea here is that if we want to improve/change the logic here 
    then we only have to do it here and not literally everywhere.
    """
    return native_x if np.all(np.isnan(input_x)) else input_x
@dataclass
class BaseOutput:
    """Class for keeping track of general response values."""
    filename: str
    # put the highest level function that returns the object
    # designed to be overwritten if a wrapper is around a function, etc.
    function_path: str 

    @property
    def contents(self):
        """Contents of the data class. """
        return self.__dict__

    @property
    def fields(self):
        """Just the names of the fields in the data class. """
        return list(self.contents.keys())

    @property
    def print_contents(self):
        """Print the contents of the data class in a nice way. """
        pprint(self.contents)

    def update_function_path(self, new_function_name:str):
        """Should help tracking nested function if needed."""
        self.function_path += f"\n->{new_function_name}"

    def __getitem__(self, index:str):
        """Allow the field names to be passed like indices too.
        
        Example
        -----------
        >>> ex = BaseOutput(filename="foo", function="bar")
        >>> ex.filename
        "foo"
        >>> ex["filename"]
        "foo"
        """
        return (self.contents | {"fields":self.fields})[index]
    
