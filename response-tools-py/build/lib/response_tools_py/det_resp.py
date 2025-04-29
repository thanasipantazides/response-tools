"""Code to load different detectro responses. """

import logging
import os
import pathlib

from astropy.io import fits
import astropy.units as u
from matplotlib.colors import LogNorm, Normalize
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np

def cdte_det_resp_rmf(file):
    """Return the redistribution matrix from a given file."""
    e_lo, e_hi, ngrp, fchan, nchan, matrix = _read_rmf(file)

    fchan_array = col2arr_py(fchan)
    nchan_array = col2arr_py(nchan)

    return e_lo<<u.keV, e_hi<<u.keV, vrmf2arr_py(data=matrix,
                                                 n_grp_list=ngrp,
                                                 f_chan_array=fchan_array,
                                                 n_chan_array=nchan_array)<<(u.ct/u.ph)

def cmos_det_resp(file=None, telescope=None):

    if telescope is None:
        logging.warning("`telescope` input in cmos_det_resp()` must be 0 or 1.")
        return
        
    _f = os.path.join(pathlib.Path(__file__).parent, 
                            "det-resp-data", 
                            "cmos", 
                            f"foxsi4_telescope-{telescope}_BASIC_RESPONSE_MATRIX_V25APR13.fits") if file is None else file
    
    with fits.open(_f) as hdul:
        matrix, counts, energy = hdul[1].data<<(u.ct/u.ph), hdul[2].data<<u.dimensionless_unscaled, hdul[3].data<<u.keV # units?
    return counts, energy, matrix 

def _read_rmf(file):
    """
    Read a .rmf file and extract useful information from it.

    Parameters
    ----------
    file :  `str`, `file-like` or `pathlib.Path`
        A .rmf file (see `~astropy.fits.io.open` for details).

    Returns
    -------
    `tuple`
        The low and high boundary of energy bins (data['energ_lo'], 
        data['energ_hi']), number of sub-set channels in the energybin 
        (data['n_grp']), starting index of each sub-set of channels 
        (data['f_chan']),number of channels in each sub-set 
        (data['n_chan']), redistribution matrix [counts per photon] 
        (data['matrix']).
    """

    with fits.open(file) as hdul:
        data = hdul[2].data

    return data["energ_lo"], data["energ_hi"], data["n_grp"], data["f_chan"], data["n_chan"], data["matrix"]

def col2arr_py(data):
    """Takes a list of parameters for each energy channel from a .rmf 
    file and returns it in the correct format.

    From: https://lost-contact.mit.edu/afs/physics.wisc.edu/home/craigm/lib/idl/util/vcol2arr.pro

    **This original function is taken from Sunkit-spex**
    - https://github.com/sunpy/sunkit-spex
    - Tweaked to change `r` below to `[r]` since the values in data 
    aren't lists (e.g., NuSTAR)

    Parameters
    ----------
    data : array/list-like object
            One parameter's array/list from the .rmf file.

    Returns
    -------
    A 2D numpy array of the correctly ordered input data.

    Example
    -------
    data = FITS_rec([(  1.6 ,   1.64,   1, [0]   , [18]  , [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]),
                     (  1.64,   1.68,   1, [0]   , [20]  , [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]),
                     (  1.68,   1.72,   2, [0,22], [20,1], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]),
                     dtype=(numpy.record, [('ENERG_LO', '>f4'), ('ENERG_HI', '>f4'), ('N_GRP', '>i2'),
                                           ('F_CHAN', '>i4', (2,)), ('N_CHAN', '>i4', (2,)), ('MATRIX', '>i4', (2,))]))

     col2arr_py(data['F_CHAN'])
    array([[  0.,   0.],
           [  0.,   0.],
           [  0.,  22.]])
    ## max row length of 2 so 2 columns, each row is an energy channel.
    """

    # this is the quicker way I have chosen to do in Python (this may be revised later but is ~30x faster than way below in Python)
    max_len = np.max([len([r]) for r in data])  # find max row length
    chan_array_py = np.array(
        [[*[r], *(max_len - len([r])) * [0]] for r in data]
    )  # make each row that length (padding with 0)

    return chan_array_py

def vrmf2arr_py(data=None, n_grp_list=None, f_chan_array=None, n_chan_array=None):
    """Takes redistribution parameters for each energy channel from a 
    .rmf file and returns it in the correct format.

    From: https://lost-contact.mit.edu/afs/physics.wisc.edu/home/craigm/lib/idl/spectral/vrmf2arr.pro

    **This original function is taken from Sunkit-spex**
    - https://github.com/sunpy/sunkit-spex

    Parameters
    ----------
    data : array/list-like object
            Redistribution matrix parameter array/list from the .rmf file. Units are counts per photon.
            Default : None

    no_of_channels : int
            Number of entries is the total number of photon channels, the entries themselves show the total number
            of count channels to which that photon channel contributes.
            Default : None

    f_chan_array : numpy.array
            The index of each sub-set channel from each energy bin from the .rmf file run through col2arr_py().
            Default : None

    n_chan_array : numpy.array
            The number of sub-set channels in each index for each energy bin from the .rmf file run through col2arr_py().
            Default : None

    Returns
    -------
    A 2D numpy array of the correctly ordered input data with dimensions of energy in the rows and channels in
    the columns.

    Example
    -------
     d_rmf = 'directory/'
     f_rmf = 'file.rmf'
     e_lo, e_hi, ngrp, fchan, nchan, matrix = det_io._read_rmf(d_rmf+f_rmf)

     fchan_array = nu_spec.col2arr_py(fchan)
     nchan_array = nu_spec.col2arr_py(nchan)

     rmf = nu_spec.vrmf2arr_py(data=matrix,
                                  n_grp_list=ngrp,
                                  f_chan_array=fchan_array,
                                  n_chan_array=nchan_array)
     rmf

    array([[0.00033627, 0.0007369 , 0.00113175, ..., 0.        , 0.        , 0.        ],
           [0.00039195, 0.00079259, 0.00138341, ..., 0.        , 0.        , 0.        ],
           [0.00042811, 0.00083381, 0.00157794, ..., 0.        , 0.        , 0.        ],
                                                ...,
           [0.        , 0.        , 0.        , ..., 0.00408081, 0.00409889, 0.00403308],
           [0.        , 0.        , 0.        , ..., 0.00405333, 0.00413722, 0.00413216],
           [0.        , 0.        , 0.        , ..., 0.        , 0.        , 0.        ]])
    ## rows = photon/energy channels, columns = counts channels

    What's Going On?
    ----------------
    The RMF file has the photon-to-counts conversion information in it.
    The martix has the photon-to-count conversion value for each count channel (columns) that is involved with theach photon channel (rows).
            E.g., matrix = [ [a, b, c, d, e, f, ...] ,
                             [        ...          ] ,
                             [        ...          ] ,
                                      ...             ]
    F_chan is the starting index of contiguous counts channels that are involved with the photon channel.
            E.g., f_chan = [ [0, 5, 0, 0, 0, ...] ,
                             [       ...        ] ,
                             [       ...        ] ,
                                     ...           ]
                            For the first photon channel, there are rows of counts channels starting at index 0 and 5
    N_chan is the corresponding number of counts channels from each index in the f_chan array.
            E.g., n_chan = [ [2, 3, 0, 0, 0, ...] ,
                             [        ...        ] ,
                             [        ...        ] ,
                                      ...           ]
                            Starting at index 0 for the first photon channel we have the first 2 matrix values, then at index 5 we have the next 3.
                            The total of each row is the same as the n_grp_list and the number of entries in each row of the matrix entry.
    Putting all this together, the rmf matrix is:
            rmf_matrix = [ [a, b, 0, 0, 0, c , d , e, 0 , 0 , ...] ,   #<-- index 0 (f_chan) with 2 entries (n_chan) with photon-to-counts conversion (matrix)
                         [                 ...                   ] ,
                         [                 ...                   ] ,
                                           ...                      ]
    """
    # this was is about >6x quicker in than the IDL code written in Python

    n_grp_list = n_grp_list.astype("<i2")  # change from ‘big-endian’ (">i2") to ‘little-endian’ ("<i2")

    # find the non-zero entries in Nchan, this is the number to counts channels
    #  in a row that contribute so will have a value if it is useful
    b = np.nonzero(n_chan_array)

    # now only want the useful entries from the pre-formatted Nchan and Fchan arrays
    c = f_chan_array[b]
    d = n_chan_array[b]

    # to help with indexing, this provides a running sum of the number of counts
    #  channels that a single photon channel contributes to
    e = np.cumsum(n_chan_array, axis=1)

    # these entries will give the final indices in the row on counts channels
    final_inds = e[b]

    # need to find the starting index so -1, but that means any entry that is
    #  -1 will be where a zero is needed
    starting_inds = b[1] - 1

    # get the  starting indices but the ones that should be 0 are replaced with
    #  the final one in the list at the minute (-1 in starting_inds)
    start_inds = np.cumsum(n_chan_array, axis=1)[(b[0], starting_inds)]

    # where starting_inds==-1 that value should be 0, i.e. starting from the first
    #  value in the rmf matrix
    new_e = np.where(starting_inds != -1, start_inds, 0)

    # initialise the rmf matrix
    mat_array_py = np.zeros((len(data), len(n_grp_list)))

    # now go through row by row (this is the slowest part and needs to be made faster).
    #  Here we go through each photon channel's number of discrete rows of counts channels.
    for r in range(len(c)):
        mat_array_py[b[0][r], c[r] : c[r] + d[r]] = data[b[0][r]][new_e[r] : final_inds[r]]

    return mat_array_py


if __name__=="__main__":

    SAVE_ASSETS = False
    assets_dir = os.path.join(pathlib.Path(__file__).parent, "..", "..", "assets", "response-tools-py-figs", "det-resp-figs")
    pathlib.Path(assets_dir).mkdir(parents=True, exist_ok=True)

    # CMOS
    fig = plt.figure(figsize=(12,7))

    gs = gridspec.GridSpec(1, 2)
    gs_ax0 = fig.add_subplot(gs[0, 0])
    telescope = 0
    c, e, m = cmos_det_resp(file=None, telescope=telescope)
    extent = [np.min(c.value), np.max(c.value), np.min(e.value), np.max(e.value)]
    i = gs_ax0.imshow(m.value, origin="lower", aspect=(extent[1]-extent[0])/(extent[3]-extent[2]), extent=extent, norm=LogNorm())
    gs_ax0.set_ylim([0,10])
    gs_ax0.set_xlabel("Counts?")
    gs_ax0.set_ylabel(f"Energy? [{e.unit:latex}]")
    gs_ax0.set_title(f"CMOS{telescope}")
    cax = gs_ax0.inset_axes([0.1, 0.08, 0.8, 0.05],)
    cbar = fig.colorbar(i, cax=cax, orientation='horizontal')
    cbar.set_label(f"{m.unit:latex}?", size=8, labelpad=0)
    cax.tick_params(axis='both', which='major', labelsize=6)


    gs_ax1 = fig.add_subplot(gs[0, 1])
    telescope = 1
    c, e, m = cmos_det_resp(file=None, telescope=telescope)
    extent = [np.min(c.value), np.max(c.value), np.min(e.value), np.max(e.value)]
    i = gs_ax1.imshow(m.value, origin="lower", aspect=(extent[1]-extent[0])/(extent[3]-extent[2]), extent=extent, norm=LogNorm())
    gs_ax1.set_ylim([0,10])
    gs_ax1.set_xlabel("Counts?")
    gs_ax1.set_ylabel(f"Energy? [{e.unit:latex}]")
    gs_ax1.set_title(f"CMOS{telescope}")
    cax = gs_ax1.inset_axes([0.1, 0.08, 0.8, 0.05],)
    cbar = fig.colorbar(i, cax=cax, orientation='horizontal')
    cbar.set_label(f"{m.unit:latex}?", size=8, labelpad=0)
    cax.tick_params(axis='both', which='major', labelsize=6)

    plt.tight_layout()
    if SAVE_ASSETS:
        plt.savefig(os.path.join(assets_dir,"cmos-response-matrices.png"), dpi=200, bbox_inches="tight")
    plt.show()

    # CdTe
    d_rmf = "./det-resp-data/cdte/merged/"
    d_rmf = "./det-resp-data/cdte/pt/"
    f_rmf = "Resp_3keVto30keV_CdTe1_reg0_1hit.rmf"


    e_lo, e_hi, rmf = cdte_det_resp_rmf(os.path.join(pathlib.Path(__file__).parent, d_rmf, f_rmf))

    fig = plt.figure(figsize=(12, 5))
    gs = gridspec.GridSpec(1, 2)

    gs_ax0 = fig.add_subplot(gs[0, 0])
    r = gs_ax0.imshow(rmf.value, origin="lower", norm=Normalize(vmin=0.001, vmax=0.12), extent=[np.min(e_lo.value), np.max(e_lo.value), np.min(e_lo.value), np.max(e_lo.value)])
    cbar = plt.colorbar(r)
    cbar.ax.set_ylabel('Counts photon$^{-1}$')
    fig.suptitle(d_rmf+f_rmf)
    gs_ax0.set_xlabel("Count Energy [keV]")
    gs_ax0.set_ylabel("Photon Energy [keV]")
    gs_ax0.set_title("Linear Scale")

    gs_ax0 = fig.add_subplot(gs[0, 1])
    r = gs_ax0.imshow(rmf.value, origin="lower", norm=LogNorm(vmin=0.001, vmax=0.12), extent=[np.min(e_lo.value), np.max(e_lo.value), np.min(e_lo.value), np.max(e_lo.value)])
    cbar = plt.colorbar(r)
    cbar.ax.set_ylabel('Counts photon$^{-1}$')
    fig.suptitle(d_rmf+f_rmf)
    gs_ax0.set_xlabel("Count Energy [keV]")
    gs_ax0.set_ylabel("Photon Energy [keV]")
    gs_ax0.set_title("Log Scale")

    if SAVE_ASSETS:
        plt.savefig(os.path.join(assets_dir,"cdte-response-matrix.png"), dpi=200, bbox_inches="tight")
    plt.show()