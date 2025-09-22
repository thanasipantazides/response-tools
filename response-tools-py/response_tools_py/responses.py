"""Functions to make the RMFs and ARFs. """

from dataclasses import dataclass
import logging
import sys

import astropy.units as u

from response_tools_py.attenuation import att_foxsi4_atmosphere
import response_tools_py.telescope_parts as tp
from response_tools_py.util import BaseOutput

@dataclass
class Response1DOutput(BaseOutput):
    """Class for keeping track of 1D response response values."""
    # numbers
    mid_energies: u.Quantity
    response: u.Quantity
    # bookkeeping
    response_type: str
    telescope: str
    elements: tuple
    # any other fields needed can be added here
    # can even add with a default so the input is not required for every other instance

@dataclass
class Response2DOutput(BaseOutput):
    """Class for keeping track of 2D response response values."""
    # numbers
    input_energy_edges: u.Quantity # photon axis
    output_energy_edges: u.Quantity # count axis
    response: u.Quantity
    # bookkeeping
    response_type: str
    telescope: str
    elements: tuple
    # any other fields needed can be added here
    # can even add with a default so the input is not required for every other instance

# telescope 2
@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin)
def foxsi4_telescope2_arf(mid_energies, off_axis_angle):
    """The ARF for telescope 2. """
    tb = tp.foxsi4_position2_thermal_blanket(mid_energies) 
    opt = tp.foxsi4_position2_optics(mid_energies, 
                              off_axis_angle=off_axis_angle) 
    uni_al = tp.foxsi4_position2_uniform_al(mid_energies)

    arf = tb.transmissions * opt.effective_areas * uni_al.transmissions

    func_name = sys._getframe().f_code.co_name
    tb.update_function_path(func_name)
    opt.update_function_path(func_name)
    uni_al.update_function_path(func_name)

    return Response1DOutput(filename="No-File",
                            function_path=func_name,
                            mid_energies=mid_energies,
                            response=arf,
                            response_type="ARF",
                            telescope="foxsi4-2",
                            elements=(tb, opt, uni_al),
                            )

@u.quantity_input(pitch=u.um)
def foxsi4_telescope2_rmf(region:int=None, pitch=None, _side:str="merged", _event_type:str="all"):
    """The RMF for telescope 2. """
    
    rmf = tp.foxsi4_position2_detector_response(region=region, 
                                                pitch=pitch, 
                                                _side=_side, 
                                                _event_type=_event_type)
    func_name = sys._getframe().f_code.co_name
    rmf.update_function_path(func_name)

    return Response2DOutput(filename="No-File",
                            function_path=func_name,
                            input_energy_edges=,
                            output_energy_edges=,
                            response=rmf.detector_response,
                            response_type="RMF",
                            telescope="foxsi4-2",
                            elements=(rmf),
                            )

input_energy_edges: u.Quantity # photon axis
    output_energy_edges: u.Quantity # count axis
    response: u.Quantity
    # bookkeeping
    response_type: str
    telescope: str
    elements: tuple

@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin, time_range=u.second)
def foxsi4_telescope2_response(mid_energies, off_axis_angle, time_range):
    """The full response for telescope 2. """
    atm = att_foxsi4_atmosphere(mid_energies=mid_energies, time_range=time_range)
    arf = foxsi4_telescope2_arf(mid_energies=mid_energies, off_axis_angle=off_axis_angle)
    rmf = foxsi4_telescope2_rmf(mid_energies=mid_energies, off_axis_angle=off_axis_angle)

    total_response = (atm * arf)[:,None] * rmf

    func_name = sys._getframe().f_code.co_name
    atm.update_function_path(func_name)
    arf.update_function_path(func_name)
    rmf.update_function_path(func_name)

    return 

# telescope 3
@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin)
def foxsi4_telescope3_arf(mid_energies, off_axis_angle=0<<u.arcmin):
    logging.warning(f"The `off_axis_angle` input to  {sys._getframe().f_code.co_name} (value:{off_axis_angle}) is unused.")
    return tp.foxsi4_position3_thermal_blanket(mid_energies) \
           * tp.foxsi4_position3_optics(mid_energies) \
           * tp.foxsi4_position3_al_mylar(mid_energies) \
           * tp.foxsi4_position3_pixelated_attenuator(mid_energies)

# telescope 4
@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin)
def foxsi4_telescope4_arf(mid_energies, off_axis_angle=0<<u.arcmin):
    logging.warning(f"The `off_axis_angle` input to  {sys._getframe().f_code.co_name} (value:{off_axis_angle}) is unused.")
    return tp.foxsi4_position4_thermal_blanket(mid_energies) \
           * tp.foxsi4_position4_optics(mid_energies) \
           * tp.foxsi4_position4_uniform_al(mid_energies)

# telescope 5
@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin)
def foxsi4_telescope5_arf(mid_energies, off_axis_angle=0<<u.arcmin):
    return tp.foxsi4_position5_thermal_blanket(mid_energies) \
           * tp.foxsi4_position5_optics(mid_energies, 
                                 off_axis_angle=off_axis_angle) \
           * tp.foxsi4_position5_al_mylar(mid_energies) \
           * tp.foxsi4_position5_pixelated_attenuator(mid_energies)

if __name__=="__main__":
    import numpy as np
    mid_energies = np.arange(3,30.1, 0.1) << u.keV
    off_axis_angle = 0 << u.arcmin
    p2_arf = telescope2_arf(mid_energies=mid_energies, off_axis_angle=off_axis_angle)