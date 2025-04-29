
import os
import pathlib

import astropy.units as u
from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

from att import (att_thermal_blanket, 
                    att_uniform_al_cdte, 
                    att_pixelated, 
                    att_al_mylar,
                    att_cmos_obfilter,
                    att_cmos_collimator_ratio,
                    att_cmos_filter,)
from det_resp import (cdte_det_resp_rmf, 
                        cmos_det_resp,
                        DET_RESP_PATH,)
from eff_area import (eff_area_msfc_10shell, 
                        eff_area_msfc_hi_res,
                        eff_area_cmos,)
from phot_spec import zeroes2nans
from quantum_eff import qe_cmos

def foxsi4_response_paths(save_assets=False):
    
    assets_dir = os.path.join(pathlib.Path(__file__).parent, "..", "..", "assets", "response-tools-py-figs", "response-paths")
    pathlib.Path(assets_dir).mkdir(parents=True, exist_ok=True)

    plt.rcParams.update({'font.size': 7})

    tb_col = plt.cm.viridis([.5])

    FIGSIZE = (18,4)
    GS = (1, 12)

    ###########################################################################
    ########################## CdTe 4 (pos. 2) ################################
    ###########################################################################

    fig = plt.figure(figsize=FIGSIZE)
    gs = gridspec.GridSpec(*GS)

    # define det response first so we know what energies we actually care about
    f_rmf = os.path.join(DET_RESP_PATH, "cdte", "merged", "Resp_3keVto30keV_CdTe1_reg0_1hit.rmf")
    e_lo, e_hi, rmf = cdte_det_resp_rmf(f_rmf)
    mid_energies = (e_lo+e_hi)/2
    photon_energy_lims = [np.nanmin(mid_energies.value), np.nanmax(mid_energies.value)]

    ## thermal blanket
    gs_ax0 = fig.add_subplot(gs[0, 1:3])
    att_therm_bl = zeroes2nans(att_thermal_blanket(mid_energies))
    gs_ax0.set_xlabel(f"Transmission [{att_therm_bl.unit:latex}]")
    gs_ax0.set_ylabel(f"Photon Energy [{e_lo.unit:latex}]")
    gs_ax0.set_title("Thermal blanket")
    gs_ax0.plot(att_therm_bl, mid_energies, color=tb_col, ls="-")

    y_lims = [0,1.01]
    gs_ax0.set_xlim(y_lims)
    gs_ax0.set_ylim(photon_energy_lims)
    gs_ax0.set_aspect(np.diff(y_lims)/np.diff(photon_energy_lims))

    ## Marshall 10-shell
    optic = "X-7"
    gs_ax1 = fig.add_subplot(gs[0, 3:5])
    gs_ax1.set_title(f"Marshall 10-shell ({optic})")
    gs_ax1.set_aspect('equal', 'box')
    gs_ax1.set_yticks([])
    _ps = []
    for oaa in [-8.64, -6.72, -4.8, -2.88, -0.96, 0., 0.96, 2.88, 4.8, 6.72, 8.64]<<u.arcmin:
        _lw = 1 if oaa >=0 else 2
        _eff_areas = eff_area_msfc_10shell(mid_energies, off_axis=oaa<<u.arcmin, optic_id=optic)
        _p = gs_ax1.plot(_eff_areas, mid_energies, label=f"{oaa:latex}", lw=_lw)
        _ps += _p
    gs_ax1.set_xlabel(f"{optic} [{_eff_areas.unit:latex}]")
    plt.legend(handles=_ps, prop={"size": 6})
    oa_eff_area = eff_area_msfc_10shell(mid_energies, off_axis=0<<u.arcmin, optic_id=optic)
    y_lims = [0, np.nanmax(oa_eff_area).value*1.01]
    gs_ax1.set_xlim(y_lims)
    gs_ax1.set_ylim(photon_energy_lims)
    gs_ax1.set_aspect(np.diff(y_lims)/np.diff(photon_energy_lims))
    gs_ax1.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    ## Al filter
    gs_ax2 = fig.add_subplot(gs[0, 5:7])
    gs_ax2.set_title("Al (0.015\")")
    cdte_fixed2 = zeroes2nans(att_uniform_al_cdte(mid_energies, file=None, position=2))
    plt.plot(cdte_fixed2, mid_energies, label="CdTe fixed p2")
    gs_ax2.set_xlabel(f"Transmission [{cdte_fixed2.unit:latex}]")
    y_lims = [0,1.01]
    gs_ax2.set_xlim(y_lims)
    gs_ax2.set_ylim(photon_energy_lims)
    gs_ax2.set_aspect(np.diff(y_lims)/np.diff(photon_energy_lims))
    gs_ax2.set_yticks([])
    gs_ax2.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    ## no2021_07
    gs_ax3 = fig.add_subplot(gs[0, 7:9])
    gs_ax3.imshow(rmf.value, origin="lower", norm=LogNorm(vmin=0.001, vmax=0.12), extent=[np.min(e_lo.value), np.max(e_lo.value), np.min(e_lo.value), np.max(e_lo.value)])
    gs_ax3.set_xlabel(f"Count Energy [{e_lo.unit:latex}]")
    gs_ax3.set_title(f"{f_rmf.split('/')[-1]}", size=8)
    gs_ax3.set_aspect('equal', 'box')
    gs_ax3.set_yticks([])
    gs_ax3.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    ## total response
    gs_ax4 = fig.add_subplot(gs[0, 9:11])
    title = "Pos. 2, CdTe 4 Response"
    gs_ax4.set_title(title)
    gs_ax4.set_aspect('equal', 'box')
    gs_ax4.set_yticks([])
    pos2_resp = rmf * att_therm_bl[:,None] * oa_eff_area[:,None] * cdte_fixed2[:,None]
    gs_ax4.imshow(pos2_resp.value, origin="lower", norm=LogNorm(vmin=0.001, vmax=0.12), extent=[np.min(e_lo.value), np.max(e_lo.value), np.min(e_lo.value), np.max(e_lo.value)])
    gs_ax4.set_xlabel(f"Count Energy [{e_lo.unit:latex}]")
    gs_ax4.annotate("=", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    plt.tight_layout()
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.01, hspace=None)

    if save_assets:
        plt.savefig(os.path.join(assets_dir,f"{title}.png"), dpi=200, bbox_inches="tight")
    plt.show()

    ###########################################################################
    ###########################################################################

    ###########################################################################
    ########################## CdTe 2 (pos. 3) ################################
    ###########################################################################

    fig = plt.figure(figsize=FIGSIZE)
    gs = gridspec.GridSpec(*GS)

    # define det response first so we know what energies we actually care about
    f_rmf = os.path.join(DET_RESP_PATH, "cdte", "merged", "Resp_3keVto30keV_CdTe1_reg0_1hit.rmf")
    e_lo, e_hi, rmf = cdte_det_resp_rmf(f_rmf)
    mid_energies = (e_lo+e_hi)/2
    photon_energy_lims = [np.nanmin(mid_energies.value), np.nanmax(mid_energies.value)]

    ## thermal blanket
    gs_ax0 = fig.add_subplot(gs[0, :2])
    att_therm_bl = zeroes2nans(att_thermal_blanket(mid_energies))
    gs_ax0.set_xlabel(f"Transmission [{att_therm_bl.unit:latex}]")
    gs_ax0.set_ylabel(f"Photon Energy [{e_lo.unit:latex}]")
    gs_ax0.set_title("Thermal blanket")
    gs_ax0.plot(att_therm_bl, mid_energies, color=tb_col, ls="-")

    y_lims = [0,1.01]
    gs_ax0.set_xlim(y_lims)
    gs_ax0.set_ylim(photon_energy_lims)
    gs_ax0.set_aspect(np.diff(y_lims)/np.diff(photon_energy_lims))

    ## Marshall 2-shell, high-res
    optic = "X09/FM2"
    gs_ax1 = fig.add_subplot(gs[0, 2:4])
    gs_ax1.set_title(f"Marshall 2-shell ({optic})")
    gs_ax1.set_aspect('equal', 'box')
    gs_ax1.set_yticks([])
    _eff_areas = eff_area_msfc_hi_res(mid_energies, position=3)
    gs_ax1.plot(_eff_areas, mid_energies, label=f"{oaa:latex}", lw=_lw)
    gs_ax1.set_xlabel(f"{optic} [{_eff_areas.unit:latex}]")
    y_lims = [0, np.nanmax(_eff_areas).value*1.01]
    gs_ax1.set_xlim(y_lims)
    gs_ax1.set_ylim(photon_energy_lims)
    gs_ax1.set_aspect(np.diff(y_lims)/np.diff(photon_energy_lims))
    gs_ax1.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    ## Al Mylar
    gs_ax2 = fig.add_subplot(gs[0, 4:6])
    gs_ax2.set_title("Al Mylar")
    al_mylar_att = zeroes2nans(att_al_mylar(mid_energies))
    plt.plot(al_mylar_att, mid_energies, label="CdTe fixed p2")
    gs_ax2.set_xlabel(f"Transmission [{al_mylar_att.unit:latex}]")
    y_lims = [0,1.01]
    gs_ax2.set_xlim(y_lims)
    gs_ax2.set_ylim(photon_energy_lims)
    gs_ax2.set_aspect(np.diff(y_lims)/np.diff(photon_energy_lims))
    gs_ax2.set_yticks([])
    gs_ax2.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    ## Pix. Att.
    gs_ax3 = fig.add_subplot(gs[0, 6:8])
    gs_ax3.set_title("Pixelated Attenuator")
    pix_att = zeroes2nans(att_pixelated(mid_energies, values="modelled"))
    plt.plot(pix_att, mid_energies, label="Pix. Att., pos. 5")
    gs_ax3.set_xlabel(f"Transmission [{pix_att.unit:latex}]")
    y_lims = [0,1.01]
    gs_ax3.set_xlim(y_lims)
    gs_ax3.set_ylim(photon_energy_lims)
    gs_ax3.set_aspect(np.diff(y_lims)/np.diff(photon_energy_lims))
    gs_ax3.set_yticks([])
    gs_ax3.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    ## no2021_07
    gs_ax4 = fig.add_subplot(gs[0, 8:10])
    gs_ax4.imshow(rmf.value, origin="lower", norm=LogNorm(vmin=0.001, vmax=0.12), extent=[np.min(e_lo.value), np.max(e_lo.value), np.min(e_lo.value), np.max(e_lo.value)])
    gs_ax4.set_xlabel(f"Count Energy [{e_lo.unit:latex}]")
    gs_ax4.set_title(f"{f_rmf.split('/')[-1]}", size=8)
    gs_ax4.set_aspect('equal', 'box')
    gs_ax4.set_yticks([])
    gs_ax4.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    ## total response
    gs_ax5 = fig.add_subplot(gs[0, 10:])
    title = "Pos. 3, CdTe 2 Response"
    gs_ax5.set_title(title)
    gs_ax5.set_aspect('equal', 'box')
    gs_ax5.set_yticks([])
    pos2_resp = rmf * att_therm_bl[:,None] * _eff_areas[:,None] * al_mylar_att[:,None] * pix_att[:,None]
    gs_ax5.imshow(pos2_resp.value, origin="lower", norm=LogNorm(vmin=0.001, vmax=0.12), extent=[np.min(e_lo.value), np.max(e_lo.value), np.min(e_lo.value), np.max(e_lo.value)])
    gs_ax5.set_xlabel(f"Count Energy [{e_lo.unit:latex}]")
    gs_ax5.annotate("=", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    plt.tight_layout()
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.01, hspace=None)

    if save_assets:
        plt.savefig(os.path.join(assets_dir,f"{title}.png"), dpi=200, bbox_inches="tight")
    plt.show()

    ###########################################################################
    ###########################################################################

    ###########################################################################
    ########################## CdTe 3 (pos. 4) ################################
    ###########################################################################

    fig = plt.figure(figsize=FIGSIZE)
    gs = gridspec.GridSpec(*GS)

    # define det response first so we know what energies we actually care about
    f_rmf = os.path.join(DET_RESP_PATH, "cdte", "merged", "Resp_3keVto30keV_CdTe1_reg0_1hit.rmf")
    e_lo, e_hi, rmf = cdte_det_resp_rmf(f_rmf)
    mid_energies = (e_lo+e_hi)/2
    photon_energy_lims = [np.nanmin(mid_energies.value), np.nanmax(mid_energies.value)]

    ## thermal blanket
    gs_ax0 = fig.add_subplot(gs[0, 1:3])
    att_therm_bl = zeroes2nans(att_thermal_blanket(mid_energies))
    gs_ax0.set_xlabel(f"Transmission [{att_therm_bl.unit:latex}]")
    gs_ax0.set_ylabel(f"Photon Energy [{e_lo.unit:latex}]")
    gs_ax0.set_title("Thermal blanket")
    gs_ax0.plot(att_therm_bl, mid_energies, color=tb_col, ls="-")

    y_lims = [0,1.01]
    gs_ax0.set_xlim(y_lims)
    gs_ax0.set_ylim(photon_energy_lims)
    gs_ax0.set_aspect(np.diff(y_lims)/np.diff(photon_energy_lims))

    ## Nagoya 1-shell
    gs_ax1 = fig.add_subplot(gs[0, 3:5])
    gs_ax1.set_title("Nagoya 1-Shell HXT")
    gs_ax1.set_aspect('equal', 'box')
    gs_ax1.set_yticks([])
    gs_ax1.annotate("?", (0.5, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")
    y_lims = [0, np.nanmax(oa_eff_area).value*1.01]
    gs_ax1.set_xlim(y_lims)
    gs_ax1.set_ylim(photon_energy_lims)
    gs_ax1.set_aspect(np.diff(y_lims)/np.diff(photon_energy_lims))
    gs_ax1.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    ## Al filter
    gs_ax2 = fig.add_subplot(gs[0, 5:7])
    gs_ax2.set_title("Al (0.005\")")
    cdte_fixed2 = zeroes2nans(att_uniform_al_cdte(mid_energies, file=None, position=4))
    plt.plot(cdte_fixed2, mid_energies, label="CdTe fixed p4")
    gs_ax2.set_xlabel(f"Transmission [{cdte_fixed2.unit:latex}]")
    y_lims = [0,1.01]
    gs_ax2.set_xlim(y_lims)
    gs_ax2.set_ylim(photon_energy_lims)
    gs_ax2.set_aspect(np.diff(y_lims)/np.diff(photon_energy_lims))
    gs_ax2.set_yticks([])
    gs_ax2.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    ## no2021_07
    gs_ax3 = fig.add_subplot(gs[0, 7:9])
    gs_ax3.imshow(rmf.value, origin="lower", norm=LogNorm(vmin=0.001, vmax=0.12), extent=[np.min(e_lo.value), np.max(e_lo.value), np.min(e_lo.value), np.max(e_lo.value)])
    gs_ax3.set_xlabel(f"Count Energy [{e_lo.unit:latex}]")
    gs_ax3.set_title(f"{f_rmf.split('/')[-1]}", size=8)
    gs_ax3.set_aspect('equal', 'box')
    gs_ax3.set_yticks([])
    gs_ax3.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    ## total response
    gs_ax4 = fig.add_subplot(gs[0, 9:11])
    title = "Pos. 4, CdTe 3 Response"
    gs_ax4.set_title(title)
    gs_ax4.set_aspect('equal', 'box')
    gs_ax4.set_yticks([])
    gs_ax4.annotate("?", (0.5, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")
    gs_ax4.set_xlabel(f"Count Energy [{e_lo.unit:latex}]")
    gs_ax4.annotate("=", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    plt.tight_layout()
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.01, hspace=None)
    
    if save_assets:
        plt.savefig(os.path.join(assets_dir,f"{title}.png"), dpi=200, bbox_inches="tight")
    plt.show()


    ###########################################################################
    ###########################################################################

    ###########################################################################
    ########################## CdTe 1 (pos. 5) ################################
    ###########################################################################

    fig = plt.figure(figsize=FIGSIZE)
    gs = gridspec.GridSpec(*GS)

    # define det response first so we know what energies we actually care about
    f_rmf = os.path.join(DET_RESP_PATH, "cdte", "merged", "Resp_3keVto30keV_CdTe1_reg0_1hit.rmf")
    e_lo, e_hi, rmf = cdte_det_resp_rmf(f_rmf)
    mid_energies = (e_lo+e_hi)/2
    photon_energy_lims = [np.nanmin(mid_energies.value), np.nanmax(mid_energies.value)]

    ## thermal blanket
    gs_ax0 = fig.add_subplot(gs[0, :2])
    att_therm_bl = zeroes2nans(att_thermal_blanket(mid_energies))
    gs_ax0.set_xlabel(f"Transmission [{att_therm_bl.unit:latex}]")
    gs_ax0.set_ylabel(f"Photon Energy [{e_lo.unit:latex}]")
    gs_ax0.set_title("Thermal blanket")
    gs_ax0.plot(att_therm_bl, mid_energies, color=tb_col, ls="-")

    y_lims = [0,1.01]
    gs_ax0.set_xlim(y_lims)
    gs_ax0.set_ylim(photon_energy_lims)
    gs_ax0.set_aspect(np.diff(y_lims)/np.diff(photon_energy_lims))

    ## Marshall 10-shell
    optic = "X-8"
    gs_ax1 = fig.add_subplot(gs[0, 2:4])
    gs_ax1.set_title(f"Marshall 10-shell ({optic})")
    gs_ax1.set_aspect('equal', 'box')
    gs_ax1.set_yticks([])
    _ps = []
    for oaa in [-8.64, -6.72, -4.8, -2.88, -0.96, 0., 0.96, 2.88, 4.8, 6.72, 8.64]<<u.arcmin:
        _lw = 1 if oaa >=0 else 2
        _eff_areas = eff_area_msfc_10shell(mid_energies, off_axis=oaa<<u.arcmin, optic_id=optic)
        _p = gs_ax1.plot(_eff_areas, mid_energies, label=f"{oaa:latex}", lw=_lw)
        _ps += _p
    gs_ax1.set_xlabel(f"{optic} [{_eff_areas.unit:latex}]")
    plt.legend(handles=_ps, prop={"size": 6})
    oa_eff_area = eff_area_msfc_10shell(mid_energies, off_axis=0<<u.arcmin, optic_id=optic)
    y_lims = [0, np.nanmax(oa_eff_area).value*1.01]
    gs_ax1.set_xlim(y_lims)
    gs_ax1.set_ylim(photon_energy_lims)
    gs_ax1.set_aspect(np.diff(y_lims)/np.diff(photon_energy_lims))
    gs_ax1.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    ## Al Mylar
    gs_ax2 = fig.add_subplot(gs[0, 4:6])
    gs_ax2.set_title("Al Mylar")
    al_mylar_att = zeroes2nans(att_al_mylar(mid_energies))
    plt.plot(al_mylar_att, mid_energies, label="CdTe fixed p2")
    gs_ax2.set_xlabel(f"Transmission [{al_mylar_att.unit:latex}]")
    y_lims = [0,1.01]
    gs_ax2.set_xlim(y_lims)
    gs_ax2.set_ylim(photon_energy_lims)
    gs_ax2.set_aspect(np.diff(y_lims)/np.diff(photon_energy_lims))
    gs_ax2.set_yticks([])
    gs_ax2.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    ## Pix. Att.
    gs_ax3 = fig.add_subplot(gs[0, 6:8])
    gs_ax3.set_title("Pixelated Attenuator")
    pix_att = zeroes2nans(att_pixelated(mid_energies, values="modelled"))
    plt.plot(pix_att, mid_energies, label="Pix. Att., pos. 5")
    gs_ax3.set_xlabel(f"Transmission [{pix_att.unit:latex}]")
    y_lims = [0,1.01]
    gs_ax3.set_xlim(y_lims)
    gs_ax3.set_ylim(photon_energy_lims)
    gs_ax3.set_aspect(np.diff(y_lims)/np.diff(photon_energy_lims))
    gs_ax3.set_yticks([])
    gs_ax3.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    ## no2021_07
    gs_ax4 = fig.add_subplot(gs[0, 8:10])
    gs_ax4.imshow(rmf.value, origin="lower", norm=LogNorm(vmin=0.001, vmax=0.12), extent=[np.min(e_lo.value), np.max(e_lo.value), np.min(e_lo.value), np.max(e_lo.value)])
    gs_ax4.set_xlabel(f"Count Energy [{e_lo.unit:latex}]")
    gs_ax4.set_title(f"{f_rmf.split('/')[-1]}", size=8)
    gs_ax4.set_aspect('equal', 'box')
    gs_ax4.set_yticks([])
    gs_ax4.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    ## total response
    gs_ax5 = fig.add_subplot(gs[0, 10:])
    title = "Pos. 5, CdTe 1 Response"
    gs_ax5.set_title(title)
    gs_ax5.set_aspect('equal', 'box')
    gs_ax5.set_yticks([])
    pos2_resp = rmf * att_therm_bl[:,None] * oa_eff_area[:,None] * al_mylar_att[:,None] * pix_att[:, None]
    gs_ax5.imshow(pos2_resp.value, origin="lower", norm=LogNorm(vmin=0.001, vmax=0.12), extent=[np.min(e_lo.value), np.max(e_lo.value), np.min(e_lo.value), np.max(e_lo.value)])
    gs_ax5.set_xlabel(f"Count Energy [{e_lo.unit:latex}]")
    gs_ax5.annotate("=", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    plt.tight_layout()
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.01, hspace=None)
    
    if save_assets:
        plt.savefig(os.path.join(assets_dir,f"{title}.png"), dpi=200, bbox_inches="tight")
    plt.show()


    ###########################################################################
    ###########################################################################


    ###########################################################################
    ###########################################################################

    ###########################################################################
    ########################## CMOS 1 (pos. 0) ################################
    ###########################################################################

    fig = plt.figure(figsize=FIGSIZE)
    GS = (1, 7)
    gs = gridspec.GridSpec(*GS)

    # PATH: optical_blocking_filter_transmittance * collimator_aperture_ratio * mirror_effective_area * attenuation_filter_transmittance * sensor_quantum_efficiency @ response_matrix

    # define det response first so we know what energies we actually care about
    telescope = 0
    counts, mid_energies, rmf = cmos_det_resp(telescope=telescope)
    photon_energy_lims = [np.nanmin(mid_energies.value), np.nanmax(mid_energies.value)]

    ## optical_blocking_filter_transmittance
    gs_ax0 = fig.add_subplot(gs[0, 0])
    obf1 = zeroes2nans(att_cmos_obfilter(mid_energies, telescope=telescope))
    gs_ax0.set_xlabel(f"Transmission [{obf1.unit:latex}]")
    gs_ax0.set_ylabel(f"Photon Energy [{mid_energies.unit:latex}]")
    gs_ax0.set_title(f"OBF{telescope}")
    gs_ax0.plot(obf1, mid_energies, color=tb_col, ls="-")

    y_lims = [0,1.01]
    gs_ax0.set_xlim(y_lims)
    gs_ax0.set_ylim(photon_energy_lims)
    gs_ax0.set_aspect(np.diff(y_lims)/np.diff(photon_energy_lims))

    ## collimator_aperture_ratio
    gs_ax1 = fig.add_subplot(gs[0, 1])
    col1 = att_cmos_collimator_ratio(0<<u.arcsec, telescope=telescope)
    gs_ax1.set_yticks([])
    gs_ax1.set_xticks([])
    gs_ax1.annotate(f"Collimator\naperture\nratio\n{col1}", (0.5, 0.5), xycoords="axes fraction", color="k", size=25, weight="bold", ha="center", va="center")
    gs_ax1.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")
    gs_ax1.set_aspect("equal", "box")

    ## mirror_effective_area
    gs_ax2 = fig.add_subplot(gs[0, 2])
    cmos_ea1 = zeroes2nans(eff_area_cmos(mid_energies, telescope=telescope))
    gs_ax2.set_xlabel(f"Effective Area [{cmos_ea1.unit:latex}]")
    gs_ax2.set_yticks([])
    gs_ax2.set_title(f"CMOS{telescope+1} Mirror")
    gs_ax2.plot(cmos_ea1, mid_energies, color=tb_col, ls="-")

    x_lims = [0, np.nanmax(cmos_ea1).value*1.01]
    gs_ax2.set_xlim(x_lims)
    gs_ax2.set_ylim(photon_energy_lims)
    gs_ax2.set_aspect(np.diff(x_lims)/np.diff(photon_energy_lims))
    gs_ax2.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    ## attenuation_filter_transmittance
    gs_ax3 = fig.add_subplot(gs[0, 3])
    filter1 = zeroes2nans(att_cmos_filter(mid_energies, telescope=telescope))
    gs_ax3.set_xlabel(f"Transmission [{filter1.unit:latex}]")
    gs_ax3.set_yticks([])
    gs_ax3.set_title(f"Filter{telescope}")
    gs_ax3.plot(filter1, mid_energies, color=tb_col, ls="-")

    y_lims = [0,1.01]
    gs_ax3.set_xlim(y_lims)
    gs_ax3.set_ylim(photon_energy_lims)
    gs_ax3.set_aspect(np.diff(y_lims)/np.diff(photon_energy_lims))
    gs_ax3.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    ## sensor_quantum_efficiency
    gs_ax4 = fig.add_subplot(gs[0, 4])
    qe1 = zeroes2nans(qe_cmos(mid_energies, telescope=telescope))
    gs_ax4.set_xlabel(f"Quantum Efficiency [{qe1.unit:latex}]")
    gs_ax4.set_yticks([])
    gs_ax4.set_title(f"CMOS{telescope+1} QE")
    gs_ax4.plot(qe1, mid_energies, color=tb_col, ls="-")

    y_lims = [0,1.01]
    gs_ax4.set_xlim(y_lims)
    gs_ax4.set_ylim(photon_energy_lims)
    gs_ax4.set_aspect(np.diff(y_lims)/np.diff(photon_energy_lims))
    gs_ax4.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    ## response_matrix
    gs_ax5 = fig.add_subplot(gs[0, 5])
    extent = [np.min(counts.value), np.max(counts.value), np.min(mid_energies.value), np.max(mid_energies.value)]
    gs_ax5.set_ylim([0,10])
    gs_ax5.set_yticks([])
    gs_ax5.set_title(f"CMOS{telescope+1} RMF")
    gs_ax5.set_aspect('equal', 'box')
    gs_ax5.imshow(rmf.value, origin="lower", aspect=(extent[1]-extent[0])/(extent[3]-0), extent=extent, norm=LogNorm())
    gs_ax5.set_xlabel(f"Counts? [{counts.unit:latex}]")
    gs_ax5.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    ## total response
    gs_ax6 = fig.add_subplot(gs[0, 6])
    title = f"Pos. {telescope}, CMOS {telescope+1} Response"
    gs_ax6.set_title(title)
    gs_ax6.set_aspect('equal', 'box')
    gs_ax6.set_yticks([])
    gs_ax6.set_ylim([0,10])
    pos0_resp = rmf * obf1[:,None] * col1 * cmos_ea1[:,None] * filter1[:,None] * qe1[:, None]
    gs_ax6.imshow(pos0_resp.value, origin="lower", aspect=(extent[1]-extent[0])/(extent[3]-0), extent=extent, norm=LogNorm())
    gs_ax6.set_xlabel(f"Counts? [{counts.unit:latex}]")
    gs_ax6.annotate("=", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    plt.tight_layout()
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.01, hspace=None)
    
    if save_assets:
        plt.savefig(os.path.join(assets_dir,f"{title}.png"), dpi=200, bbox_inches="tight")
    plt.show()


    ###########################################################################
    ###########################################################################


    ###########################################################################
    ###########################################################################

    ###########################################################################
    ########################## CMOS 2 (pos. 1) ################################
    ###########################################################################

    fig = plt.figure(figsize=FIGSIZE)
    GS = (1, 7)
    gs = gridspec.GridSpec(*GS)

    # PATH: optical_blocking_filter_transmittance * collimator_aperture_ratio * mirror_effective_area * attenuation_filter_transmittance * sensor_quantum_efficiency @ response_matrix

    # define det response first so we know what energies we actually care about
    telescope = 1
    counts, mid_energies, rmf = cmos_det_resp(telescope=telescope)
    photon_energy_lims = [np.nanmin(mid_energies.value), np.nanmax(mid_energies.value)]

    ## optical_blocking_filter_transmittance
    gs_ax0 = fig.add_subplot(gs[0, 0])
    obf2 = zeroes2nans(att_cmos_obfilter(mid_energies, telescope=telescope))
    gs_ax0.set_xlabel(f"Transmission [{obf2.unit:latex}]")
    gs_ax0.set_ylabel(f"Photon Energy [{mid_energies.unit:latex}]")
    gs_ax0.set_title(f"OBF{telescope}")
    gs_ax0.plot(obf2, mid_energies, color=tb_col, ls="-")

    y_lims = [0,1.01]
    gs_ax0.set_xlim(y_lims)
    gs_ax0.set_ylim(photon_energy_lims)
    gs_ax0.set_aspect(np.diff(y_lims)/np.diff(photon_energy_lims))

    ## collimator_aperture_ratio
    gs_ax1 = fig.add_subplot(gs[0, 1])
    col2 = att_cmos_collimator_ratio(0<<u.arcsec, telescope=telescope)
    gs_ax1.set_yticks([])
    gs_ax1.set_xticks([])
    gs_ax1.annotate(f"Collimator\naperture\nratio\n{col2}", (0.5, 0.5), xycoords="axes fraction", color="k", size=25, weight="bold", ha="center", va="center")
    gs_ax1.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")
    gs_ax1.set_aspect("equal", "box")

    ## mirror_effective_area
    gs_ax2 = fig.add_subplot(gs[0, 2])
    cmos_ea2 = zeroes2nans(eff_area_cmos(mid_energies, telescope=telescope))
    gs_ax2.set_xlabel(f"Effective Area [{cmos_ea2.unit:latex}]")
    gs_ax2.set_yticks([])
    gs_ax2.set_title(f"CMOS{telescope+1} Mirror")
    gs_ax2.plot(cmos_ea2, mid_energies, color=tb_col, ls="-")

    x_lims = [0, np.nanmax(cmos_ea2).value*1.01]
    gs_ax2.set_xlim(x_lims)
    gs_ax2.set_ylim(photon_energy_lims)
    gs_ax2.set_aspect(np.diff(x_lims)/np.diff(photon_energy_lims))
    gs_ax2.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    ## attenuation_filter_transmittance
    gs_ax3 = fig.add_subplot(gs[0, 3])
    filter2 = zeroes2nans(att_cmos_filter(mid_energies, telescope=telescope))
    gs_ax3.set_xlabel(f"Transmission [{filter2.unit:latex}]")
    gs_ax3.set_yticks([])
    gs_ax3.set_title(f"Filter{telescope}")
    gs_ax3.plot(filter2, mid_energies, color=tb_col, ls="-")

    y_lims = [0,1.01]
    gs_ax3.set_xlim(y_lims)
    gs_ax3.set_ylim(photon_energy_lims)
    gs_ax3.set_aspect(np.diff(y_lims)/np.diff(photon_energy_lims))
    gs_ax3.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    ## sensor_quantum_efficiency
    gs_ax4 = fig.add_subplot(gs[0, 4])
    qe2 = zeroes2nans(qe_cmos(mid_energies, telescope=telescope))
    gs_ax4.set_xlabel(f"Quantum Efficiency [{qe2.unit:latex}]")
    gs_ax4.set_yticks([])
    gs_ax4.set_title(f"CMOS{telescope+1} QE")
    gs_ax4.plot(qe2, mid_energies, color=tb_col, ls="-")

    y_lims = [0,1.01]
    gs_ax4.set_xlim(y_lims)
    gs_ax4.set_ylim(photon_energy_lims)
    gs_ax4.set_aspect(np.diff(y_lims)/np.diff(photon_energy_lims))
    gs_ax4.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    ## response_matrix
    gs_ax5 = fig.add_subplot(gs[0, 5])
    extent = [np.min(counts.value), np.max(counts.value), np.min(mid_energies.value), np.max(mid_energies.value)]
    gs_ax5.set_ylim([0,10])
    gs_ax5.set_yticks([])
    gs_ax5.set_title(f"CMOS{telescope+1} RMF")
    gs_ax5.set_aspect('equal', 'box')
    gs_ax5.imshow(rmf.value, origin="lower", aspect=(extent[1]-extent[0])/(extent[3]-0), extent=extent, norm=LogNorm())
    gs_ax5.set_xlabel(f"Counts? [{counts.unit:latex}]")
    gs_ax5.annotate("x", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    ## total response
    gs_ax6 = fig.add_subplot(gs[0, 6])
    title = f"Pos. {telescope}, CMOS {telescope+1} Response"
    gs_ax6.set_title(title)
    gs_ax6.set_aspect('equal', 'box')
    gs_ax6.set_yticks([])
    gs_ax6.set_ylim([0,10])
    pos1_resp = rmf * obf2[:,None] * col2 * cmos_ea2[:,None] * filter2[:,None] * qe2[:, None]
    gs_ax6.imshow(pos1_resp.value, origin="lower", aspect=(extent[1]-extent[0])/(extent[3]-0), extent=extent, norm=LogNorm())
    gs_ax6.set_xlabel(f"Counts? [{counts.unit:latex}]")
    gs_ax6.annotate("=", (0, 0.5), xycoords="axes fraction", color="red", size=25, weight="bold", ha="center", va="center")

    plt.tight_layout()
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.01, hspace=None)
    
    if save_assets:
        plt.savefig(os.path.join(assets_dir,f"{title}.png"), dpi=200, bbox_inches="tight")
    plt.show()

if __name__=="__main__":
    foxsi4_response_paths(save_assets=False)