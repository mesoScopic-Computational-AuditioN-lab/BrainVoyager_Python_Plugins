# BrainVoyager Python Plugins

A collection of python plugins (relying on UI) made for BrainVoyager.
Simply save the python files in the BrainVoyager/Extensions/PythonPlugins or BrainVoyager/Extensions/PythonScripts folder.
Run by clicking `Python` > `Python Development` (or in BrainVoyager press ctrl+p), sellect the script of choice and press `Run`.

For dependencies look at the import section of each script (e.g. bvbabel, nibabel, numpy)

List of available functions:
+ `Isovoxel_Nearest.py` : Tool to IsoVoxel volumes (and VOIs) using Nearest Neighbor interpolation.
+ `Nifti_Tools.py` : Tool to convert most BrainVoyager file formates to and from NIFTI format (and setting space to correct nifti convention).
+ `VOI_Tools.py` : Tool to take BrainVoyager VOI files, and save namings/color values to ITKsnap and 3Dslicer readable file formats.
