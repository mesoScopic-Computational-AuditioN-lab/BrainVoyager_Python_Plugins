import PythonQt.Qt as Qt
from PythonQt.QtGui import *
import traceback

import re
import numpy as np  
from os.path import join
import os

## MAIN SELLECTION FUNCTIONS
def run_samp(): 
    """Main function"""  
    
    # get fns and directories
    curdir = dir_txt.text
    vmr_pf = vmr_txt.text
    srf_fn = srf_txt.text
    vmp_fn = vmp_txt.text
    
    # vmp fns
    smp_fn = re.match(r'^(.*)\.vmp$', vmp_fn).group(1)
    
    # fetch interpolation method
    interpolation_method = int(buttons['im'].value)
    
    # fetch nonzero bool
    sample_only_nonzero_values = buttons['NONZERO_bool'].isChecked()
    
    if buttons['LH_bool'].isChecked(): 
        # set hamisphere
        hemisphere = 'LH'
        # vmr and vmp fns
        vmr_fn = f'{vmr_pf}_{hemisphere}.vmr'
        
        # sample depths
        map_fns = sample_depths(curdir, vmr_fn, vmp_fn, srf_fn, hemisphere, 
                    interpolation_method, sample_only_nonzero_values)
        
        # combine smp maps if wanted
        if buttons['COMBSMPS_bool'].isChecked(): combine_smps(map_fns)

    if buttons['RH_bool'].isChecked():
        hemisphere = 'RH'
        # vmr and vmp fns
        vmr_fn = f'{vmr_pf}_{hemisphere}.vmr'
        
        # sample depths
        map_fns = sample_depths(curdir, vmr_fn, vmp_fn, srf_fn, hemisphere, 
                    interpolation_method, sample_only_nonzero_values)
        
        # combine smp maps if wanted
        if buttons['COMBSMPS_bool'].isChecked(): combine_smps(map_fns)
 
    return

def runhelp():
    msg.exec_()
    
   
def sample_depths(dir_folder, vmr_fn, vmp_fn, srf_fn, hemisphere, 
                interpolation_method, sample_only_nonzero_values):

    # open the vmr and link vmp
    doc = bv.open(join(dir_folder, vmr_fn))
    doc.load_maps(join(dir_folder, vmp_fn))
    doc.show_map(0)

    # regex pattern
    pattern = f'^.*{srf_fn}.*_{hemisphere}_.*_D-\d+.*\.srf$'
    r = re.compile(pattern)

    # get all filenames and filter to only include items of interest
    fns = os.listdir(dir_folder)
    fns = list(filter(r.match, fns))
    
    # update user
    bv.print_to_log(f'Sampling VMPs in Depths ({len(fns)} depths found) \n -Filenames that follow stated naming convention: {fns}\n -Sampling: {vmp_fn}')

    # loop over depth meshes
    map_fns = []
    for depth_mesh in fns:    

        # load srf
        bv.print_to_log(f'loading depth mesh: {depth_mesh}, sampling {vmp_fn} from depth map')
        doc.load_mesh(depth_mesh)

        # capture prefix naming conv - gen smp filename
        mesh_map_prefix = re.search(r'(D(?!.*_D)[^W]*)(?=\.srf)', depth_mesh)[0] 
        smp_fn_depth = f'{smp_fn}_{hemisphere}_{mesh_map_prefix}.smp'
        
        # check if target smp already exists
        if os.path.exists(join(dir_folder, smp_fn_depth)):
            # gen new fn - adding COPY
            bv.print_to_log(f"Warning: file {smp_fn_depth}, saving as '_COPY'")
            fn_prefix = re.match(r'^(.*)\.smp$', smp_fn_depth).group(1)
            smp_fn_depth = f'{fn_prefix}_COPY.smp'        

        # create the surface maps in depth
        mesh = doc.current_mesh
        mesh.create_map_from_volume_map(interpolation_method, sample_only_nonzero_values)
        map_fn = join(dir_folder, smp_fn_depth)
        mesh.save_maps(map_fn)
        map_fns.append(map_fn)
    return map_fns

def combine_smps(map_fns):
    """function to combine smp maps into one smp file"""

    import bvbabel 

    # predefine
    totalnr_maps = 0
    all_maps = []
    all_data = []

    # loop over fns
    for fn in map_fns:

        # load bv smp file
        head, data_smp = bvbabel.smp.read_smp(fn)
    
        # append new number of maps
        totalnr_maps += head['Nr maps']
    
        # capture suffix and add to header
        mesh_map_prefix = re.search(r'(D(?!.*_D)[^W]*)(?=\.smp)', fn)[0] 
        for i in range(len(head['Map'])):
            head['Map'][i]['Name'] = f"{head['Map'][i]['Name']}_{mesh_map_prefix}"
    
        # append
        all_maps.extend(head['Map'])
        all_data.append(data_smp)

    # make copy for saving and appending to
    newhead = head.copy()
    # update number of maps
    newhead['Nr maps'] = totalnr_maps
    newhead['Map'] = all_maps

    # update new data
    newdata_smp = np.concatenate(all_data, axis=1)

    # update filename
    new_fn = re.search(r"^(.*?)_D-", map_fns[0]).group(1)
    new_fn = f'{new_fn}_comb.smp'

    # save
    bvbabel.smp.write_smp(new_fn, newhead, newdata_smp)

## ------------------------------------------------------------------------------ ##

# set global variables for use in functions
global curdir
global vmrfn
global vmpfn
global srffn
global lh
global rh 
global buttons

# see if a brainvoyager file is opened and use its parameters for text input defaults
try:
    doc = bv.active_document
    curdir = doc.path
    vmrfn = doc.file_name
except: 
    curdir = "..."
    vmrfn = "..."

# create screen
window =  QWidget()
window.setObjectName(u"window")
window.resize(258, 400)

# set layout settings - including grid
formLayout = QFormLayout(window)
formLayout.setObjectName(u"formLayout")

gridLayout = QGridLayout()
gridLayout.setObjectName(u"gridLayout")

# set hlines
line = QFrame(window)
line.setObjectName(u"line")
line.setFrameShape(QFrame.HLine)
line.setFrameShadow(QFrame.Sunken)
gridLayout.addWidget(line, 8, 0, 1, 3)
line_2 = QFrame(window)
line_2.setObjectName(u"line_2")
line_2.setFrameShape(QFrame.HLine)
line_2.setFrameShadow(QFrame.Sunken)
gridLayout.addWidget(line_2, 11, 0, 1, 3)

# fill in information
dir_inf = QLabel(window)
dir_inf.setObjectName(u"dir_inf")
gridLayout.addWidget(dir_inf, 0, 0, 1, 2)
vmr_inf = QLabel(window)
vmr_inf.setObjectName(u"vmr_inf")
gridLayout.addWidget(vmr_inf, 2, 0, 1, 2)
srf_inf = QLabel(window)
srf_inf.setObjectName(u"srf_inf")
gridLayout.addWidget(srf_inf, 4, 0, 1, 2)
vmp_inf = QLabel(window)
vmp_inf.setObjectName(u"vmp_inf")
gridLayout.addWidget(vmp_inf, 6, 0, 1, 2)
hem_inf = QLabel(window)
hem_inf.setObjectName(u"hem_inf")
gridLayout.addWidget(hem_inf, 9, 0, 1, 2)
im_inf = QLabel(window)
im_inf.setObjectName(u"im_inf")
gridLayout.addWidget(im_inf, 13, 0, 1, 1)

# information text
dir_txt = QLineEdit(window)
dir_txt.setObjectName(u"dir_txt")
gridLayout.addWidget(dir_txt, 1, 0, 1, 3)
vmr_txt = QLineEdit(window)
vmr_txt.setObjectName(u"vmr_txt")
gridLayout.addWidget(vmr_txt, 3, 0, 1, 3)
srf_txt = QLineEdit(window)
srf_txt.setObjectName(u"srf_txt")
gridLayout.addWidget(srf_txt, 5, 0, 1, 3)
vmp_txt = QLineEdit(window)
vmp_txt.setObjectName(u"vmp_txt")
gridLayout.addWidget(vmp_txt, 7, 0, 1, 3)
Misc_txt = QLabel(window)
Misc_txt.setObjectName(u"Misc_txt")
gridLayout.addWidget(Misc_txt, 12, 0, 1, 3)

# set all options - filetypes
buttons = {}
buttons['LH_bool'] = QCheckBox(window)
buttons['LH_bool'].setObjectName(u"LH_bool")
gridLayout.addWidget(buttons['LH_bool'], 10, 0, 1, 1)
buttons['RH_bool'] = QCheckBox(window)
buttons['RH_bool'].setObjectName(u"RH_bool")
gridLayout.addWidget(buttons['RH_bool'], 10, 1, 1, 1)
buttons['NONZERO_bool'] = QCheckBox(window)
buttons['NONZERO_bool'].setObjectName(u"NONZERO_bool")
gridLayout.addWidget(buttons['NONZERO_bool'], 14, 0, 1, 1)
buttons['COMBSMPS_bool'] = QCheckBox(window)
buttons['COMBSMPS_bool'].setObjectName(u"COMBSMPS_bool")
gridLayout.addWidget(buttons['COMBSMPS_bool'], 15, 0, 1, 1)

# misc xyz for voi
buttons['im'] = QSpinBox(window)
buttons['im'].setObjectName(u"im")
buttons['im'].setWrapping(False)
buttons['im'].setMaximum(1)
gridLayout.addWidget(buttons['im'], 13, 1, 1, 1)

# button settings
buttongo = QPushButton(window)
buttongo.setObjectName(u"buttongo")
gridLayout.addWidget(buttongo, 16, 0, 1, 2)
help_but = QPushButton(window)
help_but.setObjectName(u"help_but")
gridLayout.addWidget(help_but, 16, 2, 1, 1)

# automatically check based on loaded file
try: boolz[vmrfn[-3:]].setChecked(True)
except: pass 

# fit to layout
formLayout.setLayout(0, QFormLayout.LabelRole, gridLayout)

# set information
window.setWindowTitle(u"Sample VMP in Cortical Depths")
window.setWhatsThis(u"<html><head/><body><p>Tool to take BrainVoyager VMP files and sample them within cortical depths for one or both hemispheres." \
                    u"</p><p>Input main working directory, a VMR file for linking (e.g. UNI_reframed_ISO-0.4_WM-GM, will search for files with this prefix plus 'RH' or 'LH')," \
                    u" VMP file prefix (to sample in depth), hemispheres (left/right or both), and misc settings." \
                    u" SRF file prefix will search for SRF files including the stated string, leaving this empty will search for all SRF files of that hamispheres in all depths." \
                    u"</p><p>Filename prefixes may include directory nestings, e.g. vmps/yourvmpname will expect a 'vmps' folder within your main sellected directory." \
                    u" Output SMP's follow the same naming convention and are saved in the same direcotry as the VMP files." \
                    u"</p><p> Interpolation settings: 0: nearest neigbour, 1: trilinear  .</p></body></html>")

# set namings
Misc_txt.setText(u"Miscellaneous Settings")
vmr_inf.setText(u"VMR Prefix")
srf_inf.setText(u"SRF Prefix")
vmp_inf.setText(u"VMP Filename")
dir_inf.setText(u"Directory Path")
hem_inf.setText(u"Hemisphere")
im_inf.setText(u"     Interpolation Method")
buttons['LH_bool'].setText(u"Left")
buttons['RH_bool'].setText(u"Right")
buttons['NONZERO_bool'].setText(u"Sample only nonzero")
buttons['COMBSMPS_bool'].setText(u"Save combined SMP file")
buttongo.setText(u"Sample Depths")
help_but.setText(u"Help")

# also fatching automatically
dir_txt.setText(curdir)
vmr_txt.setText(vmrfn[:-7])
buttons['im'].setValue(1)

# connect buttons to actually run scripts
buttongo.connect('clicked(bool)', run_samp)
help_but.connect('clicked(bool)', runhelp)

# add axtra information
msg = QMessageBox()
msg.setStyleSheet("QLabel{min-width: 600px;}");
msg.setText("""Tool to take BrainVoyager VMP files and sample them within the cortical depths (looping over SRF files) for one or both hemispheres.

Input: Directory path (main working directory of files), VMR Prefix (prefix of VMR - used for linking), 
VMP Prefix (prefix of VMP to sample in depths), SRF Prefix (optional: prefix of SRF file).

Options of which hemisphere(s) to sample in, interpolation method (0: nearest, 1: trilinear), sample only nonzero (bool), and saving of combined file (bool).

See example of use below:""")

msg.setDetailedText("""Sampling VMPs in Cortial Depths:
  -Directory Path automatically loads the file location of opened BrainVoyager File. 
e.g. /MRIData/PreProc/S01_SES1/
  -VMR Prefix is automatically loaded from opened BrainVoyager file, and substracted last 7 tokens (_LH.vmr/_RH.vmr).
e.g. UNI_reframed_ISO-0.4_WM-GM    (This VMR likely doesn't serve any function, but is required for 'linking' meshes to)
  -SRF Prefix the desired mesh files to loop over (if left empty will search the current directory for '_D-' depth SRFs)
e.g. srfs/  - will look in subdirectory srfs for any depth file (and sellected hamispheres)
  -VMP filename the desired vmp map file name to sample in depths
e.g. Betas/PRF.vmp - will look in subdirectory Betas for a PRF.vmp file

If both hemispheres are sellected, the program will loop and sample for both.
Interpolation method is set to trilinear by default, but can be changed to nearest by setting it to 0.
Additionally one can choose to sample only nonzero values instead.
Save combined SMP file will save a combined SMP file for the given hemisphere (required bvbabel).""")

window.setLayout(gridLayout)
window.show()