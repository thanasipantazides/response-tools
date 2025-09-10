"""Code to load different effective areas. """

import logging
import os
import pathlib

from astropy.io import fits
import astropy.units as u
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import CloughTocher2DInterpolator, LinearNDInterpolator 
import pandas

from response_tools_py.util import native_resolution

EFF_PATH = os.path.join(pathlib.Path(__file__).parent, "..", "..", "response-information", "effective-area-data")
ASSETS_PATH = os.path.join(pathlib.Path(__file__).parent, "..", "..", "assets", "response-tools-py-figs", "eff-area-figs")

@u.quantity_input(mid_energies=u.keV, off_axis=u.arcmin)
def eff_area_msfc_10shell(mid_energies, off_axis=0, file_tilt=None, file_pan=None, optic_id=None):
    """ 
    Tilt is the off-axis angle when the optics up coincides with Solar North (“vertical”). Pan is the other angle (“horizontal”).
    """
    _id = optic_id if optic_id in ["X-7", "X-8"] else None
    if _id is None:
        logging.warning("Please provide a MSFC heritage optic ID from [\'X-7\', \'X-8\'].")
        
    vals_tilt = _get_ea_file_info(_id, "tilt", file=file_tilt)
    vals_pan = _get_ea_file_info(_id, "pan", file=file_pan)

    # from Milo on 17/3/2025 @ 13:47 (Slack)
    ea_energies = [4.5,  5.5,  6.5,  7.5,  8.5,  9.5, 11. , 13. , 15. , 17. , 19. , 22.5, 27.5] << u.keV

    off_axis_angles_tilt, eff_areas_tilt = _get_oa_and_ea_msfc_10shell(vals_tilt)
    _, eff_areas_pan = _get_oa_and_ea_msfc_10shell(vals_pan)

    mean_eff_areas_areas = (eff_areas_tilt+eff_areas_pan)/2

    x, y = np.meshgrid(ea_energies, off_axis_angles_tilt)
    i = CloughTocher2DInterpolator(list(zip(x.flatten().value, y.flatten().value)), mean_eff_areas_areas.T.flatten().value)

    mid_energies = native_resolution(native_x=ea_energies, input_x=mid_energies)
    off_axis = native_resolution(native_x=off_axis_angles_tilt, input_x=off_axis)

    return mid_energies, off_axis, i(mid_energies, off_axis) << u.cm**2

def _get_ea_file_info(optics_id, axis, file=None):
    _f = os.path.join(EFF_PATH, f"FOXSI3_Module_{optics_id}_EA_{axis}_v1.txt") if file is None else file
    return np.loadtxt(_f, delimiter=",")

def _get_oa_and_ea_msfc_10shell(grid):
    off_axis_angles = grid[0]
    eff_areas = grid[1:]
    return off_axis_angles << u.arcmin, eff_areas << u.cm**2

@u.quantity_input(mid_energies=u.keV)
def eff_area_msfc_hi_res(mid_energies, file=None, position=None, use_model=False):
    """Return MSCF hi-res effective areas interpolated to the given energies.
    
    Latest from Wayne.
    - older function is `eff_area_msfc`
    
    Position 0: X10/FM2
    Position 3: X09/FM1
    Position 6: X11/FM3
    """
    # msfc_hi_res effective areas
    _f = os.path.join(EFF_PATH, "FOXSI4_Module_MSFC_HiRes_EA_with_models_v1.txt") if file is None else file
    e, f1, f2, f3, f1_m, f2_m, f3_m = np.loadtxt(_f).T

    fm1, fm2, fm3 = (f1_m, f2_m, f3_m) if use_model else (f1, f2, f3)

    e <<= u.keV
    mid_energies = native_resolution(native_x=e, input_x=mid_energies)

    fm1 <<= u.cm**2
    fm2 <<= u.cm**2
    fm3 <<= u.cm**2
    if position==0:
        return mid_energies, np.interp(mid_energies.value, e.value, fm2.value, left=fm2.value[0], right=0) << u.cm**2
    elif position==3:
        return mid_energies, np.interp(mid_energies.value, e.value, fm1.value, left=fm1.value[0], right=0) << u.cm**2
    elif position==6:
        return mid_energies, np.interp(mid_energies.value, e.value, fm3.value, left=fm3.value[0], right=0) << u.cm**2
    else:
        logging.warning("`position` must be 0 (X10/FM2), 3 (X09/FM1), or 6 (X11/FM3).")

@u.quantity_input(mid_energies=u.keV)
def eff_area_msfc(mid_energies, file=None):
    """Return early MSCF hi-res effective areas interpolated to the given energies."""
    # msfc_hi_res effective areas
    logging.warning("Caution: This might not be the function you are looking for, please see `eff_area_msfc_hi_res`.")
    logging.warning("This current function loads in some very early numbers for the new FOXSI-4 MSFC optics.")
    _f = os.path.join(EFF_PATH, "3Inner_EA_EPDL97_14AA.csv") if file is None else file
    msfc_hi_res = pandas.read_csv(_f).to_numpy()[:,1:] # remove the first column that only indexes
    # in cm2 ; we use the innermost and the 3rd innermost shells (S10 and S08) [from Yixian]
    msfc_hi_res_es, msfc_hi_res_effas08, msfc_hi_res_effas10 = msfc_hi_res[:,0] << u.keV, msfc_hi_res[:,1] << u.cm**2, msfc_hi_res[:,3] << u.cm**2 
    msfc_hi_res_effa = msfc_hi_res_effas08 + msfc_hi_res_effas10

    mid_energies = native_resolution(native_x=msfc_hi_res_es, input_x=mid_energies)
    return mid_energies, np.interp(mid_energies.value, msfc_hi_res_es.value, msfc_hi_res_effa.value, left=msfc_hi_res_effa.value[0], right=0) << u.cm**2

@u.quantity_input(mid_energies=u.keV)
def eff_area_nagoya(mid_energies, file=None):
    """Return early Nagoya SXR hi-res effective areas interpolated to the given energies."""
    # nagoya sxr effective areas
    logging.warning("Caution: This might not be the function you are looking for and has other effects included than just optics.")
    logging.warning("This current function loads in some very early numbers for the new FOXSI-4 Nagoya SXR optics.")
    _f = os.path.join(EFF_PATH, "effective-area_raytracing_soft-xray-optic_on-axis.txt") if file is None else file
    nagoya_sxr = np.loadtxt(_f)
    nagoya_sxr_es, nagoya_sxr_effa = nagoya_sxr[:,0] << u.keV, nagoya_sxr[:,1]/100 << u.cm**2

    mid_energies = native_resolution(native_x=nagoya_sxr_es, input_x=mid_energies)
    return mid_energies, np.interp(mid_energies.value, nagoya_sxr_es.value, nagoya_sxr_effa.value, left=0, right=0) << u.cm**2

@u.quantity_input(mid_energies=u.keV)
def eff_area_nagoya_hxt(mid_energies, file=None, use_model=False):
    """Return Nagoya HXR hi-res effective areas (measured) interpolated to the given energies."""
    # nagoya hxr effective areas
    if not use_model:
        _f = os.path.join(EFF_PATH, "nagoya_hxt_onaxis_measurement_v1.txt") if file is None else file
        nagoya_hxr = np.loadtxt(_f)
        nagoya_hxr_es, _, nagoya_hxr_effa, _ = nagoya_hxr[:,0] << u.keV, nagoya_hxr[:,1] << u.keV, nagoya_hxr[:,2] << u.mm**2, nagoya_hxr[:,3] << u.mm**2
        nagoya_hxr_effa = nagoya_hxr_effa << u.cm**2
    else:
        _f = os.path.join(EFF_PATH, "HXR_Nagoya_FOXSI4.arf") if file is None else file
        with fits.open(_f) as hdul:
            nagoya_hxr_es = (hdul[1].data["ENERG_LO"]+hdul[1].data["ENERG_HI"])/2 << u.keV
            nagoya_hxr_effa = hdul[1].data["SPECRESP"] << u.cm**2
    
    mid_energies = native_resolution(native_x=nagoya_hxr_es, input_x=mid_energies)
    return mid_energies, np.interp(mid_energies.value, nagoya_hxr_es.value, nagoya_hxr_effa.value, left=0, right=0) << u.cm**2

@u.quantity_input(mid_energies=u.keV)
def eff_area_nagoya_sxt(mid_energies, file=None, use_model=False):
    """Return Nagoya SXR hi-res effective areas (measured) interpolated to the given energies.
    
    Includes the collimator and OBF too.
    """
    # nagoya sxr effective areas
    if not use_model:
        _f = os.path.join(EFF_PATH, "nagoya_sxt_onaxis_measurement_v1.txt") if file is None else file
        nagoya_sxr = np.loadtxt(_f)
        nagoya_sxr_es, _, nagoya_sxr_effa, _ = nagoya_sxr[:,0] << u.keV, nagoya_sxr[:,1] << u.keV, nagoya_sxr[:,2] << u.mm**2, nagoya_sxr[:,3] << u.mm**2
        nagoya_sxr_effa = nagoya_sxr_effa << u.cm**2
    else:
        _f = os.path.join(EFF_PATH, "SXR_nocollimator_noobf.arf") if file is None else file
        with fits.open(_f) as hdul:
            nagoya_sxr_es = (hdul[1].data["ENERG_LO"]+hdul[1].data["ENERG_HI"])/2 << u.keV
            nagoya_sxr_effa = hdul[1].data["SPECRESP"] << u.cm**2
    
    mid_energies = native_resolution(native_x=nagoya_sxr_es, input_x=mid_energies)
    return mid_energies, np.interp(mid_energies.value, nagoya_sxr_es.value, nagoya_sxr_effa.value, left=0, right=0) << u.cm**2

@u.quantity_input(mid_energies=u.keV)
def eff_area_cmos(mid_energies, file=None, telescope=None):
    """Return optics paired with CMOS effective areas interpolated to 
    the given energies.
    
    Telescope 0: position 0, X10/FM2(?)
    Telescope 1: position 1, Nagoya(?)
    """
    if telescope is None:
        logging.warning("`telescope` input in `eff_area_cmos()` must be 0 or 1.")
        return
        
    _f = os.path.join(EFF_PATH, f"foxsi4_telescope-{telescope}_BASIC_mirror_effective_area_v1.fits") if file is None else file
    with fits.open(_f) as hdul:
        es, effas = hdul[2].data << u.keV, hdul[1].data << u.cm**2
    mid_energies = native_resolution(native_x=es, input_x=mid_energies)
    return mid_energies, np.interp(mid_energies.value, es.value, effas.value, left=0, right=0) << u.cm**2

@u.quantity_input(mid_energies=u.keV)
def eff_area_cmos_telescope(mid_energies, file=None, telescope=None):
    """Return full telescope(?) with CMOS effective areas interpolated to 
    the given energies.
    
    Telescope 0: position 0, X10/FM2(?)
    Telescope 1: position 1, Nagoya(?)

    **Note**
    Will come back to this when there are off-axis angles and do 2D 
    interp. Currently only on-axis angle so just interp across energies.
    """
    if telescope is None:
        logging.warning("`telescope` input in `eff_area_cmos_telescope()` must be 0 or 1.")
        return
    
    # not tracking this combined response product
    logging.warning("Caution: This output will include a combined response from various elements.")
    logging.warning("If you care about what elements are included then proceed carefully.")
    logging.warning("For current file, see PR#11 in the `cmos-tools` repository.")

    _f = os.path.join(EFF_PATH, f"foxsi4_telescope-{telescope}_BASIC_TELESCOPE_RESPONSE_V25APR13.fits") if file is None else file
    with fits.open(_f) as hdul:
        # _ is the off-axis angle but it's just [0] at the minute
        ea_energies, _, effas = hdul[2].data << u.keV, hdul[3].data << u.arcsec, hdul[1].data << u.cm**2
    mid_energies = native_resolution(native_x=ea_energies, input_x=mid_energies)
    return mid_energies, np.interp(mid_energies.value, ea_energies.value, effas.value, left=0, right=0) << u.cm**2

def asset_cmos_plot(save_asset=False):
    """Plot the CMOS data to visually check."""
    mid_energies = np.linspace(0, 20, 1000)<<u.keV
    
    #cmos optics/telescopes
    fig = plt.figure(figsize=(14,7))
    gs = gridspec.GridSpec(1, 2)

    gs_ax0 = fig.add_subplot(gs[0, 0])
    _, a0 = eff_area_cmos(mid_energies, file=None, telescope=0)
    _, a1 = eff_area_cmos(mid_energies, file=None, telescope=1)
    _, msfcp0 = eff_area_msfc_hi_res(mid_energies, file=None, position=0)
    _, msfcp0m = eff_area_msfc_hi_res(mid_energies, file=None, position=0, use_model=True)
    _, nag = eff_area_nagoya_sxt(mid_energies)
    gs_ax0.plot(mid_energies, a0, label="CMOS telescope 0, position 0")
    gs_ax0.plot(mid_energies, a1, label="CMOS telescope 1, position 1")
    gs_ax0.plot(mid_energies, msfcp0, label="MSFC (meas.) position 0")
    gs_ax0.plot(mid_energies, msfcp0m, label="MSFC (mod.) position 0")
    gs_ax0.plot(mid_energies, nag, label="Nagoya (meas.) position 1")
    gs_ax0.set_title("CMOS Optics")
    gs_ax0.set_ylabel(f"Effective Area [{a0.unit:latex}]")
    gs_ax0.set_xlabel(f"Energy [{mid_energies.unit:latex}]")
    plt.legend()

    # CMOS full telescope ones
    gs_ax1 = fig.add_subplot(gs[0, 1])
    _, a0ft = eff_area_cmos_telescope(mid_energies, file=None, telescope=0)
    _, a1ft = eff_area_cmos_telescope(mid_energies, file=None, telescope=1)
    gs_ax1.plot(mid_energies, a0ft, label="CMOS telescope 0, position 0")
    gs_ax1.plot(mid_energies, a1ft, label="CMOS telescope 1, position 1")
    gs_ax1.set_title("CMOS Telescope?")
    gs_ax1.set_ylabel(f"Effective Area [{a0ft.unit:latex}]")
    gs_ax1.set_xlabel(f"Energy [{mid_energies.unit:latex}]")
    plt.legend()

    plt.tight_layout()
    if save_asset:
        pathlib.Path(ASSETS_PATH).mkdir(parents=True, exist_ok=True)
        plt.savefig(os.path.join(ASSETS_PATH,"cmos-sxr-optics-resp.png"), dpi=200, bbox_inches="tight")
    plt.show()

def asset_cmos_files(save_asset=False):
    """Plot the CMOS data to visually check."""
    mid_energies = np.linspace(0, 20, 1000)<<u.keV
    
    #cmos optics/telescopes
    fig = plt.figure(figsize=(14,7))
    gs = gridspec.GridSpec(1, 2)

    gs_ax0 = fig.add_subplot(gs[0, 0])
    _, a0 = eff_area_cmos(mid_energies, file=None, telescope=0)
    _, msfc_hi_res_p0 = eff_area_msfc_hi_res(mid_energies, position=0)
    _, msfc_hi_res_p0m = eff_area_msfc_hi_res(mid_energies, position=0, use_model=True)
    gs_ax0.plot(mid_energies, a0, label="CMOS telescope 0, position 0")
    gs_ax0.plot(mid_energies, msfc_hi_res_p0, label="MSFC (meas.), position 0")
    gs_ax0.plot(mid_energies, msfc_hi_res_p0m, label="MSFC (mod.), position 0")
    gs_ax0.set_title("CMOS SXR Optics: Position 0")
    gs_ax0.set_ylabel(f"Effective Area [{a0.unit:latex}]")
    gs_ax0.set_xlabel(f"Energy [{mid_energies.unit:latex}]")
    plt.legend()
    plt.yscale("log")

    from attenuation import att_cmos_obfilter, att_cmos_collimator_ratio

    gs_ax1 = fig.add_subplot(gs[0, 1])
    _, a1 = eff_area_cmos(mid_energies, file=None, telescope=1)
    _, nag_sxt = eff_area_nagoya_sxt(mid_energies)
    gs_ax1.plot(mid_energies, a1*att_cmos_obfilter(mid_energies, telescope=1)*att_cmos_collimator_ratio(0<<u.arcmin, telescope=1), label="CMOS telescope 1*collimator*obf, position 1")
    gs_ax1.plot(mid_energies, nag_sxt, label="Nagoya SXT (meas.) position 1")
    # gs_ax1.plot(mid_energies, a1, label="CMOS telescope 1, position 1")
    # gs_ax1.plot(mid_energies, nag_sxt/att_cmos_obfilter(mid_energies, telescope=1)/att_cmos_collimator_ratio(0<<u.arcmin, telescope=1), label="Nagoya SXT (meas.)/collimator/OBF, position 1")
    gs_ax1.set_title("CMOS SXR Optics: Position 1")
    gs_ax1.set_ylabel(f"Effective Area [{a1.unit:latex}]")
    gs_ax1.set_xlabel(f"Energy [{mid_energies.unit:latex}]")
    plt.legend()
    # plt.yscale("log")
    plt.ylim([0,0.35])

    plt.xlim([0,20])

    # print(a1)
    print(att_cmos_collimator_ratio(0<<u.arcmin, telescope=0), 1/att_cmos_collimator_ratio(0<<u.arcmin, telescope=0))

    plt.tight_layout()
    if save_asset:
        pathlib.Path(ASSETS_PATH).mkdir(parents=True, exist_ok=True)
        plt.savefig(os.path.join(ASSETS_PATH,"cmos-sxr-optics-resp.png"), dpi=200, bbox_inches="tight")
    plt.show()

def asset_all_optics(save_asset=False):
    """Produce a figure showing all optics as an assets."""
    # most optics
    fig = plt.figure(figsize=(9.5, 9.5))
    gs = gridspec.GridSpec(3, 3)

    ## OPTIC: X-7
    optic = "X-7" 

    vals_tilt = _get_ea_file_info(optic, "tilt")
    vals_pan = _get_ea_file_info(optic, "pan")
    off_axis_angles_tilt, eff_areas_tilt = _get_oa_and_ea_msfc_10shell(vals_tilt)
    off_axis_angles_pan, eff_areas_pan = _get_oa_and_ea_msfc_10shell(vals_pan)
    ea_energies = [4.5,  5.5,  6.5,  7.5,  8.5,  9.5, 11. , 13. , 15. , 17. , 19. , 22.5, 27.5] << u.keV

    off_axis_angles_tilt = off_axis_angles_tilt << u.arcmin
    off_axis_angles_pan = off_axis_angles_pan << u.arcmin

    e_i = 0
    gs_ax0 = fig.add_subplot(gs[0, 0])
    p00 = gs_ax0.plot(off_axis_angles_tilt, eff_areas_tilt[e_i], label="tilt", lw=4)
    p01 = gs_ax0.plot(off_axis_angles_pan, eff_areas_pan[e_i], label="pan")
    gs_ax0.set_title(f"@ Energy: {ea_energies[e_i]}")
    gs_ax0.set_ylabel(f"Heritage MSFC {optic} [{eff_areas_pan.unit:latex}]")
    gs_ax0.set_xlabel(f"off-axis angle [{off_axis_angles_tilt.unit:latex}]")
    plt.legend(handles=p00+p01)
    gs_ax0.set_xlim([off_axis_angles_tilt[0].value, off_axis_angles_tilt[-1].value])

    oa_i = 5
    gs_ax1 = fig.add_subplot(gs[0, 1])
    p10 = gs_ax1.plot(ea_energies, eff_areas_tilt[:,oa_i], label="tilt", lw=4)
    p11 = gs_ax1.plot(ea_energies, eff_areas_pan[:,oa_i], label="pan", lw=3)
    p12 = gs_ax1.plot(ea_energies, (eff_areas_pan[:,oa_i]+eff_areas_tilt[:,oa_i])/2, label="ave")
    gs_ax1.set_title(f"@ Tilt:{off_axis_angles_tilt[oa_i]:latex}, Pan:{off_axis_angles_pan[oa_i]:latex}")
    gs_ax1.set_ylabel(f"{optic} [{eff_areas_pan.unit:latex}]")
    gs_ax1.set_xlabel(f"Energy [{ea_energies.unit:latex}]")
    plt.legend(handles=p10+p11+p12)
    gs_ax1.set_xlim([ea_energies[0].value, ea_energies[-1].value])
    # gs_ax1.set_ylim([0, np.nanmax(eff_areas_tilt[:,oa_i]).value*1.01])

    gs_ax2 = fig.add_subplot(gs[0, 2])
    _ps = []
    for oaa in off_axis_angles_tilt:
        _lw = 1 if oaa >=0 else 2
        _, _, efs = eff_area_msfc_10shell(ea_energies, off_axis=oaa<<u.arcmin, optic_id=optic)
        _p = gs_ax2.plot(ea_energies, efs, label=f"{oaa:latex}", lw=_lw)
        _ps += _p
    gs_ax2.set_ylabel(f"{optic} [{eff_areas_pan.unit:latex}]")
    gs_ax2.set_xlabel(f"Energy [{ea_energies.unit:latex}]")
    plt.legend(handles=_ps, prop={"size": 9})
    gs_ax2.set_xlim([ea_energies[0].value, ea_energies[-1].value])

    for gsax in [gs_ax0, gs_ax1, gs_ax2]:
        _, _, efs = eff_area_msfc_10shell(ea_energies, off_axis=0<<u.arcmin, optic_id=optic)
        gsax.set_ylim([0, np.nanmax(efs).value*1.01])

    ## OPTIC: X-8
    optic = "X-8"

    vals_tilt = _get_ea_file_info(optic, "tilt")
    vals_pan = _get_ea_file_info(optic, "pan")
    off_axis_angles_tilt, eff_areas_tilt = _get_oa_and_ea_msfc_10shell(vals_tilt)
    off_axis_angles_pan, eff_areas_pan = _get_oa_and_ea_msfc_10shell(vals_pan)
    ea_energies = [4.5,  5.5,  6.5,  7.5,  8.5,  9.5, 11. , 13. , 15. , 17. , 19. , 22.5, 27.5] << u.keV
    e_i = 0
    gs_ax3 = fig.add_subplot(gs[1, 0])
    p00 = gs_ax3.plot(off_axis_angles_tilt, eff_areas_tilt[e_i], label="tilt", lw=4)
    p01 = gs_ax3.plot(off_axis_angles_pan, eff_areas_pan[e_i], label="pan")
    gs_ax3.set_title(f"@ Energy: {ea_energies[e_i]}")
    gs_ax3.set_ylabel(f"Heritage MSFC {optic} [{eff_areas_pan.unit:latex}]")
    gs_ax3.set_xlabel(f"off-axis angle [{off_axis_angles_tilt.unit:latex}]")
    plt.legend(handles=p00+p01)
    gs_ax3.set_xlim([off_axis_angles_tilt[0].value, off_axis_angles_tilt[-1].value])

    oa_i = 5
    gs_ax4 = fig.add_subplot(gs[1, 1])
    p10 = gs_ax4.plot(ea_energies, eff_areas_tilt[:,oa_i], label="tilt", lw=4)
    p11 = gs_ax4.plot(ea_energies, eff_areas_pan[:,oa_i], label="pan", lw=3)
    p12 = gs_ax4.plot(ea_energies, (eff_areas_pan[:,oa_i]+eff_areas_tilt[:,oa_i])/2, label="ave")
    gs_ax4.set_title(f"@ Tilt:{off_axis_angles_tilt[oa_i]:latex}, Pan:{off_axis_angles_pan[oa_i]:latex}")
    gs_ax4.set_ylabel(f"{optic} [{eff_areas_pan.unit:latex}]")
    gs_ax4.set_xlabel(f"Energy [{ea_energies.unit:latex}]")
    plt.legend(handles=p10+p11+p12)
    gs_ax4.set_xlim([ea_energies[0].value, ea_energies[-1].value])
    # gs_ax4.set_ylim([0, np.nanmax(eff_areas_tilt[:,oa_i]).value*1.01])

    gs_ax5 = fig.add_subplot(gs[1, 2])
    _ps = []
    for oaa in off_axis_angles_tilt:
        _lw = 1 if oaa >=0 else 2
        _, _, efs = eff_area_msfc_10shell(ea_energies, off_axis=oaa<<u.arcmin, optic_id=optic)
        _p = gs_ax5.plot(ea_energies, efs, label=f"{oaa:latex}", lw=_lw)
        _ps += _p
    gs_ax5.set_ylabel(f"{optic} [{eff_areas_pan.unit:latex}]")
    gs_ax5.set_xlabel(f"Energy [{ea_energies.unit:latex}]")
    plt.legend(handles=_ps, prop={"size": 9})
    gs_ax5.set_xlim([ea_energies[0].value, ea_energies[-1].value])

    for gsax in [gs_ax3, gs_ax4, gs_ax5]:
        _, _, efs = eff_area_msfc_10shell(ea_energies, off_axis=0<<u.arcmin, optic_id=optic)
        gsax.set_ylim([0, np.nanmax(efs).value*1.01])

    gs_ax5 = fig.add_subplot(gs[2, 0])
    _f = os.path.join(EFF_PATH, "FOXSI4_Module_MSFC_HiRes_EA_with_models_v1.txt")
    e, *_ = np.loadtxt(_f).T
    e <<= u.keV
    _, msfc_hi_res_p0 = eff_area_msfc_hi_res(e, position=0)
    _, msfc_hi_res_p3 = eff_area_msfc_hi_res(e, position=3)
    _, msfc_hi_res_p6 = eff_area_msfc_hi_res(e, position=6)
    _, msfc_hi_res_p0m = eff_area_msfc_hi_res(e, position=0, use_model=True)
    _, msfc_hi_res_p3m = eff_area_msfc_hi_res(e, position=3, use_model=True)
    _, msfc_hi_res_p6m = eff_area_msfc_hi_res(e, position=6, use_model=True)
    p10 = gs_ax5.plot(e, msfc_hi_res_p0, label="Pos. 0 (X10/FM2)")
    p20 = gs_ax5.plot(e, msfc_hi_res_p3, label="Pos. 3 (X09/FM1)")
    p30 = gs_ax5.plot(e, msfc_hi_res_p6, label="Pos. 6 (X11/FM3)")
    p11 = gs_ax5.plot(e, msfc_hi_res_p0m, label="Pos. 0 (X10/FM2, model)")
    p21 = gs_ax5.plot(e, msfc_hi_res_p3m, label="Pos. 3 (X09/FM1, model)")
    p31 = gs_ax5.plot(e, msfc_hi_res_p6m, label="Pos. 6 (X11/FM3, model)")
    gs_ax5.set_title("MSFC High-res.")
    gs_ax5.set_xlabel(f"Energy {e.unit:latex}")
    gs_ax5.set_ylabel(f"Eff. Area {msfc_hi_res_p0.unit:latex}")
    plt.legend(handles=p10+p11+p20+p21+p30+p31, fontsize=6)

    gs_ax5.set_xlim([e[0].value, e[-1].value])

    gs_ax6 = fig.add_subplot(gs[2, 1])
    for_native_res = np.nan << u.keV
    native_es_on, old_vals = eff_area_nagoya(for_native_res, file=None)
    native_es_cmos, cmos_vals = eff_area_cmos(for_native_res, file=None, telescope=1)
    native_es_nag, nag_vals = eff_area_nagoya_sxt(for_native_res, file=None)
    p1 = gs_ax6.plot(native_es_on, old_vals, label="Old SXR Nagoya (might inc. coll. &| OBF)")
    p2 = gs_ax6.plot(native_es_cmos, cmos_vals, label="CMOS SXR Nagoya")
    p3 = gs_ax6.plot(native_es_nag, nag_vals, label="SXR Nagoya (inc. coll. & OBF)")
    gs_ax6.set_title("Nagoya SXR")
    gs_ax6.set_xlabel(f"Energy {e.unit:latex}")
    gs_ax6.set_ylabel(f"Eff. Area {msfc_hi_res_p0.unit:latex}")
    plt.legend(handles=p1+p2+p3, fontsize=6)

    gs_ax6 = fig.add_subplot(gs[2, 2])
    for_native_res = np.nan << u.keV
    native_es_nag, nag_vals = eff_area_nagoya_hxt(for_native_res, file=None)
    p1 = gs_ax6.plot(native_es_nag, nag_vals, label="HXR Nagoya")
    gs_ax6.set_title("Nagoya HXR")
    gs_ax6.set_xlabel(f"Energy {e.unit:latex}")
    gs_ax6.set_ylabel(f"Eff. Area {msfc_hi_res_p0.unit:latex}")
    plt.legend(handles=p1, fontsize=6)

    plt.tight_layout()
    if save_asset:
        pathlib.Path(ASSETS_PATH).mkdir(parents=True, exist_ok=True)
        plt.savefig(os.path.join(ASSETS_PATH,"heritage-and-msfc-optics.png"), dpi=200, bbox_inches="tight")
    plt.show()

if __name__=="__main__":
    s = np.array([np.nan, np.nan])<<u.keV
    s = np.nan<<u.keV
    # print(s, np.all(np.isnan(s)))
    eff_area_nagoya_hxt(s, file=None)
    save_asset = False
    # asset_cmos_plot(save_asset=save_asset)
    asset_cmos_files(save_asset=save_asset)
    asset_all_optics(save_asset=save_asset)
    