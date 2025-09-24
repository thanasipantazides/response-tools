"""
Function & Outputs
------------------

Script showing a quick example on how to use the functions.

The chosen telescope for the example is Telescope 2 with photon path:
- Thermal blanket -> Marshall 10-shell X-7 -> Al (0.015") -> CdTe4

Mainly a quick example on unit aware objects and how to access the 
returned dataclass objects.

This example shows the use of nice high level functions that are tied to
FOXSI-4 telescopes. 
- responses
- telescope_parts

If you're looking for access to response data of the 
individual components with more freedom then you'll likely be interested 
in the longer named moduels in the package like:
- attenuation
- detector_response
- effective_area
- quantum_efficiency

THIS SCRIPT IS AN EXAMPLE, DO NOT USE DIRECTLY. 
-----------------------------------------------
If you would like to run the contents of this script and play around 
with it then either use this file and be aware of not adding/commiting 
any changes you make and/or just make a copy of this file, put it 
somewhere else on your computer, and play around with the copy.
"""

import numpy as np

"""
For higher level user engagement, the following two modules are the ones 
likely to use. The `telescope_parts` are well-named functions tied to 
FOXSI positions: E.g., `foxsi4_position2_optics` will return FOXSI-4's 
optical information for Position/Telescope 2.

The `responses` module will contains functions that combine the relevant 
`telescope_parts` functions into one to return higher level products 
such as the telescope's Ancillary Response Function (ARF), 
Redistribution Matrix Function (RMF), and/or Detector Response Matrix 
(DRM).
"""

import response_tools_py.responses as responses
import response_tools_py.telescope_parts as telescope_parts

"""
Let's look at the `foxsi4_position2_optics` function since we mentioned
it earlier. To see the documentation for this, and any function, we can 
always run:

```
>>> help(telescope_parts.foxsi4_position2_optics)
Help on function foxsi4_position2_optics in module 
response_tools_py.telescope_parts:

foxsi4_position2_optics(mid_energies, off_axis_angle)
    Position 2 MSFC heritage X-7 optic effective areas.

    Parameters
    ----------
    mid_energies : `astropy.units.quantity.Quantity`
            The energies at which the position 2 optics is required. If 
            `numpy.nan<<astropy.units.keV` is passed then an entry for 
            all native file energies are returned.
            Unit must be convertable to keV.

    off_axis_angle : `astropy.units.quantity.Quantity`
            The off-axis angle of the source.
            Unit must be convertable to arc-minutes.
            
    Returns
    -------     
    : `effective_area.EffAreaOutput`
            An object containing the effective area information of the 
            MSFC heritage X-7 optic. See accessible information using 
            `.contents` on the output.
(END)
```

We can see that the help function tells us about the function, how to 
use it, and what it returns. The above function is looking for some
energies and an off-axis angle.

It shows that one thing we're making use of here are unit aware inputs 
to functions (believe me, when it comes to response units, this will 
save time). 

So let's import Astropy's unit module.
"""

import astropy.units as u

"""
Let's choose a sensible energy array and off-axis angle (remembering to 
add the units to the array/value):
"""

mid_energies = np.arange(4,20,0.5) << u.keV 
off_axis_angle = 0 << u.arcmin
pos2_optics = telescope_parts.foxsi4_position2_optics(mid_energies, 
                                                      off_axis_angle)

"""
One great thing about the unit-awareness of the inputs/outputs is that 
you can pass any reasonable input units and they'll be converted for you
so you don't need to worry about conversion factors throughout your code
to use the functions.

E.g., the following will result in the same function output
"""

mid_energies_eV = np.arange(4_000,20_000,500) << u.eV 
off_axis_angle_arcsec = 0 << u.arcsec
_pos2_ = telescope_parts.foxsi4_position2_optics(mid_energies_eV, 
                                                 off_axis_angle_arcsec)

"""
I.e., `pos2_optics` and `_pos2_` are identical.

You can also access just the value or just the unit from a unit-aware 
object with `.value` or `.unit` as well. This can useful for axis labels
when necessary.

The output of `pos2_optics` (an `pos2_optics_new`) isn't just an array 
now, it's a dataclass. The dataclass contains the effective areas of the 
optics but also the energy, file, off-axis angle information used to 
produce it. This is crucial to track when there are a lot of files 
flying around.

As suggested in the "Output" section of the helpful documentation 
earlier, we can see the contents of the dataclass and how to access the 
information within it:
"""

print(pos2_optics.contents)

"""
The above should produce something like:

```
{'filename': 'some-long-file-path-and-name',
 'function_path': 'eff_area_msfc_10shell\n->foxsi4_position2_optics',
 'mid_energies': <Quantity [ 4. ,  4.5,  5. ,  5.5,  6. ,  6.5,  7. ,  
            7.5,  8. ,  8.5,   9. ,  9.5, 10. , 10.5, 11. , 11.5, 12. , 
            12.5, 13. , 13.5, 14. , 14.5, 15. , 15.5, 16. , 16.5, 17. , 
            17.5, 18. , 18.5, 19. , 19.5] keV>,
 'off_axis_angle': <Quantity 0. arcmin>,
 'effective_areas': <Quantity [        nan, 25.6       , 25.72057417, 
            25.7       , 25.41348566, 25.2       , 25.43761831, 
            25.8       , 25.81248981, 25.6       , 25.40025845, 
            24.8       , 23.53212343, 21.72665134, 19.4       ,
            16.63423381, 13.70639236, 10.92535473,  8.6       ,  
            6.93807847,   5.82109618,  5.06856579,  4.5       ,  
            3.96451406,  3.45878343,   3.02366109,  2.7       ,  
            2.48516453,  2.32308489,  2.1744628 ,   2.        ,  
            1.76986129] cm2>,
 'optic_id': 'X-7',
 'model': False}
```

Note: there is a method called `print_contents()` you can use on the 
function output that might format the contents a little nicer than the
above you may wish to use.

Each field can be accessed with the displayed name. For excample, to get
the effective areas of the optics, simply:
"""

print(pos2_optics.effective_areas)

"""
Notice that these are also unit-aware, help you see at a glance you're 
working with a product that you might expect.

The `telescope_parts.foxsi4_position2_optics` function is helpful but an
even higher level exists that will allow a user to specify a FOXSI-4 
telescope to obtain the Ancillary Response Function (ARF), 
Redistribution Matrix Function (RMF), and/or Detector Response Matrix 
(DRM).

First, we can get the RMF for a telescope, say, Telescope 2:
"""

pos2_rmf = responses.foxsi4_telescope2_rmf(region=0)

"""
The `region` input refers to the different pitch regions across the CdTe
detectors. IF you would rather specificy by passing the pitch (that is
unit aware) then practice running `help` on the function and check the 
documentation.

The RMF defined the input and output energy axes for the detector so we
might as well access the RMF input energies for those energies we want 
the ARF values for:
"""

mid_energies = (pos2_rmf.input_energy_edges[:-1]\
                +pos2_rmf.input_energy_edges[1:])/2
pos2_arf = responses.foxsi4_telescope2_arf(mid_energies=mid_energies, 
                                           off_axis_angle=0<<u.arcmin)

"""
Once we have the RMF and ARF for a given instrument, you might want to 
just see what the total DRM is. This can be done by passing the ARF and 
RMF to the general `responses.foxsi4_telescope_response` function:
"""

pos2_drm = responses.foxsi4_telescope_response(pos2_arf, pos2_rmf)

"""
Note that with the FOXSI-4 Telescope fucntions (`foxsi4_telescope*`), 
there exists a field in the class called `elements`. This field contains
all the dataclasses used to produce the objects `response` field.

Checking the `elements` field for, say, the ARF object:
"""

print(pos2_arf.elements)

"""
We find that the `elements` field contains all the dataclasses that 
produced the Telescope 2 ARF such as the thermal blanket transmission 
(dimensionless), the Marshall 10-shell X-7 optics effective areas 
(cm**2), and the Al (0.015") attenuator transmissions (dimensionless).
"""