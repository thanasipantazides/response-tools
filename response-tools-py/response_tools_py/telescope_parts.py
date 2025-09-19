"""Wrappers for position aliases for more specific functions."""

import sys

import astropy.units as u

from response_tools_py.attenuation import (att_thermal_blanket,
                                           att_pixelated, 
                                           att_al_mylar,
                                           att_uniform_al_cdte
                                           )
from response_tools_py.detector_response import (cdte_det_resp_rmf, 
                                                 cmos_det_resp,
                                                 DET_RESP_PATH,
                                                 )
from response_tools_py.effective_area import (eff_area_msfc_10shell,
                                              eff_area_msfc_hi_res,
                                              eff_area_nagoya_hxt,
                                              )

# position 2
@u.quantity_input(mid_energies=u.keV)
def position2_thermal_blanket(mid_energies):
    r = att_thermal_blanket(mid_energies)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin)
def position2_optics(mid_energies, off_axis_angle):
    r = eff_area_msfc_10shell(mid_energies, 
                              off_axis_angle=off_axis_angle, 
                              optic_id="X-7")
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(mid_energies=u.keV)
def position2_uniform_al(mid_energies):
    r = att_uniform_al_cdte(mid_energies, 
                            position=2)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(off_axis_angle=u.arcmin)
def position2_detector_response(off_axis_angle):
    r = cdte_det_resp_rmf # TODO
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

# position 3
@u.quantity_input(mid_energies=u.keV)
def position3_thermal_blanket(mid_energies):
    r = att_thermal_blanket(mid_energies)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(mid_energies=u.keV)
def position3_optics(mid_energies):
    r = eff_area_msfc_hi_res(mid_energies, 
                             position=3, 
                             use_model=True)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(mid_energies=u.keV)
def position3_al_mylar(mid_energies):
    r = att_al_mylar(mid_energies)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(mid_energies=u.keV)
def position3_pixelated_attenuator(mid_energies):
    r = att_pixelated(mid_energies, 
                      values="modelled")
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(off_axis_angle=u.arcmin)
def position3_detector_response(off_axis_angle):
    r = cdte_det_resp_rmf # TODO
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

# position 4
@u.quantity_input(mid_energies=u.keV)
def position4_thermal_blanket(mid_energies):
    r = att_thermal_blanket(mid_energies)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(mid_energies=u.keV)
def position4_optics(mid_energies):
    r = eff_area_nagoya_hxt(mid_energies, 
                            use_model=True)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(mid_energies=u.keV)
def position4_uniform_al(mid_energies):
    r = att_uniform_al_cdte(mid_energies, 
                            position=4)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(off_axis_angle=u.arcmin)
def position4_detector_response(off_axis_angle):
    r = cdte_det_resp_rmf # TODO
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

# position 5
@u.quantity_input(mid_energies=u.keV)
def position5_thermal_blanket(mid_energies):
    r = att_thermal_blanket(mid_energies)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin)
def position5_optics(mid_energies, off_axis_angle):
    r = eff_area_msfc_10shell(mid_energies, 
                              off_axis_angle=off_axis_angle<<u.arcmin, 
                              optic_id="X-8")
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(mid_energies=u.keV)
def position5_al_mylar(mid_energies):
    r = att_al_mylar(mid_energies)
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(mid_energies=u.keV)
def position5_pixelated_attenuator(mid_energies):
    r = att_pixelated(mid_energies, 
                      values="modelled")
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

@u.quantity_input(off_axis_angle=u.arcmin)
def position5_detector_response(off_axis_angle):
    r = cdte_det_resp_rmf # TODO
    r.update_function_path(sys._getframe().f_code.co_name)
    return r

if __name__=="__main__":
    mid_energies = [4.5,  5.5,  6.5,  7.5,  8.5,  9.5, 11. , 13. , 15. , 17. , 19. , 22.5, 27.5] << u.keV
    p2_tb = position2_thermal_blanket(mid_energies)