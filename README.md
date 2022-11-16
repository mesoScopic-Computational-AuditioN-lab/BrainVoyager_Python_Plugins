# BrainVoyager Python Plugins

A collection of python plugins (relying on UI) made for BrainVoyager.
Simply save the python files in the BrainVoyager/Extensions/PythonPlugins or BrainVoyager/Extensions/PythonScripts folder.
Run by clicking `Python` > `Python Development` (or in BrainVoyager press ctrl+p), sellect the script of choice and press `Run`.

For dependencies look at the import section of each script (e.g. bvbabel, nibabel, numpy)

List of available functions:
+ `Isovoxel_Nearest.py` : Tool to IsoVoxel volumes (and VOIs) using Nearest Neighbor interpolation.
+ `Nifti_Tools.py` : Tool to convert most BrainVoyager file formates to and from NIFTI format (and setting space to correct nifti convention).
+ `VOI_Tools.py` : Tool to take BrainVoyager VOI files, and save namings/color values to ITKsnap and 3Dslicer readable file formats.
+ `VTC_BOX.py`: Tool to quickly load the header information from a .vtc file, and draw a nifti bounding box based on it (usefull for manual segmenation - to see the bounds of your functional data).

-------------------------------------------------------------------

Windows users: 
`bvbabel` isnt always playing ball when intalling within a conda environment, a solution is to manually copy paste the bvbabel directory somewhere and within the scripts (before `import bvbabel`) add `import sys` & `sys.path.append('C:/path/to/parentdirectory/ofbvbabel')`.
When using this approach, please remove the last two lines of code from the `__init__.py` file within the bvbabel folder (starting from `import pkg_resources`).
