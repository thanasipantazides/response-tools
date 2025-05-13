"""
After taking the original file "./FOXSI4_Effective_Areas_2025April11.txt"
and doing a find-and-replace on any commas to remove them, the following
code was used.
"""

import numpy as np

if __name__=="__main__":
    SACLE2INF = 1/0.92

    # get the transpose so it's easier to check the numbers by eye
    e, *fms = np.loadtxt("./FOXSI4_Effective_Areas_2025April11_commasRemoved.txt").T

    new_fms = np.array(fms[:3]) * SACLE2INF

    SCALED = np.concatenate((e[None,:],new_fms,fms[3:]), axis=0).T

    HEADER = """Original file: FOXSI4_Effective_Areas_2023Oct26-removedComma.txt
    Measured areas scaled by 1/0.92 to correct for "finite source distance"
    [Effective areas as measured at SLTF at 104m finite source distance to X-ray node]
    SDD detector areas of 4.0mm radius were used for the effective area calculations
    Energy[keV] FM1[cm2] FM2[cm2] FM3[cm2] FM1_model[cm2] FM2_model[cm2] FM3_model[cm2] """

    np.savetxt("./FOXSI4_Module_MSFC_HiRes_EA_with_models_v1.txt", SCALED, header=HEADER)