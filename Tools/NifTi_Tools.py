import PythonQt.Qt as Qt
from PythonQt.QtGui import *
import traceback

import re
import bvbabel
import nibabel
import numpy as np  

from os.path import join
import matplotlib.pyplot as plt

## MAIN SELLECTION FUNCTIONS
def runto(): 
    """Main steps to run through after pressing the 'to nifti' button,
    includes informing participants the sellected parameters and running the actual needed function"""   
    curdir = dir_txt.text
    curfn = fil_txt.text
    curhead = miscs['head_txt'].text
    
    if miscs['firstslice_bool'].isChecked(): bv.print_to_log('\nFirst slide load option is not been fully implemented yet, though standalone script is working, setting will be ignored for now')

    # quick check if valid input
    alltypes = [buttons[key].isChecked() for key in buttons.keys()]
    if np.sum(alltypes) == 0:
        bv.print_to_log('\nPlease sellect a filetype to convert to...')
        return
    elif np.sum(alltypes) > 1:
        bv.print_to_log('\nPlease sellect only one filetype...')
        return        
    
    # fatch information and giveback to user
    sellected_ft = [key for key in buttons.keys() if buttons[key].isChecked()][0]
    bv.print_to_log(f"Converting {curfn} to Nifti format:\n -sellected folder: {curdir}\n" \
                    f" -sellected file type: {sellected_ft[:3]}\n -convert nans: {miscs['nan_bool'].isChecked()}\n" \
                    f" -read only first volume: {miscs['firstslice_bool'].isChecked()}\n")

    # run main transformation function
    to_ft[sellected_ft](curdir, curfn, curhead)  
    return


def runfrom():
    """Main steps to run through after pressing the 'from nifti' button,
    includes informing participants the sellected parameters and running the actual needed function""" 
    curdir = dir_txt.text
    curfn = fil_txt.text
    curhead = miscs['head_txt'].text

    if miscs['firstslice_bool'].isChecked(): bv.print_to_log('\nFirst slide load option is not been fully implemented yet, though standalone script is working, setting will be ignored for now')

    # quick check if valid input
    alltypes = [buttons[key].isChecked() for key in buttons.keys()]
    if np.sum(alltypes) == 0:
        bv.print_to_log('\nPlease sellect a filetype to convert from...')
        return
    elif np.sum(alltypes) > 1:
        bv.print_to_log('\nPlease sellect only one filetype...')
        return    
    
    # fatch information and giveback to user
    sellected_ft = [key for key in buttons.keys() if buttons[key].isChecked()][0]
    bv.print_to_log(f"Converting {curfn} to {sellected_ft[:3]} format:\n -sellected folder: {curdir}\n" \
                    f" -convert nans: {miscs['nan_bool'].isChecked()}\n")

    # run main transformation function
    from_ft[sellected_ft](curdir, curfn, curhead)  
    return
  

def runhelp():
    msg.exec_()
    

## MAIN TRANFORMATION FUNCTIONS
def gtc_to_nifti(curdir, curfn, curhead):    
    """create nifti files from gtc files, optional input convert_nans (default False) will convert nans to 0"""
    bv.print_to_log("GTC TO NIFTI IS UNTESTED, USE AT OWN RISK - HELP BY SENDING FINDING TO JJG.VANHAREN@MAASTRICHTUNIVERSITY.NL")
    # read in the BrainVoyager data
    gtc_path = join(curdir, curfn)
    _, img = bvbabel.gtc.read_gtc(gtc_path)
    if miscs['nan_bool'].isChecked(): img = np.nan_to_num(img)     # quickly translate nans to zeros
    img = nibabel.Nifti1Image(img, affine=np.eye(4))
    nibabel.save(img, '{}.nii.gz'.format(re.search(r'.+(?=.*.gtc$)',gtc_path)[0])) 
    return

def vtc_to_nifti(curdir, curfn, curhead):
    """create nifti files from vtc files, optional input convert_nans (default False) will convert nans to 0"""
    # read in the BrainVoyager data
    vtc_path = join(curdir, curfn)
    _, img = bvbabel.vtc.read_vtc(vtc_path, rearrange_data_axes=False)
    if miscs['nan_bool'].isChecked(): img = np.nan_to_num(img)     # quickly translate nans to zeros
    # transpose / flip axes
    img = np.transpose(img, [0, 2, 1, 3])
    img = img[::-1, ::-1, ::-1]
    # translate to nifti
    img = nibabel.Nifti1Image(img, affine=np.eye(4))
    nibabel.save(img, '{}.nii.gz'.format(re.search(r'.+(?=.*.vtc$)',vtc_path)[0])) 
    return

def fmr_to_nifti(curdir, curfn, curhead):
    """create nifti files from fmr files, optional input convert_nans (default False) will convert nans to 0"""
    # read in the BrainVoyager data
    fmr_path = join(curdir, curfn)
    _, img = bvbabel.fmr.read_fmr(fmr_path)
    if miscs['nan_bool'].isChecked(): img = np.nan_to_num(img)     # quickly translate nans to zeros
    img = nibabel.Nifti1Image(img, affine=np.eye(4))
    nibabel.save(img, '{}.nii.gz'.format(re.search(r'.+(?=.*.fmr$)',fmr_path)[0])) 
    return

def vmp_to_nifti(curdir, curfn, curhead):
    """create nifti files from vmp files, optional input convert_nans (default False) will convert nans to 0"""
    # read in the BrainVoyager data
    vmp_path = join(curdir, curfn)
    _, img = bvbabel.vmp.read_vmp(vmp_path)
    if miscs['nan_bool'].isChecked(): img = np.nan_to_num(img)     # quickly translate nans to zeros
    img = nibabel.Nifti1Image(img, affine=np.eye(4))
    nibabel.save(img, '{}.nii.gz'.format(re.search(r'.+(?=.*.vmp$)',vmp_path)[0])) 
    return

def vmr_to_nifti(curdir, curfn, curhead):
    """create nifti files from vmr files, optional input convert_nans (default False) will convert nans to 0"""
    # read in the BrainVoyager data
    vmr_path = join(curdir, curfn)
    _, img = bvbabel.vmr.read_vmr(vmr_path)
    if miscs['nan_bool'].isChecked(): img = np.nan_to_num(img)     # quickly translate nans to zeros
    img = nibabel.Nifti1Image(img, affine=np.eye(4))
    nibabel.save(img, '{}.nii.gz'.format(re.search(r'.+(?=.*.vmr$)',vmr_path)[0])) 
    return

def voi_to_nifti(curdir, curfn, curhead):
    """create nifti file from voi file, voi list will be translated to base10 labels (1, 2, 3 etc.)"""
    voi_path = join(curdir, curfn)
    _, img = bvbabel.voi.read_voi(voi_path)
    # predefine zeros table
    x, y, z = int(miscs['x'].value), int(miscs['y'].value), int(miscs['z'].value)
    new_img = np.zeros([x, y, z], dtype=np.uint8)
    # loop over all the labels
    for l in range(len(img)):
        try:
            # get single dim coordinates
            xind = img[l]['Coordinates'][:,0]
            yind = img[l]['Coordinates'][:,1]
            zind = img[l]['Coordinates'][:,2]   
            # populate
            new_img[xind, yind, zind] = l+1
        except:
            bv.print_to_log("DIMENSIONS MISMATCH. check xyz")
    # convert to nii and save
    new_img = np.transpose(new_img, (2,0,1))
    new_img = new_img[::-1, ::-1, ::-1]
    new_img = nibabel.Nifti1Image(new_img, affine=np.eye(4))
    nibabel.save(new_img, '{}.nii.gz'.format(re.search(r'.+(?=.*.voi$)',voi_path)[0])) 
    return

def v16_to_nifti(curdir, curfn, curhead):
    """create nifti files from v16 files, optional input convert_nans (default False) will convert nans to 0"""
    # read in the BrainVoyager data
    v16_path = join(curdir, curfn)
    _, img = bvbabel.v16.read_v16(v16_path)
    if miscs['nan_bool'].isChecked(): img = np.nan_to_num(img)     # quickly translate nans to zeros
    img = nibabel.Nifti1Image(img, affine=np.eye(4))
    nibabel.save(img, '{}.nii.gz'.format(re.search(r'.+(?=.*.v16$)',v16_path)[0])) 
    return

def msk_to_nifti(curdir, curfn, curhead):
    """create nifti files from msk files"""
    # read in the BrainVoyager data
    msk_path = join(curdir, curfn)
    _, img = bvbabel.msk.read_msk(msk_path)
    if miscs['nan_bool'].isChecked(): img = np.nan_to_num(img)     # quickly translate nans to zeros
    # translate to nifti
    img = nibabel.Nifti1Image(img, affine=np.eye(4))
    nibabel.save(img, '{}.nii.gz'.format(re.search(r'.+(?=.*.msk$)',msk_path)[0])) 
    return
    
def nifti_to_gtc(curdir, curfn, curhead):
    """create gtc from nifti"""
    bv.print_to_log("GTC TO NIFTI IS UNTESTED, USE AT OWN RISK - HELP BY SENDING FINDING TO JJG.VANHAREN@MAASTRICHTUNIVERSITY.NL")    
    gtc_path = join(curdir, curfn)
    img = nibabel.load(gtc_path)
    img = img.get_fdata()
    if miscs['nan_bool'].isChecked(): img = np.nan_to_num(img) # quickly translate nans to zeros
    # fatch header information from donor file or create
    if miscs['head_bool'].isChecked():
        gtc_head, _ = bvbabel.gtc.read_gtc(join(curdir, curhead))
    else:
        bv.print_to_log("BVBABEL DOES NOT CURRENTLY SUPPORT VMR HEADER CREATION. use donor header instead")
        raise ValueError('Option combination not possible!')
    # translate and save vmr
    bvbabel.gtc.write_gtc('{}.gtc'.format(re.search(r'.+(?=.*.nii.gz$)',gtc_path)[0]), gtc_head, img)
    return
    
def nifti_to_vtc(curdir, curfn, curhead):
    """create v16 from nifti"""
    vtc_path = join(curdir, curfn)
    img = nibabel.load(vtc_path)
    img = img.get_fdata()
    # do some transformation
    img = img[::-1, ::-1, ::-1, :]
    img = np.transpose(img, (0, 2, 1, 3))
    if miscs['nan_bool'].isChecked(): img = np.nan_to_num(img) # quickly translate nans to zeros
    # fatch header information from donor file or create
    if miscs['head_bool'].isChecked():
        vtc_head, _ = bvbabel.vtc.read_vtc(join(curdir, curhead), rearrange_data_axes=False)
    else:
        vtc_head, _ = bvbabel.vtc.create_vtc()
    # translate and save vmr
    bvbabel.vtc.write_vtc('{}.vtc'.format(re.search(r'.+(?=.*.nii.gz$)',vtc_path)[0]), vtc_head, img,
                          rearrange_data_axes=False)
    
def nifti_to_fmr(curdir, curfn, curhead):
    """create v16 from nifti"""
    fmr_path = join(curdir, curfn)
    img = nibabel.load(fmr_path)
    img = img.get_fdata()
    if miscs['nan_bool'].isChecked(): img = np.nan_to_num(img) # quickly translate nans to zeros
    # if we have only one volume
    if img.ndim == 3: img = img[:, :, :, np.newaxis]
    # fatch header information from donor file or create
    if miscs['head_bool'].isChecked():
        fmr_head, _ = bvbabel.fmr.read_fmr(join(curdir, curhead))
    else:
        bv.print_to_log('NOT OFFICIALLY SUPPORTED BY BVBABEL. use at own discresion')
        fmr_head, _ = bvbabel.fmr.create_fmr()
    # translate and save vmr
    bvbabel.stc.write_stc('{}.stc'.format(re.search(r'.+(?=.*.nii.gz$)',fmr_path)[0]), img, data_type=fmr_head['DataType'])
    bvbabel.fmr.write_fmr('{}.fmr'.format(re.search(r'.+(?=.*.nii.gz$)',fmr_path)[0]), fmr_head, img)
    return
    
def nifti_to_vmp(curdir, curfn, curhead):
    """create vmp from nifti"""
    vmp_path = join(curdir, curfn)
    img = nibabel.load(vmp_path)
    img = img.get_fdata()
    img = img.astype('float32')
    if miscs['nan_bool'].isChecked(): img = np.nan_to_num(img) # quickly translate nans to zeros
    # fatch header information from donor file or create
    if miscs['head_bool'].isChecked():
        vmp_head, _ = bvbabel.vmp.read_vmp(join(curdir, curhead))
    else:
        bv.print_to_log("BVBABEL DOES NOT CURRENTLY SUPPORT VMR HEADER CREATION. use donor header instead")
        raise ValueError('Option combination not possible!')
    # define partial header
    part_head = []
    bv.print_to_log("NOT FULLY IMPLEMNTED YET, COME BACK LATER, SEE CODE FOR DETAILS AND PROOF OF CONCEPT")
    raise ValueError('Option combination not possible!')
    # not implemented as of yet, proof of concept working,
    # see presentations/segmentationmeeting/nighres.ipynb for details
    # loop over last dimension, set rgb to some range, give placeholder name 1, 2, 3 etc
    # translate and save vmr
    bvbabel.vmp.write_vmp('{}.vmp'.format(re.search(r'.+(?=.*.nii.gz$)',vmp_path)[0]), vmp_head, img)
    return
    
def nifti_to_vmr(curdir, curfn, curhead):
    """create vmr from nifti"""
    vmr_path = join(curdir, curfn)
    img = nibabel.load(vmr_path)
    img = img.get_fdata().astype(np.uint8)
    if miscs['nan_bool'].isChecked(): img = np.nan_to_num(img) # quickly translate nans to zeros
    # fatch header information from donor file or create
    if miscs['head_bool'].isChecked():
        vmr_head, _ = bvbabel.vmr.read_vmr(join(curdir, curhead))
    else:
        bv.print_to_log("BVBABEL DOES NOT CURRENTLY SUPPORT VMR HEADER CREATION. use donor header instead")
        raise ValueError('Option combination not possible!')
    # translate and save vmr
    bvbabel.vmr.write_vmr('{}.vmr'.format(re.search(r'.+(?=.*.nii.gz$)',vmr_path)[0]), vmr_head, img)
    return
    
def nifti_to_v16(curdir, curfn, curhead):
    """create v16 from nifti"""
    v16_path = join(curdir, curfn)
    img = nibabel.load(v16_path)
    img = img.get_fdata().astype(np.uint16)
    if miscs['nan_bool'].isChecked(): img = np.nan_to_num(img) # quickly translate nans to zeros
    # fatch header information from donor file or create
    if miscs['head_bool'].isChecked():
        v16_head, _ = bvbabel.v16.read_v16(join(curdir, curhead))
    else:
        v16_head, _ = bvbabel.v16.create_v16()
    # translate and save vmr
    bvbabel.v16.write_v16('{}.v16'.format(re.search(r'.+(?=.*.nii.gz$)',vmr_path)[0]), v16_head, img)
    return
    
def nifti_to_msk(curdir, curfn, curhead):
    """create v16 from nifti"""
    msk_path = join(curdir, curfn)
    img = nibabel.load(msk_path)
    img = img.get_fdata()
    if miscs['nan_bool'].isChecked(): img = np.nan_to_num(img) # quickly translate nans to zeros
    # fatch header information from donor file or create
    if miscs['head_bool'].isChecked():
        msk_head, _ = bvbabel.msk.read_msk(join(curdir, curhead))
    else:
        bv.print_to_log("BVBABEL DOES NOT CURRENTLY SUPPORT VMR HEADER CREATION. use donor header instead")
        raise ValueError('Option combination not possible!')
    # translate and save vmr
    bvbabel.msk.write_msk('{}.msk'.format(re.search(r'.+(?=.*.nii.gz$)',msk_path)[0]), msk_head, img)
    
def nifti_to_voi(curdir, curfn, curhead):
    """create voi files from label nifti files"""
    # create or load header
    if miscs['head_bool'].isChecked(): 
        header, _ = bvbabel.voi.read_voi(join(curdir, curhead))
    else: 
        header = {'FileVersion': 4, 'ReferenceSpace': 'BV', 'OriginalVMRResolutionX': '0.4', 
                    'OriginalVMRResolutionY': '0.4', 'OriginalVMRResolutionZ': '0.4', 
                    'OriginalVMROffsetX': 0, 'OriginalVMROffsetY': 0, 'OriginalVMROffsetZ': 0, 
                    'OriginalVMRFramingCubeDim': 512, 'LeftRightConvention': 1, 
                    'SubjectVOINamingConvention': '<VOI>_<SUBJ>', 
                    'NrOfVOIs': 1, 'NrOfVOIVTCs': 0, 'VOIVTCs': []}
    # load data
    voi_path = join(curdir, curfn)
    img = nibabel.load(voi_path)
    img = img.get_fdata()
    # transform data to make it match bv
    img = img[::-1, ::-1, ::-1]
    img = np.transpose(img, (1, 2, 0))
    # prepair data
    data = []
    newidx = 0
    cmap = plt.cm.get_cmap('tab10')
    all_val = np.unique(img)
    # loop over values but keep background
    for l in all_val[1:]:
        tmp = np.where(img == l)
        tmp = np.transpose(np.stack(tmp))
        # insert new data
        data.append({})
        data[newidx]['Coordinates'] = tmp
        data[newidx]['NameOfVOI'] = str(round(l))
        data[newidx]['ColorOfVOI'] = [int(cmap(newidx)[0] * 254), 
                                      int(cmap(newidx)[1] * 254), 
                                      int(cmap(newidx)[2] * 254)]
        data[newidx]['NrOfVoxels'] = tmp.shape[0]
        # adjust index
        newidx += 1
    # set Nr of Vois
    header['NrOfVOIs'] = len(data)
    header['OriginalVMRFramingCubeDim'] = np.max(img.shape)
    header['VOIVTCs'] = []
    # save voi
    bvbabel.voi.write_voi('{}.voi'.format(re.search(r'.+(?=.*.nii.gz$)',voi_path)[0]), header, data)
    return

# set global variables for use in functions
global curdir
global curfn
global curhead
global buttons
global miscs

# create lookup dicts
to_ft = {'GTC_bool':gtc_to_nifti, 'VTC_bool':vtc_to_nifti, 'FMR_bool':fmr_to_nifti,
         'VMP_bool':vmp_to_nifti, 'VMR_bool':vmr_to_nifti, 'V16_bool':v16_to_nifti, 
         'MSK_bool':msk_to_nifti, 'VOI_bool':voi_to_nifti}
from_ft = {'GTC_bool':nifti_to_gtc, 'VTC_bool':nifti_to_vtc, 'FMR_bool':nifti_to_fmr, 
           'VMP_bool':nifti_to_vmp, 'VMR_bool':nifti_to_vmr, 'V16_bool':nifti_to_v16, 
           'MSK_bool':nifti_to_msk, 'VOI_bool':nifti_to_voi}
           
# see if a brainvoyager file is opened and use its parameters for text input defaults
try:
    doc = bv.active_document
    curdir = doc.path
    curfn = doc.file_name
    x_0 = doc.dim_x
    y_0 = doc.dim_y
    z_0 = doc.dim_z
except: 
    curdir = "..."
    curfn = "..."
    x_0 = 0
    y_0 = 0
    z_0 = 0

# create screen
window =  QWidget()
window.setObjectName(u"window")
window.resize(258, 443)


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
gridLayout.addWidget(line, 13, 0, 1, 5)
line_2 = QFrame(window)
line_2.setObjectName(u"line_2")
line_2.setFrameShape(QFrame.HLine)
line_2.setFrameShadow(QFrame.Sunken)
gridLayout.addWidget(line_2, 4, 0, 1, 5)

# fill in information
fil_inf = QLabel(window)
fil_inf.setObjectName(u"fil_inf")
gridLayout.addWidget(fil_inf, 2, 0, 1, 2)
dir_inf = QLabel(window)
dir_inf.setObjectName(u"dir_inf")
gridLayout.addWidget(dir_inf, 0, 0, 1, 2)

# information text
filetype_txt = QLabel(window)
filetype_txt.setObjectName(u"filetype_txt")
gridLayout.addWidget(filetype_txt, 5, 0, 1, 2)
fil_txt = QLineEdit(window)
fil_txt.setObjectName(u"fil_txt")
gridLayout.addWidget(fil_txt, 3, 0, 1, 5)
dir_txt = QLineEdit(window)
dir_txt.setObjectName(u"dir_txt")
gridLayout.addWidget(dir_txt, 1, 0, 1, 5)
Misc_txt = QLabel(window)
Misc_txt.setObjectName(u"Misc_txt")
gridLayout.addWidget(Misc_txt, 14, 0, 1, 3)

# set all options - filetypes
buttons = {}
buttons['GTC_bool'] = QCheckBox(window)
buttons['GTC_bool'].setObjectName(u"GTC_bool")
gridLayout.addWidget(buttons['GTC_bool'], 7, 0, 1, 1)
buttons['VTC_bool'] = QCheckBox(window)
buttons['VTC_bool'].setObjectName(u"VTC_bool")
gridLayout.addWidget(buttons['VTC_bool'], 12, 0, 1, 1)
buttons['FMR_bool'] = QCheckBox(window)
buttons['FMR_bool'].setObjectName(u"FMR_bool")
gridLayout.addWidget(buttons['FMR_bool'], 6, 0, 1, 2)
buttons['VMP_bool'] = QCheckBox(window)
buttons['VMP_bool'].setObjectName(u"VMP_bool")
gridLayout.addWidget(buttons['VMP_bool'], 10, 0, 1, 1)
buttons['VMR_bool'] = QCheckBox(window)
buttons['VMR_bool'].setObjectName(u"VMR_bool")
gridLayout.addWidget(buttons['VMR_bool'], 9, 0, 1, 1)
buttons['V16_bool'] = QCheckBox(window)
buttons['V16_bool'].setObjectName(u"V16_bool")
gridLayout.addWidget(buttons['V16_bool'], 9, 1, 1, 1)
buttons['MSK_bool'] = QCheckBox(window)
buttons['MSK_bool'].setObjectName(u"MSK_bool")
gridLayout.addWidget(buttons['MSK_bool'], 8, 0, 1, 1)
buttons['VOI_bool'] = QCheckBox(window)
buttons['VOI_bool'].setObjectName(u"VOI_bool")
gridLayout.addWidget(buttons['VOI_bool'], 11, 0, 1, 1)

# misc bools
miscs = {}
miscs['nan_bool'] = QCheckBox(window)
miscs['nan_bool'].setObjectName(u"nan_bool")
gridLayout.addWidget(miscs['nan_bool'], 15, 0, 1, 2)
miscs['firstslice_bool'] = QCheckBox(window)
miscs['firstslice_bool'].setObjectName(u"firstslice_bool")
gridLayout.addWidget(miscs['firstslice_bool'], 16, 0, 1, 3)
# misc xyz for voi
miscs['x'] = QSpinBox(window)
miscs['x'].setObjectName(u"x")
miscs['x'].setWrapping(False)
miscs['x'].setMaximum(9999)
gridLayout.addWidget(miscs['x'], 11, 2, 1, 1)
miscs['y'] = QSpinBox(window)
miscs['y'].setObjectName(u"y")
miscs['y'].setWrapping(False)
miscs['y'].setMaximum(9999)
gridLayout.addWidget(miscs['y'], 11, 3, 1, 1)
miscs['z'] = QSpinBox(window)
miscs['z'].setObjectName(u"z")
miscs['z'].setWrapping(False)
miscs['z'].setMaximum(9999)
gridLayout.addWidget(miscs['z'], 11, 4, 1, 1)
miscs['head_bool'] = QCheckBox(window)
miscs['head_bool'].setObjectName(u"head_bool")
gridLayout.addWidget(miscs['head_bool'], 18, 0, 1, 1)
miscs['head_txt'] = QLineEdit(window)
miscs['head_txt'].setObjectName(u"head_txt")
gridLayout.addWidget(miscs['head_txt'], 18, 1, 1, 4)

# button settings
buttongo_to = QPushButton(window)
buttongo_to.setObjectName(u"buttongo_to")
gridLayout.addWidget(buttongo_to, 19, 2, 1, 2)
buttongo_from = QPushButton(window)
buttongo_from.setObjectName(u"buttongo_from")
gridLayout.addWidget(buttongo_from, 19, 0, 1, 2)
help_but = QPushButton(window)
help_but.setObjectName(u"help_but")
gridLayout.addWidget(help_but, 19, 4, 1, 1)



# check naming regex and sellect automatically
boolz = {'gtc' : buttons['GTC_bool'],
         'vtc' : buttons['VTC_bool'],
         'fmr' : buttons['FMR_bool'],
         'vmp' : buttons['VMP_bool'],
         'vmr' : buttons['V16_bool'],
         'v16' : buttons['V16_bool'],
         'msk' : buttons['MSK_bool'],
         'voi' : buttons['VOI_bool']}

# automatically check based on loaded file
try: boolz[curfn[-3:]].setChecked(True)
except: pass 

# fit to layout
formLayout.setLayout(0, QFormLayout.LabelRole, gridLayout)

# set information
window.setWindowTitle(u"Nifti Tools")
window.setWhatsThis(u"<html><head/><body><p>Tool to take BrainVoyager file format and transform them to Nifti file format and visa versa." \
                    u"</p><p>If a BrainVoyager window is open it will automatically fill in the directory path and filename of that file," \
                    u" but both varaibles can be adjusted manually (and need be for Nifti file formats).<br/></p><p>From filetype will " \
                    u"automatically sellect based on currently opened file (for VMR the tool will always try to convert the V16 file instead by default)." \
                    u" </p><p>Miscellaneous settings can be sellected if desired, these include: Convert Nans (set nans to zeros), Zero pad (zero pad the numpy array), " \
                    u"First Volume Only (take only the first Volume for quick timeseries loading).</p></body></html>")

# set namings
Misc_txt.setText(u"Miscellaneous Settings")
filetype_txt.setText(u"File Type")
fil_inf.setText(u"File Name")
dir_inf.setText(u"Directory Path")
buttons['GTC_bool'].setText(u"GTC")
buttons['VTC_bool'].setText(u"VTC")
buttons['FMR_bool'].setText(u"FMR / STC")
buttons['VMP_bool'].setText(u"VMP")
buttons['VMR_bool'].setText(u"VMR")
buttons['V16_bool'].setText(u"V16")
buttons['MSK_bool'].setText(u"MSK")
buttons['VOI_bool'].setText(u"VOI")
miscs['nan_bool'].setText(u"Convert Nans")
miscs['firstslice_bool'].setText(u"First Volume Only (4D) - UNDER CONSTRUCTION")
miscs['x'].setPrefix(u"X: ")
miscs['y'].setPrefix(u"Y: ")
miscs['z'].setPrefix(u"Z: ")
buttongo_to.setText(u"Convert to NIFTI")
buttongo_from.setText(u"Convert from NIFTI") 
help_but.setText(u"Help") 
miscs['head_bool'].setText(u"Header from:")
miscs['head_txt'].setText(u"")

# also fatching automatically
dir_txt.setText(curdir)
fil_txt.setText(curfn)
miscs['x'].setValue(x_0)
miscs['y'].setValue(y_0)
miscs['z'].setValue(z_0)

# connect buttons to actually run scripts
buttongo_to.connect('clicked(bool)', runto)
buttongo_from.connect('clicked(bool)', runfrom)
help_but.connect('clicked(bool)', runhelp)

# add axtra information
msg = QMessageBox()
msg.setStyleSheet("QLabel{min-width: 600px;}");
msg.setText("""NifTi Tools can be used to transform BrainVoyager files into corresponding NifTi files and vice versa. 
Simply sellect the desired directory, the file name (for NifTi a file ending in nii.gz), the file type you want to convert to/from and press the convert button. 

The new file is saved in the same directory with matching name.""")

msg.setDetailedText("""Conversion from NifTi:
  -Directory Path automatically loads the file location of opened BrainVoyager File. 
If needed change this to the location where the NifTi file of interest is located. 
  -File Name must be changed to the full NifTi file (including .nii.gz).
  -File Type again assumes the file type of the currently opened BrainVoyager file, 
please sellect what to convert to (e.g. FMR for timeseries, VTC for voxeltimecourses, V16 for anatomical data).
  -Misc Settings includes the convertion of any nan value to zero, loading the data from a first volume (timeseries data only), 
and selecting donor header.

Selection of a proper header is especially important, this way BrainVoyager knows what data to expect. 
When this option is not selected, a default header is created – which is in many cases subpar. 
In most cases it is preferred to use a ‘donor’ header from a (similar) BrainVoyager file 
(e.g. when converting to NifTi, doing some calculations, and converting back to BrainVoyager, the original BrainVoyager file has the desired header).


Conversion to NifTi:
  -Directory Path automatically loads the file location of opened BrainVoyager File.
  -File Name will match the filename of the opened BrainVoyager File, but can be changed to any BrainVoyager file.
  -File Type will automatically select what it thinks the current filetype is, please select the current file type (only one).
  -VOIs are a special case since they do not hold boundary information, please select the size of the matching anatmical.
  
For anatomicals, Nifti Tools always tries to convert the v16 instead of the vmr (for increased precision). 
If no matching v16 is available, you can select vmr instead. 


Extra Tips: 
For conversion of NifTi anatomical data, please run the program twice – once for V16 and once again form vmr.""")

window.setLayout(gridLayout)
window.show()
