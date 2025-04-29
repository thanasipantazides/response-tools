"""Code to load different attenuators. """

import logging
import os
import pathlib

from astropy.io import fits
import astropy.units as u
import numpy as np
import pandas
import scipy

# thermal blanket attenuation
@u.quantity_input(mid_energies=u.keV)
def att_thermal_blanket(mid_energies, file=None):
    """Return thermal blanket transmittance interpolated to the given energies."""
    _f = os.path.join(pathlib.Path(__file__).parent, 
                            "att-data", 
                            "F4_Blanket_transmission.dat") if file is None else file
    att = scipy.io.readsav(_f)
    att_es, att_values = att["energy_kev"] << u.keV, att["f4_transmission"] << u.dimensionless_unscaled
    return np.interp(mid_energies.value, att_es.value, att_values.value, left=0, right=1) << u.dimensionless_unscaled

# thermal blanket attenuation
@u.quantity_input(mid_energies=u.keV)
def att_uniform_al_cdte(mid_energies, file=None, position=None):
    """Return thermal blanket transmittance interpolated to the given energies."""
    if position is None:
        logging.info("`position` must be 2 or 4.")
    _f = os.path.join(pathlib.Path(__file__).parent, 
                            "att-data", 
                            f"unif_att_p{position}_theoretical.csv") if file is None else file
    att = pandas.read_csv(_f)
    att_es, att_values = att["energy[keV]"] << u.keV, att["transmission"] << u.dimensionless_unscaled
    return np.interp(mid_energies.value, att_es.value, att_values.value, left=0, right=1) << u.dimensionless_unscaled

# pixelated attenuator attenuation
@u.quantity_input(mid_energies=u.keV)
def att_pixelated(mid_energies, file=None, values=None):
    """Return pixelated attenuator transmittance interpolated to the given energies."""
    _f = os.path.join(pathlib.Path(__file__).parent, 
                            "att-data", 
                            "20240607_fosxi4_transmission.csv") if file is None else file
    att = pandas.read_csv(_f)
    att_es, att_values_measured, att_values_modelled = att["energy"] << u.keV, att["measured_transmission"] << u.dimensionless_unscaled, att["modeled_transmission"] << u.dimensionless_unscaled

    if values=="measured":
        return np.interp(mid_energies.value, att_es.value, att_values_measured.value, left=0, right=1) << u.dimensionless_unscaled
    elif values in ["modelled", "modeled"]:
        return np.interp(mid_energies.value, att_es.value, att_values_modelled.value, left=0, right=1) << u.dimensionless_unscaled
    else:
        logging.info("`values` must be \"measured\" or \"modelled\" (or \"modeled\" for you Americans).")

# aluminized mylar attenuation
@u.quantity_input(mid_energies=u.keV)
def att_al_mylar(mid_energies, file=None):
    """Return aluminized mylar transmittance interpolated to the given energies."""
    _f = os.path.join(pathlib.Path(__file__).parent, 
                            "att-data", 
                            "thin_mylar_p3_p5_theoretical.csv") if file is None else file
    att = pandas.read_csv(_f)
    att_es, att_values = att["energy[keV]"] << u.keV, att["transmission"] << u.dimensionless_unscaled
    return np.interp(mid_energies.value, att_es.value, att_values.value, left=0, right=1) << u.dimensionless_unscaled

# OBF attenuation
@u.quantity_input(mid_energies=u.keV)
def att_obf0(mid_energies, file=None):
    """Return OBF0 transmittance interpolated to the given energies."""
    logging.warning("This might not be the function you are looking for, please see `att_cmos_obfilter`.")
    _f = os.path.join(pathlib.Path(__file__).parent, 
                            "att-data", 
                            "CMOST_Prefilter_transmission.dat") if file is None else file
    att = scipy.io.readsav(_f)
    att_es, att_values = att["cmos_prefilter_transmission"]["energy_kev"][0], att["cmos_prefilter_transmission"]["position0"][0]

    # this attenuation acts weird because it stops noticably above 0 at 1 keV (the lower energy), so...
    # assume same drop-off as OBF1
    _obf1_numbers = att_obf1(mid_energies, file=None).value
    _ex_obf0_inds = np.nonzero(_obf1_numbers<att_values[0])
    _energy_ext = mid_energies[_ex_obf0_inds].value
    att_es = np.concatenate((_energy_ext-np.max(_energy_ext)+att_es[0], att_es)) << u.keV
    att_values = np.concatenate((_obf1_numbers[_ex_obf0_inds], att_values)) << u.dimensionless_unscaled

    return np.interp(mid_energies.value, att_es.value, att_values.value, left=0, right=1) << u.dimensionless_unscaled
    
# OBF attenuation
@u.quantity_input(mid_energies=u.keV)
def att_obf1(mid_energies, file=None):
    """Return OBF1 transmittance interpolated to the given energies."""
    logging.warning("This might not be the function you are looking for, please see `att_cmos_obfilter`.")
    _f = os.path.join(pathlib.Path(__file__).parent, 
                            "att-data", 
                            "CMOST_Prefilter_transmission.dat") if file is None else file
    att = scipy.io.readsav(_f)
    att_es, att_values = att["cmos_prefilter_transmission"]["energy_kev"][0] << u.keV, att["cmos_prefilter_transmission"]["position1"][0] << u.dimensionless_unscaled
    return np.interp(mid_energies.value, att_es.value, att_values.value, left=0, right=1) << u.dimensionless_unscaled

@u.quantity_input(mid_energies=u.keV)
def att_sigmoid(mid_energies, l ,x0, k, b):
    """Sigmoid model for a general/fake attenuator."""
    return (l / (1 + np.exp(-k*(mid_energies.value-x0))) + b) << u.dimensionless_unscaled

@u.quantity_input(mid_energies=u.keV)
def att_cmos_filter(mid_energies, file=None, telescope=None):
    if telescope is None:
        logging.warning("`telescope` input in `att_cmos_filter()` must be 0 or 1.")
        return
    _f = os.path.join(pathlib.Path(__file__).parent, 
                            "att-data", 
                            f"foxsi4_telescope-{telescope}_BASIC_attenuation_filter_transmittance_V25APR13.fits") if file is None else file
    with fits.open(_f) as hdul:
        es, t = hdul[2].data << u.keV, hdul[1].data << u.dimensionless_unscaled
    return np.interp(mid_energies.value, es.value, t.value, left=0, right=1) << u.dimensionless_unscaled

@u.quantity_input(mid_energies=u.keV)
def att_cmos_obfilter(mid_energies, file=None, telescope=None):
    if telescope is None:
        logging.warning("`telescope` input in `att_cmos_obfilter()` must be 0 or 1.")
        return
    _f = os.path.join(pathlib.Path(__file__).parent, 
                            "att-data", 
                            f"foxsi4_telescope-{telescope}_BASIC_optical_blocking_filter_transmittance_V25APR13.fits") if file is None else file
    with fits.open(_f) as hdul:
        es, t = hdul[2].data << u.keV, hdul[1].data << u.dimensionless_unscaled
    return np.interp(mid_energies.value, es.value, t.value, left=0, right=1) << u.dimensionless_unscaled

@u.quantity_input(off_axis_angle=u.arcsec)
def att_cmos_collimator_ratio(off_axis_angle, file=None, telescope=None):
    if telescope is None:
        logging.warning("`telescope` input in `att_cmos_collimator_ratio()` must be 0 or 1.")
        return
    _f = os.path.join(pathlib.Path(__file__).parent, 
                            "att-data", 
                            f"foxsi4_telescope-{telescope}_BASIC_collimator_aperture_ratio_V25APR13.fits") if file is None else file
    with fits.open(_f) as hdul:
        oa_angles, aperture_ratio = hdul[2].data << u.arcsec, hdul[1].data << u.dimensionless_unscaled
    return np.interp(off_axis_angle.value, oa_angles.value, aperture_ratio.value, left=0, right=0) << u.dimensionless_unscaled

if __name__=="__main__":
    import matplotlib.pyplot as plt

    from phot_spec import create_energy_midpoints, zeroes2nans

    SAVE_ASSETS = False
    assets_dir = os.path.join(pathlib.Path(__file__).parent, "..", "..", "assets", "response-tools-py-figs", "att-figs")
    pathlib.Path(assets_dir).mkdir(parents=True, exist_ok=True)

    mid_energies = create_energy_midpoints()

    tb_col, obf0_col, obf1_col, cdte_fixed2_col, cdte_fixed4_col = plt.cm.viridis([0, 0.2, 0.4, 0.6, 0.8])
    pix_att_meas_col, pix_att_mod_col, al_mylar_mod_col, cmost0_col, cmost1_col = plt.cm.plasma([0, 0.2, 0.4, 0.6, 0.8])
    cmost2_col, cmost3_col = plt.cm.cividis([0.1, 0.9])

    # all attenuators
    plt.figure(figsize=(10,8))
    att_therm_bl = zeroes2nans(att_thermal_blanket(mid_energies))
    plt.ylabel(f"Transmission [{att_therm_bl.unit:latex}]")
    plt.xlabel(f"Energy [{mid_energies.unit:latex}]")
    p1 = plt.plot(mid_energies, att_therm_bl, color=tb_col, ls="-", label="Thermal blanket")

    obf0 = zeroes2nans(att_obf0(mid_energies))
    p2 = plt.plot(mid_energies, obf0, color=obf0_col, ls="--", label="OBF0", lw=3)

    obf1 = zeroes2nans(att_obf1(mid_energies))
    p3 = plt.plot(mid_energies, obf1, color=obf1_col, ls="-.", label="OBF1", lw=3)

    cdte_fixed4 = zeroes2nans(att_uniform_al_cdte(mid_energies, position=4))
    p4 = plt.plot(mid_energies, cdte_fixed4, color=cdte_fixed4_col, ls="-.", label="CdTe fixed p4")

    cdte_fixed2 = zeroes2nans(att_uniform_al_cdte(mid_energies, position=2))
    p5 = plt.plot(mid_energies, cdte_fixed2, color=cdte_fixed2_col, ls="-.", label="CdTe fixed p2")

    pix_att_meas = zeroes2nans(att_pixelated(mid_energies, values="measured"))
    p6 = plt.plot(mid_energies, pix_att_meas, color=pix_att_meas_col, ls="--", label="Pix. Att. Measured")

    pix_att_mod = zeroes2nans(att_pixelated(mid_energies, values="modelled"))
    p7 = plt.plot(mid_energies, pix_att_mod, color=pix_att_mod_col, ls="--", label="Pix. Att. Modelled")

    al_mylar_mod = zeroes2nans(att_al_mylar(mid_energies))
    p8 = plt.plot(mid_energies, al_mylar_mod, color=al_mylar_mod_col, ls="-", label="Al-Mylar")

    cmos_t0 = att_cmos_filter(mid_energies, telescope=0)
    p9 = plt.plot(mid_energies, cmos_t0, color=cmost0_col, ls="-", label="CMOS0-filter", lw=2)

    cmos_t1 = att_cmos_filter(mid_energies, telescope=1)
    p10 = plt.plot(mid_energies, cmos_t1, color=cmost1_col, ls="-.", label="CMOS1-filter", lw=2)

    cmos_t2 = att_cmos_obfilter(mid_energies, telescope=0)
    p11 = plt.plot(mid_energies, cmos_t2, color=cmost2_col, ls="--", label="CMOS0-OBF", lw=1)

    cmos_t3 = att_cmos_obfilter(mid_energies, telescope=1)
    p12 = plt.plot(mid_energies, cmos_t3, color=cmost3_col, ls=":", label="CMOS1-OBF", lw=1)

    plt.ylim([0,1.05])
    plt.xlim([0.5, 100])
    plt.xscale("log")

    plt.title("Attenuators")
    
    plt.legend(handles=p1+p2+p3+p4+p5+p6+p7+p8+p9+p10+p11+p12)
    plt.tight_layout()
    if SAVE_ASSETS:
        plt.savefig(os.path.join(assets_dir,"transmissions.png"), dpi=200, bbox_inches="tight")
    plt.show()

    ## other
    # collimator (so far, only have value for on-axis)
    print(att_cmos_collimator_ratio(0<<u.arcsec, file=None, telescope=0))
    print(att_cmos_collimator_ratio(0<<u.arcsec, file=None, telescope=1))

    # any fake/functionaly model attenuators
    # sigmoid
    l ,x0, k, b = 1, 0, 1, 0
    example = att_sigmoid(mid_energies, l ,x0, k, b)
    p1 = plt.plot(mid_energies, example, ls="-", label=f"l:{l} ,x0:{x0}, k:{k}, b:{b}")
    l ,x0, k, b = 1.04, 0, 1, 0
    p2 = plt.plot(mid_energies, att_sigmoid(mid_energies, l, x0, k, b), ls="-", label=f"l:{l} ,x0:{x0}, k:{k}, b:{b}")
    l ,x0, k, b = 1, 3, 1, 0
    p3 = plt.plot(mid_energies, att_sigmoid(mid_energies, l, x0, k, b), ls="-", label=f"l:{l} ,x0:{x0}, k:{k}, b:{b}")
    l ,x0, k, b = 1, 3, 1, 0.04
    p4 = plt.plot(mid_energies, att_sigmoid(mid_energies, l, x0, k, b), ls="-", label=f"l:{l} ,x0:{x0}, k:{k}, b:{b}")
    l ,x0, k, b = 1, 10, 0.5, 0
    p5 = plt.plot(mid_energies, att_sigmoid(mid_energies, l, x0, k, b), ls="-", label=f"l:{l} ,x0:{x0}, k:{k}, b:{b}")
    l ,x0, k, b = 1, 10, 1, 0
    p6 = plt.plot(mid_energies, att_sigmoid(mid_energies, l, x0, k, b), ls="-", label=f"l:{l} ,x0:{x0}, k:{k}, b:{b}")
    l ,x0, k, b = 1, 10, 2, 0
    p7 = plt.plot(mid_energies, att_sigmoid(mid_energies, l, x0, k, b), ls="-", label=f"l:{l} ,x0:{x0}, k:{k}, b:{b}")
    l ,x0, k, b = 1, 25, 1, 0
    p8 = plt.plot(mid_energies, att_sigmoid(mid_energies, l, x0, k, b), ls="-", label=f"spectrometer-like:\nl:{l} ,x0:{x0}, k:{k}, b:{b}")

    plt.ylabel(f"Transmission [{example.unit:latex}]")
    plt.xlabel(f"Energy [{mid_energies.unit:latex}]")
    plt.title("Fake Attenuator, Sigmoid$=l/(1+exp^{-k*(x-x0)})+b")
    plt.ylim([0,1.05])
    plt.xlim([0.5, 100])
    plt.xscale("log")

    plt.legend(handles=p1+p2+p3+p4+p5+p6+p7+p8)
    plt.tight_layout()
    if SAVE_ASSETS:
        plt.savefig(os.path.join(assets_dir,"model-transmissions.png"), dpi=200, bbox_inches="tight")
    plt.show()