"""Code to load different quantum efficiencies. """

import logging
import os
import pathlib

from astropy.io import fits
import astropy.units as u
import numpy as np

Q_PATH = os.path.join(pathlib.Path(__file__).parent, "..", "..", "response-information", "quantum-efficiency-data")

@u.quantity_input(mid_energies=u.keV)
def qe_cmos(mid_energies, file=None, telescope=None):
    """Return quantum efficency of CMOS detectors.
    
    Telescope 0: position 0, X10/FM2(?)
    Telescope 1: position 1, Nagoya(?)
    """
    if telescope is None:
        logging.warning("`telescope` input in `qe_cmos()` must be 0 or 1.")
        return
        
    _f = os.path.join(Q_PATH, f"foxsi4_telescope-{telescope}_BASIC_sensor_quantum_efficiency_v1.fits") if file is None else file
    with fits.open(_f) as hdul:
        es, qe = hdul[2].data << u.keV, hdul[1].data << u.dimensionless_unscaled
    return np.interp(mid_energies.value, es.value, qe.value, left=0, right=0) << u.dimensionless_unscaled

if __name__=="__main__":
    import matplotlib.pyplot as plt

    SAVE_ASSETS = False
    assets_dir = os.path.join(pathlib.Path(__file__).parent, "..", "..", "assets", "response-tools-py-figs", "quantum-eff-figs")
    pathlib.Path(assets_dir).mkdir(parents=True, exist_ok=True)

    mid_energies = np.linspace(0, 20, 1000)<<u.keV
    plt.figure()
    qe0 = qe_cmos(mid_energies, telescope=0)
    qe1 = qe_cmos(mid_energies, telescope=1)
    plt.plot(mid_energies, qe0, lw=2, label="CMOS telescope 0, position 0")
    plt.plot(mid_energies, qe1, lw=1, ls=":", label="CMOS telescope 1, position 1")
    plt.title("CMOS Detectors")
    plt.ylabel(f"Quantum efficiency [{qe0.unit:latex}]")
    plt.xlabel(f"Energy [{mid_energies.unit:latex}]")
    plt.xlim([np.min(mid_energies.value), np.max(mid_energies.value)])
    plt.ylim([0, 1.01])
    plt.legend()
    if SAVE_ASSETS:
        plt.savefig(os.path.join(assets_dir,"cmos-qunatum-eff.png"), dpi=200, bbox_inches="tight")
    plt.show()
