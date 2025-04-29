"""Code to create photon models. """

import astropy.units as u
from copy import deepcopy
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.io import readsav

def get_energy_delta():
    """Return energy bin width."""
    return 0.0445 << u.keV

def create_energy_edges():
    """One function to handle giving out the same energies."""
    # no longer needed with above files `lower_e = 1.0002920302956426` # from lower bounds thermal() error, in KeV
    lower_e = 0.5 # from lower bounds thermal() error, in KeV
    return np.arange(lower_e, 100, get_energy_delta().value) << u.keV

def create_energy_midpoints(edges=None):
    """Tied to `create_energy_edges`."""
    _edges = create_energy_edges() if edges is None else edges
    return (_edges[1:]+_edges[:-1])/2

def zeroes2nans(array):
    """Replace 0s in the array with np.nans."""
    _array_copy = deepcopy(array)
    _array_copy[np.nonzero(array==0)] = np.nan
    return _array_copy

def nans2zeroes(array):
    """Replace Nans in the array with Os."""
    _array_copy = deepcopy(array)
    _array_copy[np.isnan(array)] = 0
    return _array_copy

def gaussian_blur(array, fwhm):
    """Apply a Gaussian blur (with FWHM) to an array. 
    
    Parameters
    ----------
    array : `numpy.ndarray`
        Array to which apply blurring.
        
    fwhm : `int`, `float`
        Full-width half-max of the Gaussian. must be in units of "number
        of bins" for the function,  not anything else like energy, etc.
    """
    sigma = fwhm/2.355 # std for kernal in units of "number of bins"
    return gaussian_filter1d(array, sigma)

def sxr_res():
    """Return the SXR energy resolution (from Albert).
    
    FOXSI-4: 0.4 keV @ 10 keV
    Albert: 0.2 keV
    """
    return 0.2 << u.keV

def sxr_blur(array):
    """Apply the FOXSI-4 SXR energy resolution to the incoming array. """
    return gaussian_blur(array, sxr_res()/get_energy_delta()) << array.unit

def hxr_res():
    """Return the HXR energy resolution (from FOXSI-4).
    
    0.8 keV @ 14 keV
    """
    return 0.8 << u.keV

def hxr_blur(array):
    """Apply the FOXSI-4 HXR energy resolution to the incoming array. """
    return gaussian_blur(array, hxr_res()/get_energy_delta()) << array.unit

def _load_idl_sim(filename):
    """Function to return simulated spectrum."""
    results = readsav(filename)

    energy_edges = results["e_hist_bins"]
    full_loop = results["spatially_resolved_I_photon"][:,0]
    loop_top = results["spatially_resolved_I_photon"][:,1]
    mean_footpoint = results["spatially_resolved_I_photon"][:,2]

    return {"model":{"energy_edges":energy_edges << u.keV, "full_loop":full_loop << (u.ph / (u.keV * u.s * u.cm**2))}, 
            "submodels":{"loop_top":loop_top << (u.ph / (u.keV * u.s * u.cm**2)), "footpoints":mean_footpoint << (u.ph / (u.keV * u.s * u.cm**2))}}

def sim_energy_edges(*_, filename=None, **__):
    """Access energy bin edges from Morgan's simulations."""
    return _load_idl_sim(filename)["model"]["energy_edges"]

def sim_full_loop(*_, filename=None, **__):
    """Access full loop spectrum from Morgan's simulations."""
    return _load_idl_sim(filename)["model"]["full_loop"]

def sim_loop_top(*_, filename=None, **__):
    """Access loop-top spectrum from Morgan's simulations."""
    return _load_idl_sim(filename)["submodels"]["loop_top"]

def sim_footpoints(*_, filename=None, **__):
    """Access ONE footpoint spectrum from Morgan's simulations."""
    return _load_idl_sim(filename)["submodels"]["footpoints"]