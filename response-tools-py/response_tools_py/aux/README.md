# `response_tools_py.aux`

A folder to contain any extra code/processes used for, say, formatting the files we have. Somewhere to document this stuff.

An example of this is scaling some of the values in the new MSFC optics for sources at infinite distance.

## 1. Edits to MSFC 2-shell optics

Performing instructions (email Lindsay->Kris on Wed. 12/03/2025 @ 7:20 pm) on original file (`"FOXSI4_Effective_Areas_2025April11.txt"`):

1. Multiply these areas by that correction factor.
   - Multiply by (1/0.92) to convert to infinite source distance
   - 1 AU = infinite distance, close enough!
2. Add a note to the top of the file.

To actually perform the above:

1. Open original file and remove all the commas (to work with Numpy's `loadtxt`).
   - replace all `","` with `""`
2. Use `format-msfc-eff-areas.py` to scale the values and save out a new file.

Most current MSFC Hi-res effective areas:

- FOXSI4_Module_MSFC_HiRes_EA_with models_v1.txt
