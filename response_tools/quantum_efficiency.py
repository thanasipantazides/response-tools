"""Code to load different quantum efficiencies. """

from dataclasses import dataclass
import logging
import os
import pathlib
import sys

from astropy.io import fits
import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np

import response_tools
from response_tools.util import BaseOutput, native_resolution

FILE_PATH = response_tools.responseFilePath
RESPONSE_INFO_TYPE = response_tools.contextResponseInfo["files"]["quantum_efficiency"]
ASSETS_PATH = os.path.join(pathlib.Path(__file__).parent, "assets", "response-tools-figs", "quantum-eff-figs")

@dataclass
class QuantumEffOutput(BaseOutput):
    """Class for keeping track of quantum efficiency response values."""
    # numbers
    mid_energies: u.Quantity
    quantum_efficiency: u.Quantity
    # bookkeeping
    detector: str
    # any other fields needed can be added here
    # can even add with a default so the input is not required for every other instance = np.nan<<u.keV

@u.quantity_input(mid_energies=u.keV)
def qe_cmos(mid_energies, telescope=None, file=None):
    """Return quantum efficency of CMOS detectors.
    
    Telescope 0: position 0, X10/FM2(?)
    Telescope 1: position 1, Nagoya(?)

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
        The energies at which the transmission is required. If 
        `numpy.nan<<astropy.units.keV` is passed then an entry for all 
        native file energies are returned. 
        Unit must be convertable to keV.

    telescope : `int`
        The focal plane position of the detector of the desired quantum 
        efficiency. Must be in the list [0, 1]. 
            Telescope 0 -> Position 0
            Telescope 1 -> Position 1
        Default: None

    file : `str` or `None`
        Gives the ability to provide custom files for the information. 
        Default: None

    Returns
    -------
    : `QuantumEffOutput`
        An object containing the energies for each quantum efficency, 
        the quantum efficencies, and more. See accessible information 
        using `.contents` on the output.
    """
    if (telescope is None) or (telescope not in [0,1]):
        logging.warning(f"The `telescope` input in {sys._getframe().f_code.co_name} must be 0 or 1.")
        return
    
    _f = os.path.join(FILE_PATH, RESPONSE_INFO_TYPE[f"qe_cmos_telescope-{telescope}"]) if file is None else file
    with fits.open(_f) as hdul:
        es, qe = hdul[2].data << u.keV, hdul[1].data << u.dimensionless_unscaled
    mid_energies = native_resolution(native_x=es, input_x=mid_energies)

    return QuantumEffOutput(filename=_f,
                            function_path=f"{sys._getframe().f_code.co_name}",
                            mid_energies=mid_energies,
                            quantum_efficiency=np.interp(mid_energies.value, 
                                                         es.value, 
                                                         qe.value, 
                                                         left=0, 
                                                         right=0) << u.dimensionless_unscaled,
                            detector="CMOS{telescope}-Quantum-Efficiency"
                            )

def asset_qe(save_location=None):
    mid_energies = np.linspace(0, 20, 1000)<<u.keV
    plt.figure()
    qe0 = qe_cmos(mid_energies, telescope=0)
    qe1 = qe_cmos(mid_energies, telescope=1)
    plt.plot(mid_energies, qe0.quantum_efficiency, lw=2, label="CMOS telescope 0, position 0")
    plt.plot(mid_energies, qe1.quantum_efficiency, lw=1, ls=":", label="CMOS telescope 1, position 1")
    plt.title("CMOS Detectors")
    plt.ylabel(f"Quantum efficiency [{qe0.quantum_efficiency.unit:latex}]")
    plt.xlabel(f"Energy [{mid_energies.unit:latex}]")
    plt.xlim([np.min(mid_energies.value), np.max(mid_energies.value)])
    plt.ylim([0, 1.01])
    plt.legend()
    if save_location is not None:
        pathlib.Path(save_location).mkdir(parents=True, exist_ok=True)
        plt.savefig(os.path.join(save_location,"cmos-qunatum-eff.png"), dpi=200, bbox_inches="tight")
    plt.show()

if __name__=="__main__":
    save_location = None # ASSETS_PATH
    asset_qe(save_location=save_location)