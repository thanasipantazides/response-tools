"""Code to load different attenuators. """

import logging
import os
import pathlib
import sys
import warnings

from astropy.io import fits
import astropy.units as u
import numpy as np
import pandas
import scipy

from response_tools_py.util import native_resolution

ATT_PATH = os.path.join(pathlib.Path(__file__).parent, "..", "..", "response-information", "attenuation-data")
ATM_PATH = os.path.join(pathlib.Path(__file__).parent, "..", "..", "response-information", "atmospheric-data")
ASSETS_PATH = os.path.join(pathlib.Path(__file__).parent, "..", "..", "assets", "response-tools-py-figs", "att-figs")

# thermal blanket attenuation
@u.quantity_input(mid_energies=u.keV)
def att_thermal_blanket(mid_energies, file=None):
    """Return thermal blanket transmittance interpolated to the given energies."""
    _f = os.path.join(ATT_PATH, "F4_Blanket_transmission_v1.dat") if file is None else file
    att = scipy.io.readsav(_f)
    att_es, att_values = att["energy_kev"] << u.keV, att["f4_transmission"] << u.dimensionless_unscaled
    return np.interp(mid_energies.value, att_es.value, att_values.value, left=0, right=1) << u.dimensionless_unscaled

# thermal blanket attenuation
@u.quantity_input(mid_energies=u.keV)
def att_uniform_al_cdte(mid_energies, file=None, position=None):
    """Return thermal blanket transmittance interpolated to the given energies."""
    if position is None:
        logging.info("`position` must be 2 or 4.")
    _f = os.path.join(ATT_PATH, f"unif_att_p{position}_theoretical_v1.csv") if file is None else file
    att = pandas.read_csv(_f)
    att_es, att_values = att["energy[keV]"] << u.keV, att["transmission"] << u.dimensionless_unscaled
    return np.interp(mid_energies.value, att_es.value, att_values.value, left=0, right=1) << u.dimensionless_unscaled

# pixelated attenuator attenuation
@u.quantity_input(mid_energies=u.keV)
def att_pixelated(mid_energies, file=None, values=None):
    """Return pixelated attenuator transmittance interpolated to the given energies."""
    _f = os.path.join(ATT_PATH, "20240607_fosxi4_transmission_v1.csv") if file is None else file
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
    _f = os.path.join(ATT_PATH, "thin_mylar_p3_p5_theoretical_v1.csv") if file is None else file
    att = pandas.read_csv(_f)
    att_es, att_values = att["energy[keV]"] << u.keV, att["transmission"] << u.dimensionless_unscaled
    return np.interp(mid_energies.value, att_es.value, att_values.value, left=0, right=1) << u.dimensionless_unscaled

# pre-filter attenuation
@u.quantity_input(mid_energies=u.keV)
def _att_old_prefilter0(mid_energies, file=None):
    """Return pre-filter 0 transmittance interpolated to the given energies.
    
    This function was used for simulations pre-launch.
    """
    logging.warning("This might not be the function you are looking for, please see `att_cmos_obfilter`.")
    _f = os.path.join(ATT_PATH, "CMOST_Prefilter_transmission.dat") if file is None else file
    att = scipy.io.readsav(_f)
    att_es, att_values = att["cmos_prefilter_transmission"]["energy_kev"][0], att["cmos_prefilter_transmission"]["position0"][0]

    # this attenuation acts weird because it stops noticably above 0 at 1 keV (the lower energy), so...
    # assume same drop-off as pre-filter1
    _obf1_numbers = _att_old_prefilter1(mid_energies, file=None).value
    _ex_obf0_inds = np.nonzero(_obf1_numbers<att_values[0])
    _energy_ext = mid_energies[_ex_obf0_inds].value
    att_es = np.concatenate((_energy_ext-np.max(_energy_ext)+att_es[0], att_es)) << u.keV
    att_values = np.concatenate((_obf1_numbers[_ex_obf0_inds], att_values)) << u.dimensionless_unscaled

    return np.interp(mid_energies.value, att_es.value, att_values.value, left=0, right=1) << u.dimensionless_unscaled
    
# pre-filter attenuation
@u.quantity_input(mid_energies=u.keV)
def _att_old_prefilter1(mid_energies, file=None):
    """Return pre-filter 1 transmittance interpolated to the given energies.
    
    This function was used for simulations pre-launch.
    """
    logging.warning("Caution: This might not be the function you are looking for, please see `att_cmos_obfilter`.")
    _f = os.path.join(ATT_PATH, "CMOST_Prefilter_transmission.dat") if file is None else file
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
    _f = os.path.join(ATT_PATH, f"foxsi4_telescope-{telescope}_BASIC_attenuation_filter_transmittance_v1.fits") if file is None else file
    with fits.open(_f) as hdul:
        es, t = hdul[2].data << u.keV, hdul[1].data << u.dimensionless_unscaled
    return np.interp(mid_energies.value, es.value, t.value, left=0, right=1) << u.dimensionless_unscaled

@u.quantity_input(mid_energies=u.keV)
def att_cmos_obfilter(mid_energies, file=None, telescope=None):
    if telescope is None:
        logging.warning("`telescope` input in `att_cmos_obfilter()` must be 0 or 1.")
        return
    _f = os.path.join(ATT_PATH, f"foxsi4_telescope-{telescope}_BASIC_optical_blocking_filter_transmittance_v1.fits") if file is None else file
    with fits.open(_f) as hdul:
        es, t = hdul[2].data << u.keV, hdul[1].data << u.dimensionless_unscaled
    return np.interp(mid_energies.value, es.value, t.value, left=0, right=1) << u.dimensionless_unscaled

@u.quantity_input(off_axis_angle=u.arcsec)
def att_cmos_collimator_ratio(off_axis_angle, file=None, telescope=None):
    if telescope is None:
        logging.warning("`telescope` input in `att_cmos_collimator_ratio()` must be 0 or 1.")
        return
    _f = os.path.join(ATT_PATH, f"foxsi4_telescope-{telescope}_BASIC_collimator_aperture_ratio_v1.fits") if file is None else file
    with fits.open(_f) as hdul:
        oa_angles, aperture_ratio = hdul[2].data << u.arcsec, hdul[1].data << u.dimensionless_unscaled
    return np.interp(off_axis_angle.value, oa_angles.value, aperture_ratio.value, left=0, right=0) << u.dimensionless_unscaled

@u.quantity_input(mid_energies=u.keV, time=u.second)
def att_atmosphere(mid_energies, time_range=None, file=None):
    """ 
    Atmsopheric attenuation from and for FOXSI-4 flight data.

    energy = array containing energy in keV for energies 0.01 - 30 keV. Array has 506 elements
		 
    atmospheric_trans = array containing transmission for all energy values in energy array.
                        Transmission is calculated for 10284 times covering the FOXSI-4 flight. 
                        Array shape is: [10284,506] which corresponds to transmission for [time,energy]
                        
                        Launch time t = 0 corresponds to  index [0,*] 
                        Observation starts at t = 100s corresponds to index [2000,*]
                        Approximate middle of observation at t = 280s corresponds to index [5600,*]
                        End of observation at t = 461s corresponds to index [9200,*] 


    Units in the FITS header needs to change from keV->eV
    Need an array of times included
    -> 10,284 entries and t=0 is index `0` while t=100 is index `2000`
    -> final time is 100/2000 * 10284 = 514.2

    Parameters
    ----------
    mid_energies 

    time_range
    
    file: `str` or `None`
    """
    if (time_range is None) or np.all(np.isnan(time_range)):
        time_range = [np.nan, np.nan] << u.second
    
    if (len(time_range)!=2):
        warnings.warn(f"{sys._getframe().f_code.co_name} `time_range` (convertable to astropy.units.seconds) should be of length 2.")
        return

    _f = os.path.join(ATM_PATH, f"FOXSI4_atmospheric_transmission_v1.fits") if file is None else file
    with fits.open(_f) as hdul:
        native_energies, transmission = (hdul[1].data[0][0]<<u.eV)<<u.keV, hdul[1].data[0][1]<<u.dimensionless_unscaled
        # Need an array of times included
        # -> 10,284 entries and t=0 is index `0` while t=100 is index `2000`
        # -> final time is 100/2000 * 10284 = 514.2
        native_times = np.linspace(0, 514.2, 10_284)<<u.second

        # assume some sort of uniform uniform binning
        en_res = np.mean(np.diff(native_energies))

    # if the time range is nothing them just want all the times, deal with energies separately
    if np.all(np.isnan(time_range)):
        if np.all(np.isnan(mid_energies)):
            # don't bother going further if we're just going to return the native data
            return native_energies<<u.keV, native_times, transmission
        
        # the grid can be huge so let's help cut down on the interpolation amount
        cut_native_energies_inds = np.nonzero(((mid_energies[0]-en_res)<=native_energies) & (native_energies<=(mid_energies[-1]+en_res)))
        cut_native_energies = native_energies[cut_native_energies_inds]
        cut_transmission = transmission[cut_native_energies_inds]

        x, y = np.meshgrid(cut_native_energies, native_times)
        i = scipy.interpolate.LinearNDInterpolator(list(zip(x.flatten().value, y.flatten().value)), cut_transmission.T.flatten().value)

        mid_energies = native_resolution(native_x=native_energies, input_x=mid_energies)
        all_times = native_resolution(native_x=native_times, input_x=time_range)
        X, Y = np.meshgrid(mid_energies, all_times)

        return mid_energies, all_times, i(X, Y)<<u.dimensionless_unscaled

    # this is a big array so let's slice before interpolating
    time_inds = np.nonzero((time_range[0]<=native_times) & (native_times<=time_range[1]))[0]

    mid_energies = native_resolution(native_x=native_energies, input_x=mid_energies)
    # energy_inds = np.nonzero((mid_energies[0]<=native_energies) & (native_energies<=mid_energies[-1]))[0]

    # # we'll interpolate so make sure to include a range one wider for the energy range
    # energy_inds = np.insert(energy_inds, 0, energy_inds[0]-1) if energy_inds[0]>0 else energy_inds
    # energy_inds = np.insert(energy_inds, 1, energy_inds[-1]+1) if energy_inds[-1]<(len(energy_inds)-1) else energy_inds

    times = native_times[time_inds]
    transmissions = transmission[:,time_inds]

    tave_transmissions = np.mean(transmissions, axis=1)

    return mid_energies<<u.keV, times, np.interp(mid_energies.value, native_energies.value, tave_transmissions.value, left=0, right=0) << u.dimensionless_unscaled

def asset_att(save_asset=False):
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

    old_prefilter0 = zeroes2nans(_att_old_prefilter0(mid_energies))
    p2 = plt.plot(mid_energies, old_prefilter0, color=obf0_col, ls="--", label="Old pre-filter 0", lw=3)

    old_prefilter1 = zeroes2nans(_att_old_prefilter1(mid_energies))
    p3 = plt.plot(mid_energies, old_prefilter1, color=obf1_col, ls="-.", label="Old pre-filter 1", lw=3)

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
    if save_asset:
        pathlib.Path(ASSETS_PATH).mkdir(parents=True, exist_ok=True)
        plt.savefig(os.path.join(ASSETS_PATH,"transmissions.png"), dpi=200, bbox_inches="tight")
    plt.show()

def asset_sigmoid(save_asset=False):
    mid_energies = create_energy_midpoints()

    plt.figure(figsize=(10,8))

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
    if save_asset:
        pathlib.Path(ASSETS_PATH).mkdir(parents=True, exist_ok=True)
        plt.savefig(os.path.join(ASSETS_PATH,"model-transmissions.png"), dpi=200, bbox_inches="tight")
    plt.show()

def asset_atm(save_asset=False):
    fig = plt.figure(figsize=(10,5))

    obs_start = 100
    obs_mid = 280
    obs_end = 461

    gs = gridspec.GridSpec(1, 2)

    gs_ax0 = fig.add_subplot(gs[0, 0])

    energy0, time0 = [1]<<u.keV, np.nan<<u.second
    _, t0, a0 = att_atmosphere(mid_energies=energy0, time_range=time0)
    p0 = gs_ax0.plot(t0, a0, ls="-", label=f"energy:{energy0:latex} ,time:{time0:latex}")

    energy1, time1 = [1, 3, 5, 10, 15]<<u.keV, np.nan<<u.second
    _, t1, a1 = att_atmosphere(mid_energies=energy1, time_range=time1)
    p1 = []
    for i in range(len(energy1)):
        p1 += gs_ax0.plot(t1, a1[:,i], ls=":", label=f"energy:{energy1[i]:latex}")

    gs_ax0.set_ylabel(f"Transmission [{a0.unit:latex}]")
    gs_ax0.set_xlabel(f"Time (Obs. start=100 s) [{t0.unit:latex}]")
    gs_ax0.set_ylim([0,1.05])
    gs_ax0.axvline(obs_start, ls=":")
    gs_ax0.axvline(obs_mid, ls=":")
    gs_ax0.axvline(obs_end, ls=":")
    gs_ax0.set_xlim([0, 600])
    # plt.xscale("log")

    plt.legend(handles=p0+p1)
    
    gs_ax1 = fig.add_subplot(gs[0, 1])

    energy2, time2 = np.nan<<u.keV, [obs_start, obs_end]<<u.second
    e2, _, a2 = att_atmosphere(mid_energies=energy2, time_range=time2)
    p2 = gs_ax1.plot(e2, a2, ls="-", label=f"time:{time2:latex}")

    energy3, time3 = np.nan<<u.keV, np.nan<<u.second
    e3, t3, a3 = att_atmosphere(mid_energies=energy3, time_range=time3)
    # print(t3)
    # st, mid, en = np.nonzero(t3==obs_start), np.nonzero(t3==obs_mid), np.nonzero(t3==obs_end)
    p3 = gs_ax1.plot(e3, a3[:, 2000], ls="-", label=f"time:{t3[2000]:latex}")
    p4 = gs_ax1.plot(e3, a3[:, 5600], ls="-", label=f"time:{t3[5600]:latex}")
    p5 = gs_ax1.plot(e3, a3[:, 9200], ls="-", label=f"time:{t3[9200]:latex}")

    gs_ax1.set_ylabel(f"Transmission [{a2.unit:latex}]")
    gs_ax1.set_xlabel(f"Energy [{e2.unit:latex}]")
    gs_ax1.set_ylim([0,1.05])
    gs_ax1.set_xlim([1, 25])
    gs_ax1.set_xscale("log")

    plt.legend(handles=p2+p3+p4+p5)

    plt.tight_layout()
    if save_asset:
        pathlib.Path(ASSETS_PATH).mkdir(parents=True, exist_ok=True)
        plt.savefig(os.path.join(ASSETS_PATH,"atmospheric-transmissions.png"), dpi=200, bbox_inches="tight")
    plt.show()

if __name__=="__main__":
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec

    from phot_spec import create_energy_midpoints, zeroes2nans

    mid_energies = create_energy_midpoints()
    # e0, t0, a0 = att_atmosphere(mid_energies=np.nan<<u.keV, time_range=None, file=None)
    # e1, t1, a1 = att_atmosphere(mid_energies=np.nan<<u.keV, time_range=np.nan<<u.second, file=None)
    # e2, t2, a2 = att_atmosphere(mid_energies=[1, 4, 6]<<u.keV, time_range=[100, 150]<<u.second, file=None)
    # e3, t3, a3 = att_atmosphere(mid_energies=np.nan<<u.keV, time_range=[100, 150]<<u.second, file=None)
    # exit()
    SAVE_ASSETS = False
    
    # asset_att(save_asset=SAVE_ASSETS)
    
    # ## other
    # # collimator (so far, only have value for on-axis)
    # print(att_cmos_collimator_ratio(0<<u.arcsec, file=None, telescope=0))
    # print(att_cmos_collimator_ratio(0<<u.arcsec, file=None, telescope=1))

    # asset_sigmoid(save_asset=SAVE_ASSETS)

    asset_atm(save_asset=SAVE_ASSETS)