"""
Plotting ARFs, RMFs, and DRMs
-----------------------------

Script showing a quick example how to plot the Ancillary Response 
Function (ARF), Redistribution Matrix Function (RMF), and the Detector 
Response Matrix (DRM) of a FOXSI-4 telescope.

The chosen telescope is Telescope 2 with photon path:
- Thermal blanket -> Marshall 10-shell X-7 -> Al (0.015") -> CdTe4

If you would like to run the contents of this script and play around 
with it then either use this file and be aware of not adding/commiting 
any changes you make and/or just make a copy of this file, put it 
somewhere else on your computer, and play around with the copy.
"""

import astropy.units as u
from matplotlib.colors import LogNorm
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np

import response_tools.responses as responses

fig = plt.figure(figsize=(18, 5))
gs = gridspec.GridSpec(1, 3)

# set up the ARF with the RMF information then make the DRM
off_axis_angle = 0 << u.arcmin
pos_rmf = responses.foxsi4_telescope2_rmf(region=0)
mid_energies = (pos_rmf.input_energy_edges[:-1]\
                +pos_rmf.input_energy_edges[1:])/2
pos_arf = responses.foxsi4_telescope2_arf(mid_energies=mid_energies, 
                                          off_axis_angle=off_axis_angle)
pos_drm = responses.foxsi4_telescope_response(pos_arf, pos_rmf)

# the ARF info
gs_ax0 = fig.add_subplot(gs[0, 0])
gs_ax0.plot(pos_arf.mid_energies, pos_arf.response)
gs_ax0.set_xlabel(f"Photon Energy [{pos_arf.mid_energies.unit:latex}]")
gs_ax0.set_ylabel(f"Response [{pos_arf.response.unit:latex}]")
gs_ax0.set_title(f"Telescope 2: ARF")

# the RMF info
gs_ax1 = fig.add_subplot(gs[0, 1])
r = gs_ax1.imshow(pos_rmf.response.value, 
                origin="lower", 
                norm=LogNorm(vmin=0.001), 
                extent=[np.min(pos_rmf.output_energy_edges.value), 
                        np.max(pos_rmf.output_energy_edges.value), 
                        np.min(pos_rmf.input_energy_edges.value), 
                        np.max(pos_rmf.input_energy_edges.value)]
                )
cbar = plt.colorbar(r)
cbar.ax.set_ylabel(f"Response [{pos_rmf.response.unit:latex}]")
gs_ax1.set_xlabel(f"Count Energy [{pos_rmf.output_energy_edges.unit:latex}]")
gs_ax1.set_ylabel(f"Photon Energy [{pos_rmf.input_energy_edges.unit:latex}]")
gs_ax1.set_title(f"Telescope 2: RMF")

# the DRM info
gs_ax2 = fig.add_subplot(gs[0, 2])
r = gs_ax2.imshow(pos_drm.response.value, 
                origin="lower", 
                norm=LogNorm(vmin=0.001), 
                extent=[np.min(pos_drm.output_energy_edges.value), 
                        np.max(pos_drm.output_energy_edges.value), 
                        np.min(pos_drm.input_energy_edges.value), 
                        np.max(pos_drm.input_energy_edges.value)]
                )
cbar = plt.colorbar(r)
cbar.ax.set_ylabel(f"Response [{pos_drm.response.unit:latex}]")
gs_ax2.set_xlabel(f"Count Energy [{pos_drm.output_energy_edges.unit:latex}]")
gs_ax2.set_ylabel(f"Photon Energy [{pos_drm.input_energy_edges.unit:latex}]")
gs_ax2.set_title(f"Telescope 2: DRM")

plt.tight_layout()
plt.show()