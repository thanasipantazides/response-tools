# `response-tools` for FOXSI-4  <span>&#129418;</span>

Repository to manage response elements, originally for the FOXSI-4 sounding rocket mission but it can be extended.

**See below on contributing to the repository.**

**Note:** Although this repositiory can be extanded to any other instrument (e.g., FOXSI-1, -2, and -3), this repository is only currently aimed for FOXSI-4 use.

## Response files

There are many response elements for FOXSI-4. Once downloaded, they can be places or found [here](./response-information/).

We can describe various aspect like versioned filename (official one to use), original filename, description, etc.

We can group them in which telescope they belonged to in FOXSI-4 and order them with regards to the photon path. This list should be kept up-to-date.

For a historical description of the response files below (old versions, etc.), see the [README in response-information](./response-information/README.md).

### Position 0 (SXR, CMOS1)

- **Optical blocking filter:** `"foxsi4_telescope-0_BASIC_optical_blocking_filter_transmittance_v1.fits"`
  - _Description:_
- **Collimator:** `"foxsi4_telescope-0_BASIC_collimator_aperture_ratio_v1.fits"`
- **Optics:** `""`
- **Filter:** `"foxsi4_telescope-0_BASIC_attenuation_filter_transmittance_v1.fits"`
- **Detector response:** ""
  - **Quantum efficiency:** ""

![Position 0 photon path](./assets/response-tools-py-figs/response-paths/Pos_0_CMOS_1_Response.png "Position 0 photon path")

### Position 1 (SXR, CMOS2)

- **Optical blocking filter:** `"foxsi4_telescope-1_BASIC_optical_blocking_filter_transmittance_v1.fits"`
- **Collimator:** `"foxsi4_telescope-1_BASIC_collimator_aperture_ratio_v1.fits"`
- **Optics:** ""
- **Filter:** `"foxsi4_telescope-1_BASIC_attenuation_filter_transmittance_v1.fits"`
- **Detector response:** ""
  - **Quantum efficiency:** ""

![Position 1 photon path](./assets/response-tools-py-figs/response-paths/Pos_1_CMOS_2_Response.png "Position 1 photon path")

### Position 2 (HXR, CdTe4)

- **Thermal blanket:** ""
- **Optics:** ""
- **Filter:** ""
- **Detector response:** ""

![Position 2 photon path](./assets/response-tools-py-figs/response-paths/Pos_2_CdTe_4_Response.png "Position 2 photon path")

### Position 3 (HXR, CdTe2)

- **Thermal blanket:** ""
- **Optics:** ""
- **Filter:** ""
- **Pixelated attenuator:** ""
- **Detector response:** ""

![Position 3 photon path](./assets/response-tools-py-figs/response-paths/Pos_3_CdTe_2_Response.png "Position 3 photon path")

### Position 4 (HXR, CdTe3)

- **Thermal blanket:** ""
- **Optics:** ""
- **Filter:** ""
- **Detector response:** ""

![Position 4 photon path](./assets/response-tools-py-figs/response-paths/Pos_4_CdTe_3_Response.png "Position 4 photon path")

### Position 5 (HXR, CdTe1)

- **Thermal blanket:** ""
- **Optics:** ""
- **Filter:** ""
- **Pixelated attenuator:** ""
- **Detector response:** ""

![Position 5 photon path](./assets/response-tools-py-figs/response-paths/Pos_5_CdTe_1_Response.png "Position 5 photon path")

### Position 6 (Timepix)

- N/A

## Software and software help

The repository may make use of multiple languages and each folder like `response-tools-???` hosts code in their respective languages relating to response tools. These include:

- [`response-tools-py`](response-tools-py/) which contains Python code to download and read in the response files.
  - The README in this directory also contains Python specific information & help

## Example code

There are a few existing example scripts showing how to use a lot of tools in the repository.

**Python examples:** Python example scripts can be found in response-tools-py [examples](response-tools-py/examples/) folder which has an associated [README file](response-tools-py/examples/README.md).

## Repository Aim

This repository will contain all code that proves useful in loading FOXSI response elements (at least from FOXSI-4). Several languages might be used and so the top level will be to contain language specific packages.

For example, the `response-tools-py` folder will be a Python package containing all the necessary `.py` files. If other languages are to be included, like `IDL`, then a folder called `response-tools-idl` should be created and used to contain all the `IDL`-ness of the repository. This standard can be applied to the inclusion of other languages (e.g., C++ as `response-tools-cpp`, Shell code as `response-tools-shell`, etc.).

Every `response-tools-<?>` folder should have an "examples" and a "tests" folder. The "examples" folder is a great place to include scripts that show how some of the code in the repository works and the "tests" folder is a fantastic place to put code that tests the tools that have been created.

Additionally, there is also an "examples" and "tests" folder in the top level of the repository so there is a place for anything that fits these folders that spans across code from multiple languages.

## Contributing to the repository

Thank you so much for considering to contribute to the repository! <span>&#127881;</span>

In order to contribute, we ask that you first create your own fork of the repository and then clone that fork to your local machine. Branches of your new fork can be created to develop new features or fix bugs (exciting!). When you are happy with the code in that new branch, a pull request (PR) can be opened which aims to merge the code in your fork's branch into the `main` `foxsi/response-tools` repository. A lot of discussion can be facilitated in an open PR.

**Note:** We aim to _never_ `push` from a local machine to this repository directly. If this happens then it can be very difficult for other contributers to understand what changes are being made and how it affects their own PRs. _If the repository is pushed to directly, in order to help track changes and make them visible to other contributers, the repository will be reverted back to it's state before the push and the undone changes will be asked to be proposed via a PR to then be merged._

## The `external` directory

The `external` directory is a place for software external to the repository. There is no guarentee that it will follow any specific coding language and so it would perhaps not be ideal to place it in a specific coding language `tools` directory. Some may be [`git` submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules).

To clone submodules when cloning the main repository, try the following:

- `git clone --recurse-submodules https://github.com/foxsi/response-tools.git`

## The `response-information` directory

This directory contains context information about the response files that can be shared between a lot of different scripts. E.g., the latest versions of the files the code should be using.

## Versioning

The versioning approach for all code, files, and data products is [semantic versioning](https://en.wikipedia.org/wiki/Software_versioning#Semantic_versioning).

This means that we represent the item with one-three digits indicating `major`.`minor`.`patch` changes made. Files will likely only use the `major` value.

- `major`: Increment to include breaking changes from previous versions.
  - E.g., the file's data changes or the pre-existing code's behaviour is changed and is no longer backwards compatible.
- `minor`: Increment to include new additions to the item.
  - E.g., the file now includes new additional data or the code has new tools.
- `patch`: Increment to include all other small changes.
  - E.g., the file has small details added, like some metadata, or the code has had a couple of small typo fixes.
