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

def foxsi4_telescope_response(arf_response, rmf_response):
    """Full response (DRM: detector response matrix) for a telescope. """

    # check compatibility
    rmf_mids = (rmf_response.input_energy_edges[:-1]+rmf_response.input_energy_edges[1:])/2
    if not np.all(arf_response.mid_energies==rmf_mids):
        raise ValueError("The `arf_response.mid_energies` do not match the bin centers of `rmf_response.input_energy_edges`.\nDRM product cannot be calculated")

    total_response = arf_response.response[:,None] * rmf_response.response

    func_name = sys._getframe().f_code.co_name
    arf_response.update_function_path(func_name)
    rmf_response.update_function_path(func_name)

    return Response2DOutput(filename="No-File",
                            function_path=func_name,
                            input_energy_edges=rmf_response.input_energy_edges,
                            output_energy_edges=rmf_response.output_energy_edges,
                            response=total_response,
                            response_type="DRM",
                            telescope="foxsi4-2",
                            elements=(arf_response,
                                      rmf_response,
                                      ),
                            )

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
                            elements=(tb, 
                                      opt, 
                                      uni_al,
                                      ),
                            )

@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin, time_range=u.second)
def foxsi4_telescope2_flight_arf(mid_energies, off_axis_angle, time_range):
    """The flight ARF for telescope 2.
    
    Includes atmospheric attenuation from flight.
    """
    atm = att_foxsi4_atmosphere(mid_energies=mid_energies, 
                                time_range=time_range)
    arf = foxsi4_telescope2_arf(mid_energies, off_axis_angle)

    flight_arf = atm.transmissions*arf.response

    func_name = sys._getframe().f_code.co_name
    atm.update_function_path(func_name)
    arf.update_function_path(func_name)

    return Response1DOutput(filename="No-File",
                            function_path=func_name,
                            mid_energies=mid_energies,
                            response=flight_arf,
                            response_type="ARF-flight",
                            telescope=f"foxsi4-2",
                            elements=(atm, 
                                      arf,
                                      ),
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
                            input_energy_edges=rmf.input_energy_edges,
                            output_energy_edges=rmf.output_energy_edges,
                            response=rmf.detector_response,
                            response_type="RMF",
                            telescope="foxsi4-2",
                            elements=(rmf,
                                      ),
                            )

# telescope 3
@u.quantity_input(mid_energies=u.keV)
def foxsi4_telescope3_arf(mid_energies):
    """The ARF for telescope 3. """
    tb = tp.foxsi4_position3_thermal_blanket(mid_energies) 
    opt = tp.foxsi4_position3_optics(mid_energies) 
    mylar = tp.foxsi4_position3_al_mylar(mid_energies)
    pix_att = tp.foxsi4_position3_pixelated_attenuator(mid_energies)

    arf = tb.transmissions * opt.effective_areas * mylar.transmissions * pix_att.transmissions

    func_name = sys._getframe().f_code.co_name
    tb.update_function_path(func_name)
    opt.update_function_path(func_name)
    mylar.update_function_path(func_name)
    pix_att.update_function_path(func_name)

    return Response1DOutput(filename="No-File",
                            function_path=func_name,
                            mid_energies=mid_energies,
                            response=arf,
                            response_type="ARF",
                            telescope="foxsi4-2",
                            elements=(tb, 
                                      opt,
                                      mylar, 
                                      pix_att,
                                      ),
                            )

@u.quantity_input(mid_energies=u.keV, time_range=u.second)
def foxsi4_telescope3_flight_arf(mid_energies, time_range):
    """The flight ARF for telescope 3.
    
    Includes atmospheric attenuation from flight.
    """
    atm = att_foxsi4_atmosphere(mid_energies=mid_energies, 
                                time_range=time_range)
    arf = foxsi4_telescope3_arf(mid_energies)

    flight_arf = atm.transmissions*arf.response

    func_name = sys._getframe().f_code.co_name
    atm.update_function_path(func_name)
    arf.update_function_path(func_name)

    return Response1DOutput(filename="No-File",
                            function_path=func_name,
                            mid_energies=mid_energies,
                            response=flight_arf,
                            response_type="ARF-flight",
                            telescope=f"foxsi4-3",
                            elements=(atm, 
                                      arf,
                                      ),
                            )

@u.quantity_input(pitch=u.um)
def foxsi4_telescope3_rmf(region:int=None, pitch=None, _side:str="merged", _event_type:str="all"):
    """The RMF for telescope 3. """
    
    rmf = tp.foxsi4_position3_detector_response(region=region, 
                                                pitch=pitch, 
                                                _side=_side, 
                                                _event_type=_event_type)
    func_name = sys._getframe().f_code.co_name
    rmf.update_function_path(func_name)

    return Response2DOutput(filename="No-File",
                            function_path=func_name,
                            input_energy_edges=rmf.input_energy_edges,
                            output_energy_edges=rmf.output_energy_edges,
                            response=rmf.detector_response,
                            response_type="RMF",
                            telescope="foxsi4-3",
                            elements=(rmf,
                                      ),
                            )

# telescope 4
@u.quantity_input(mid_energies=u.keV)
def foxsi4_telescope4_arf(mid_energies):
    """The ARF for telescope 4. """
    tb = tp.foxsi4_position4_thermal_blanket(mid_energies) 
    opt = tp.foxsi4_position4_optics(mid_energies) 
    uni_al = tp.foxsi4_position4_uniform_al(mid_energies)

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
                            telescope="foxsi4-4",
                            elements=(tb, 
                                      opt, 
                                      uni_al,
                                      ),
                            )

@u.quantity_input(mid_energies=u.keV, time_range=u.second)
def foxsi4_telescope4_flight_arf(mid_energies, time_range):
    """The flight ARF for telescope 4.
    
    Includes atmospheric attenuation from flight.
    """
    atm = att_foxsi4_atmosphere(mid_energies=mid_energies, 
                                time_range=time_range)
    arf = foxsi4_telescope4_arf(mid_energies)

    flight_arf = atm.transmissions*arf.response

    func_name = sys._getframe().f_code.co_name
    atm.update_function_path(func_name)
    arf.update_function_path(func_name)

    return Response1DOutput(filename="No-File",
                            function_path=func_name,
                            mid_energies=mid_energies,
                            response=flight_arf,
                            response_type="ARF-flight",
                            telescope=f"foxsi4-4",
                            elements=(atm, 
                                      arf,
                                      ),
                            )

@u.quantity_input(pitch=u.um)
def foxsi4_telescope4_rmf(region:int=None, pitch=None, _side:str="merged", _event_type:str="all"):
    """The RMF for telescope 4. """
    
    rmf = tp.foxsi4_position4_detector_response(region=region, 
                                                pitch=pitch, 
                                                _side=_side, 
                                                _event_type=_event_type)
    func_name = sys._getframe().f_code.co_name
    rmf.update_function_path(func_name)

    return Response2DOutput(filename="No-File",
                            function_path=func_name,
                            input_energy_edges=rmf.input_energy_edges,
                            output_energy_edges=rmf.output_energy_edges,
                            response=rmf.detector_response,
                            response_type="RMF",
                            telescope="foxsi4-4",
                            elements=(rmf,
                                      ),
                            )

# telescope 5
@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin)
def foxsi4_telescope5_arf(mid_energies, off_axis_angle):
    """The ARF for telescope 5. """
    tb = tp.foxsi4_position5_thermal_blanket(mid_energies) 
    opt = tp.foxsi4_position5_optics(mid_energies, 
                              off_axis_angle=off_axis_angle) 
    mylar = tp.foxsi4_position5_al_mylar(mid_energies)
    pix_att = tp.foxsi4_position5_pixelated_attenuator(mid_energies)

    arf = tb.transmissions * opt.effective_areas * mylar.transmissions * pix_att.transmissions

    func_name = sys._getframe().f_code.co_name
    tb.update_function_path(func_name)
    opt.update_function_path(func_name)
    mylar.update_function_path(func_name)
    pix_att.update_function_path(func_name)

    return Response1DOutput(filename="No-File",
                            function_path=func_name,
                            mid_energies=mid_energies,
                            response=arf,
                            response_type="ARF",
                            telescope="foxsi4-5",
                            elements=(tb, 
                                      opt, 
                                      mylar,
                                      pix_att,
                                      ),
                            )

@u.quantity_input(mid_energies=u.keV, off_axis_angle=u.arcmin, time_range=u.second)
def foxsi4_telescope5_flight_arf(mid_energies, off_axis_angle, time_range):
    """The flight ARF for telescope 5.
    
    Includes atmospheric attenuation from flight.
    """
    atm = att_foxsi4_atmosphere(mid_energies=mid_energies, 
                                time_range=time_range)
    arf = foxsi4_telescope5_arf(mid_energies, off_axis_angle)

    flight_arf = atm.transmissions*arf.response

    func_name = sys._getframe().f_code.co_name
    atm.update_function_path(func_name)
    arf.update_function_path(func_name)

    return Response1DOutput(filename="No-File",
                            function_path=func_name,
                            mid_energies=mid_energies,
                            response=flight_arf,
                            response_type="ARF-flight",
                            telescope=f"foxsi4-5",
                            elements=(atm, 
                                      arf,
                                      ),
                            )

@u.quantity_input(pitch=u.um)
def foxsi4_telescope5_rmf(region:int=None, pitch=None, _side:str="merged", _event_type:str="all"):
    """The RMF for telescope 5. """
    
    rmf = tp.foxsi4_position5_detector_response(region=region, 
                                                pitch=pitch, 
                                                _side=_side, 
                                                _event_type=_event_type)
    func_name = sys._getframe().f_code.co_name
    rmf.update_function_path(func_name)

    return Response2DOutput(filename="No-File",
                            function_path=func_name,
                            input_energy_edges=rmf.input_energy_edges,
                            output_energy_edges=rmf.output_energy_edges,
                            response=rmf.detector_response,
                            response_type="RMF",
                            telescope="foxsi4-5",
                            elements=(rmf,
                                      ),
                            )

if __name__=="__main__":
    from matplotlib.colors import LogNorm, Normalize
    import matplotlib.gridspec as gridspec
    import matplotlib.pyplot as plt
    import numpy as np

    off_axis_angle = 0 << u.arcmin
    p5_rmf = foxsi4_telescope5_rmf(region=0)
    mid_energies = (p5_rmf.input_energy_edges[:-1]+p5_rmf.input_energy_edges[1:])/2
    p5_arf = foxsi4_telescope5_arf(mid_energies=mid_energies, off_axis_angle=off_axis_angle)
    p5_drm = foxsi4_telescope_response(p5_arf, p5_rmf)

    fig = plt.figure(figsize=(12, 5))
    gs = gridspec.GridSpec(1, 1)

    gs_ax0 = fig.add_subplot(gs[0, 0])
    r = gs_ax0.imshow(p5_drm.response.value, 
                      origin="lower", 
                      norm=LogNorm(vmin=0.001), 
                      extent=[np.min(p5_drm.output_energy_edges.value), 
                              np.max(p5_drm.output_energy_edges.value), 
                              np.min(p5_drm.input_energy_edges.value), 
                              np.max(p5_drm.input_energy_edges.value)]
                      )
    cbar = plt.colorbar(r)
    cbar.ax.set_ylabel(f"Response [{p5_drm.response.unit:latex}]")
    gs_ax0.set_xlabel(f"Count Energy [{p5_drm.output_energy_edges.unit:latex}]")
    gs_ax0.set_ylabel(f"Photon Energy [{p5_drm.input_energy_edges.unit:latex}]")
    gs_ax0.set_title("Linear Scale")
    plt.show()