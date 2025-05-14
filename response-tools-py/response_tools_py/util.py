"""Generally useful functions."""

import numpy as np

def native_resolution(native_x, input_x):
    """Providing an input for effective areas, etc., this function can 
    help decide whether to return values to interpolate to or to just 
    interpolate to the original x-points.
    
    The idea here is that if we want to improve/change the logic here 
    then we only have to do it here and not literally everywhere.
    """
    return native_x if np.all(np.isnan(input_x)) else input_x