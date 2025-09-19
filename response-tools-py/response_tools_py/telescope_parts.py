"""Wrappers for position aliases for more specific functions."""

import sys

import astropy.units as u

from response_tools_py.attenuation import (att_thermal_blanket,
                                           att_pixelated, 
                                           att_al_mylar,
                                           att_atmosphere,
                                           att_uniform_al_cdte
                                           )
from response_tools_py.detector_response import (cdte_det_resp_rmf, 
                                                 DET_RESP_PATH,
                                                 )
from response_tools_py.effective_area import (eff_area_msfc_10shell,
                                              eff_area_msfc_hi_res,
                                              eff_area_nagoya_hxt,
                                              )

# position 2
def position2_thermal_blanket(mid_energies):
    r = att_thermal_blanket(mid_energies)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

def position2_optics(mid_energies, off_axis=0):
    return eff_area_msfc_10shell(mid_energies, 
                                 off_axis=off_axis<<u.arcmin, 
                                 optic_id="X-7")

def position2_uniform_al(mid_energies):
    return att_uniform_al_cdte(mid_energies, 
                               position=2)

# def position2_arf(mid_energies, off_axis=0):
#     """********* Create a response.py file, make a dataclass in there.
#     """
#     return position2_thermal_blanket(mid_energies) \
#            * position2_optics(mid_energies, 
#                               off_axis=off_axis) \
#            * position2_uniform_al(mid_energies)

# position 3
def position3_thermal_blanket(mid_energies):
    return att_thermal_blanket(mid_energies)

def position3_optics(mid_energies):
    return eff_area_msfc_hi_res(mid_energies, 
                                position=3, 
                                use_model=True)

def position3_al_mylar(mid_energies):
    return att_al_mylar(mid_energies)

def position3_pixelated_attenuator(mid_energies):
    return att_pixelated(mid_energies, 
                         values="modelled")

# def position3_arf(mid_energies, _off_axis=0):
#     return position3_thermal_blanket(mid_energies) \
#            * position3_optics(mid_energies) \
#            * position3_al_mylar(mid_energies) \
#            * position3_pixelated_attenuator(mid_energies)

# position 4
def position4_thermal_blanket(mid_energies):
    return att_thermal_blanket(mid_energies)

def position4_optics(mid_energies):
    return eff_area_nagoya_hxt(mid_energies, 
                               use_model=True)

def position4_uniform_al(mid_energies):
    return att_uniform_al_cdte(mid_energies, 
                               position=4)

# def position4_arf(mid_energies, _off_axis=0):
#     return position4_thermal_blanket(mid_energies) \
#            * position4_optics(mid_energies) \
#            * position4_uniform_al(mid_energies)

# position 5
def position5_thermal_blanket(mid_energies):
    return att_thermal_blanket(mid_energies)

def position5_optics(mid_energies, off_axis=0):
    return eff_area_msfc_10shell(mid_energies, 
                                 off_axis=off_axis<<u.arcmin, 
                                 optic_id="X-8")

def position5_al_mylar(mid_energies):
    return att_al_mylar(mid_energies)

def position5_pixelated_attenuator(mid_energies):
    return att_pixelated(mid_energies, 
                         values="modelled")

# def position5_arf(mid_energies, off_axis=0):
#     return position5_thermal_blanket(mid_energies) \
#            * position5_optics(mid_energies, 
#                               off_axis=off_axis) \
#            * position5_al_mylar(mid_energies) \
#            * position5_pixelated_attenuator(mid_energies)

if __name__=="__main__":
    mid_energies = [4.5,  5.5,  6.5,  7.5,  8.5,  9.5, 11. , 13. , 15. , 17. , 19. , 22.5, 27.5] << u.keV
    p2_tb = position2_thermal_blanket(mid_energies)