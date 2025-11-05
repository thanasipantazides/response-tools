"""
Telescope Summary
=================

An example showing the constituants and, therefore, photon paths of all 
FOXSI-4 telescopes.
"""

import response_tools.telescope_parts as telescope_parts
import numpy as np
import matplotlib as mpl
from matplotlib.colors import LogNorm

import astropy.units as u



def flatten(something):
    if isinstance(something, (list, tuple, set, range, np.ndarray)):
        for sub in something:
            yield from flatten(sub)
    else:
        yield something

def call_response(abbrev:str, mid_energies):
    fname = ''
    if abbrev[0] == 'p':
        fname = 'foxsi4_position' + abbrev[1::]
        posint = int(abbrev[1])
        if 'annotate' not in abbrev:
            # print('will call the function:', fname)
            try:
                response = getattr(telescope_parts, fname)
                if 'optic' in abbrev:
                    return response(mid_energies, off_axis_angle=0 << u.arcmin)
                elif 'detector' in abbrev:
                    if posint < 6 and posint > 1:
                        return response(region=0)
                    else:
                        return response()
                elif 'collimator' in abbrev:
                    return response(off_axis_angle=0 << u.arcmin)
                else:
                    print(response(mid_energies))
                    return response(mid_energies)
            except AttributeError as e:
                print(e)
                return None

# rules:
#   p# -> position#
#   prefix -> foxsi4_
#   detector -> detector_response
#   blanket -> thermal_blanket
#   filter -> uniform_al
#   mylar -> al_mylar
#   attenuator -> pixelated_attenuator

def behemoth_plot():
    blank_sentinel = "BLANK"
    mosaic = np.array([
        ["p0_prefilter",            "p1_prefilter",         "BLANK",                "BLANK",                    "BLANK",                "BLANK",                    "BLANK",                "r0_annotate"],
        ["p0_collimator",           "p1_collimator",        "p2_thermal_blanket",   "p3_thermal_blanket",       "p4_thermal_blanket",   "p5_thermal_blanket",       "p6_thermal_blanket",   "r1_annotate"],
        ["p0_optics",               "p1_optics",            "p2_optics",            "p3_optics",                "p4_optics",            "p5_optics",                "p6_optics",            "r2_annotate"],
        ["BLANK",                   "BLANK",                "BLANK",                "p3_pixelated_attenuator",  "BLANK",                "p5_pixelated_attenuator",  "BLANK",                "r3_annotate"],
        ["p0_obf",                  "p1_obf",               "p2_uniform_al",        "p3_al_mylar",              "p4_uniform_al",        "p5_al_mylar",              "p6_al_mylar",          "r4_annotate"],
        ["p0_detector_response",    "p1_detector_response", "p2_detector_response", "p3_detector_response",     "p4_detector_response", "p5_detector_response",     "p6_detector_response", "r5_annotate"],
        ["p0_annotate",             "p1_annotate",          "p2_annotate",          "p3_annotate",              "p4_annotate",          "p5_annotate",              "p6_annotate",          "corner"],
    ])

    fig, ax = mpl.pyplot.subplot_mosaic(mosaic, figsize=(12,8), empty_sentinel=blank_sentinel, width_ratios=[2, 2, 2, 2, 2, 2, 2, 1], height_ratios=[2, 2, 2, 2, 2, 2, 1])

    mid_energies = np.arange(4,20,0.5) << u.keV

    # plot everything
    for p in flatten(mosaic):
        r = call_response(p, mid_energies)
        # print(p, r)
        if r is not None:
            # print(p, r.contents)
            try:
                ax[p].plot(mid_energies, r.contents['transmissions'], color='black')
                # ax[p].semilogy(mid_energies, r.contents['transmissions'], color='black')
                # ax[p].set_ylim([1e-4,1e0])
                continue
            except Exception:
                print("no transmissions!")
            try:
                ax[p].plot(mid_energies, r.contents['effective_areas'], color='black')
                continue
            except Exception:
                print("no ea!")
            try:
                ax[p].axhline(r.transmissions, color='black')
            except Exception:
                pass
            try:
                ax[p].imshow(
                    r.contents['detector_response'].value, 
                    origin="lower",
                    norm=LogNorm(vmin=0.001),
                    extent=[np.min(r.output_energy_edges.value), 
                            np.max(r.output_energy_edges.value), 
                            np.min(r.input_energy_edges.value), 
                            np.max(r.input_energy_edges.value)],
                    aspect='auto'
                )
                # print(np.shape(r.detector_response.value))
                # print(r.detector_response.value)
                continue
            except Exception:
                print("no detector!")
                # rmf_mid_energies = (r.input_energy_edges[:-1]+r.input_energy_edges[1:])/2
            # try:
                # ax[p].imshow(r.contents[''])

    # format the table
    for col in mosaic.T:
        first_nonblank = np.argmax(col != blank_sentinel)
        for k,p in enumerate(col):
            if (k == 0): continue
            if p == blank_sentinel: continue
            print(first_nonblank, p)
            ax[p].sharex(ax[col[first_nonblank]])
    for row in mosaic:
        first_nonblank = np.argmax(row != blank_sentinel)
        for k,p in enumerate(row):
            if (k == 0): continue
            if p == blank_sentinel: continue
            print(first_nonblank, p)
            ax[p].sharey(ax[row[first_nonblank]])
            
    mpl.pyplot.show()
    
behemoth_plot()
