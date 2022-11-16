## functions / tool to isovoxel volumes or vois to any new resolution in any framing box
## note that functions are far from optimal - especially for VOIs 
# (if you are dealing with many volumes and use this a lot you might want to optimize this - e.g. set all volumes to boolean [vois, x,y,z])
# but for many cases the few minutes it takes to run are fine - get yourself a coffee ;)

# if you want to use the function standalone on some arbetrary numpy array, please use 
# isovoxel_nearest(img, framecube, source_vox, target_vox)
#   (which uses: padarray(A, size), create_affine_mat(source_vox, target_vox, size), apply_affine(A, target_affine)
#   order=0 garantees nearest neigbor

import PythonQt.Qt as Qt
from PythonQt.QtGui import *
import traceback

import re
import bvbabel
import nibabel
import numpy as np  

from os.path import join
import matplotlib.pyplot as plt
from scipy import ndimage

## MAIN SELLECTION FUNCTIONS
def runall(): 
    """Main steps to run through after pressing the 'to nifti' button,
    includes informing participants the sellected parameters and running the actual needed function"""   
    curdir = dir_txt.text
    curfn = fil_txt.text

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

    # loading function
    bv.print_to_log(f'\nLoading {join(curdir, curfn)}')
    head, img, headv16, imgv16 = load_ft[sellected_ft](curdir, curfn)
    
    # fetch filled in parameters
    framecube = int(miscs['fram'].value)
    source_vox = [float(miscs['x_s'].text), float(miscs['y_s'].text), float(miscs['z_s'].text)]
    target_vox = [float(miscs['x_t'].text), float(miscs['y_t'].text), float(miscs['z_t'].text)]
    bv.print_to_log(f'\nIsovoxel - using nearest neighbor interpolation \nFrom: \n {source_vox} \nTo: \n {target_vox} \nIn bounding box with size:\n {framecube}')

    # do actual isovoxel steps
    newimg = isovoxel_nearest(img, framecube, source_vox, target_vox)
    if headv16: newimgv16 = isovoxel_nearest(imgv16, framecube, source_vox, target_vox)   # run again if v16/vmr was selected
    else: newimgv16 = imgv16   
    
    # updating header information
    newhead, newheadv16 = update_ft[sellected_ft](head, headv16, framecube, target_vox, curdir, curfn)

    # saving function
    newfn = '{}_ISO{}{}'.format(curfn[:-4],
                                re.sub('\D', '', miscs['x_t'].text), 
                                curfn[-4:])
    bv.print_to_log(f'\nSaving {join(curdir, newfn)}')
    save_ft[sellected_ft](curdir, newfn, newimg, newhead, newimgv16, newheadv16)    
    return
    

def isovoxel_nearest(img, framecube, source_vox, target_vox):
    """mean function to iso voxel a 3d array using nearest neighbor"""    
    
    # add padding to matrix and calculate translation matrix
    img = padarray(img, framecube)  
    target_affine = create_affine_mat(source_vox, target_vox, framecube)

    # apply affine
    return( apply_affine(img, target_affine) )


def padarray(A, size):
    """add padding / transform to some new framing cube dimension"""

    # check if demensions are odd or even
    if np.any([x % 2 for x in A.shape[-3:]]):
        bv.print_to_log("WARNING: DIMENSIONS ARE FOUND TO BE ODD NUMBERED... PLEASE CHECK IF RESULTS MATCH BV NATIVE APPROACH")
        raise Exception("Odd numbered input not supported") 

    # get dimension shape
    dim1 = int((size - A.shape[-3]) / 2)
    dim2 = int((size - A.shape[-2]) / 2)
    dim3 = int((size - A.shape[-1]) / 2)

    # return array with padding
    if A.ndim == 3: A = np.pad(A, pad_width=((dim1, dim1), (dim2, dim2), (dim3, dim3)), mode='constant')
    elif A.ndim == 4: A = np.pad(A, pad_width=((0, 0), (dim1, dim1), (dim2, dim2), (dim3, dim3)), mode='constant')
    return(A)


def create_affine_mat(source_vox, target_vox, size):
    """create scaling affine matrix, including center translation"""
    target_affine = np.eye(4)
    for i in range(3):
        target_affine[i,  i]  = target_vox[i]/source_vox[i]
        target_affine[i, -1]  = (1 - (target_vox[i]/source_vox[i])) * (size/2)
    return(target_affine)


def apply_affine(A, target_affine):
    """use ndimage affine transformation function with target_affine and use
    nearest neigbor interpolation"""
    bv.print_to_log(f'\nApplying affine transformation:\n{target_affine}')
    if A.ndim == 3: 
        Anew = ndimage.affine_transform(A, target_affine, order=0)
    elif A.ndim == 4: 
        Anew = np.empty(A.shape)
        for i in range(A.shape[0]):
            Anew[i,:] = ndimage.affine_transform(A[i,:], target_affine, order=0)
    return(Anew)


# helper functions for loading
def _load_vmr(curdir, curfn):
    head, img = bvbabel.vmr.read_vmr(join(curdir, curfn))
    return(head, img, [], [])

def _load_v16(curdir, curfn):
    head, img = bvbabel.v16.read_v16(join(curdir, curfn))
    return(head, img, [], [])

def _load_voi(curdir, curfn):
    head, img = bvbabel.voi.read_voi(join(curdir, curfn))
    # predefine zeros table
    x, y, z = int(miscs['x'].value), int(miscs['y'].value), int(miscs['z'].value)
    new_img = np.zeros([head['NrOfVOIs'], z, y, x], dtype=np.uint8)
    # loop over all the labels
    for l in range(len(img)):
        try:
            # get single dim coordinates
            xind = img[l]['Coordinates'][:,0]
            yind = img[l]['Coordinates'][:,1]
            zind = img[l]['Coordinates'][:,2]   
            # populate
            new_img[l, xind, yind, zind] = l+1
        except:
            bv.print_to_log("DIMENSIONS MISMATCH. check xyz")
    # SEE IF WE NEED TO TRANSPOSE DIMENSIONS HERE
    new_img = np.transpose(new_img, (0, 3,1,2))
    new_img = new_img[:, ::-1, ::-1, ::-1] 
    return(head, new_img, [], img)

def _load_vmrv16(curdir, curfn):
    head, img = bvbabel.vmr.read_vmr(join(curdir, curfn))
    headv16, imgv16 = bvbabel.v16.read_v16(join(curdir, '{}v16'.format(curfn[:-3])))
    return(head, img, headv16, imgv16)
    

def _save_vmr(curdir, curfn, img, head, imgv16, headv16):
    bvbabel.vmr.write_vmr(join(curdir, curfn), head, img)
    return

def _save_v16(curdir, curfn, img, head, imgv16, headv16):
    bvbabel.v16.write_v16(join(curdir, curfn), head, img.astype(np.uint16))
    return

def _save_voi(curdir, curfn, img, head, imgv16, headv16):
    # reorder data
    img = img[:, ::-1, ::-1, ::-1]
    img = np.transpose(img, (0, 2, 3, 1))
    # loop over vois
    for l in range(head['NrOfVOIs']):
        tmp = np.where(img[l,:] > 0)
        tmp = np.transpose(np.stack(tmp))
        # insert new data
        imgv16[l]['Coordinates'] = tmp
        imgv16[l]['NrOfVoxels'] = imgv16[l]['Coordinates'].shape[0]
    bvbabel.voi.write_voi(join(curdir, curfn), head, imgv16)
    return

def _save_vmrv16(curdir, curfn, img, head, imgv16, headv16):
    bvbabel.vmr.write_vmr(join(curdir, curfn), head, img)
    bvbabel.v16.write_v16(join(curdir, '{}v16'.format(curfn[:-3])), headv16, imgv16.astype(np.uint16))
    return


def _update_vmr(head, headv16, framecube, target_vox, curdir, curfn):
    # get affine transformation minus translation for header
    temp_affine = np.eye(4)
    for i in range(3):
        temp_affine[i,  i]  = target_vox[i]/source_vox[i]
    temp_affine = temp_affine.flatten().tolist()

    # update parts of header
    head['DimX'] = framecube
    head['DimY'] = framecube
    head['DimZ'] = framecube
    head['FramingCubeDim'] = framecube
    head['NrOfPastSpatialTransformations'] += 1    
    head['PastTransformation'] =  [{'Name': 'IsoVoxelation, nearest neighbor', 
                                    'Type': 2, 
                                    'SourceFileName': join(curdir, curfn), 
                                    'NrOfValues': 16, 
                                    'Values': temp_affine}]
    head['VoxelSizeX'] = target_vox[0]
    head['VoxelSizeY'] = target_vox[1]
    head['VoxelSizeZ'] = target_vox[2]
    return(head, [])
    
def _update_v16(head, headv16, framecube, target_vox, curdir, curfn):
    # update parts of header
    head['DimX'] = framecube
    head['DimY'] = framecube
    head['DimZ'] = framecube
    return(head, [])
    
def _update_voi(head, headv16, framecube, target_vox, curdir, curfn):
    # get affine transformation minus translation for header
    head['OriginalVMRResolutionX'] = target_vox[0]
    head['OriginalVMRResolutionY'] = target_vox[1]
    head['OriginalVMRResolutionZ'] = target_vox[2]
    head['OriginalVMRFramingCubeDim'] = framecube
    return(head, [])
    
def _update_vmrv16(head, headv16, framecube, target_vox, curdir, curfn):
    # get affine transformation minus translation for header
    temp_affine = np.eye(4)
    for i in range(3):
        temp_affine[i,  i]  = target_vox[i]/source_vox[i]
    temp_affine = temp_affine.flatten().tolist()

    # update parts of header
    head['DimX'] = framecube
    head['DimY'] = framecube
    head['DimZ'] = framecube
    head['FramingCubeDim'] = framecube
    head['NrOfPastSpatialTransformations'] += 1
    head['PastTransformation'] =  [{'Name': 'IsoVoxelation, nearest neighbor', 
                                    'Type': 2, 
                                    'SourceFileName': join(curdir, curfn), 
                                    'NrOfValues': 16, 
                                    'Values': temp_affine}]        
    head['VoxelSizeX'] = target_vox[0]
    head['VoxelSizeY'] = target_vox[1]
    head['VoxelSizeZ'] = target_vox[2]
    
    # update v16 header
    headv16['DimX'] = framecube
    headv16['DimY'] = framecube
    headv16['DimZ'] = framecube
    return(head, headv16)


# set global variables for use in functions
global curdir
global curfn
global miscs
           
# see if a brainvoyager file is opened and use its parameters for text input defaults
try:
    doc = bv.active_document
    curdir = doc.path
    curfn = doc.file_name
    x_s0 = np.round(doc.voxelsize_x, 3)
    y_s0 = np.round(doc.voxelsize_y, 3)
    z_s0 = np.round(doc.voxelsize_z, 3)
    x_0 = doc.dim_x
    y_0 = doc.dim_y
    z_0 = doc.dim_z
except: 
    curdir = "..."
    curfn = "..."
    x_s0 = ""
    y_s0 = ""
    z_s0 = ""
    x_0 = ""
    y_0 = ""
    z_0 = ""


load_ft = {'VMR_bool': _load_vmr,
         'V16_bool': _load_v16,
         'VOI_bool': _load_voi,
         'VMR/V16_bool': _load_vmrv16}
save_ft = {'VMR_bool': _save_vmr,
         'V16_bool': _save_v16,
         'VOI_bool': _save_voi,
         'VMR/V16_bool': _save_vmrv16}
update_ft = {'VMR_bool': _update_vmr,
         'V16_bool': _update_v16,
         'VOI_bool': _update_voi,
         'VMR/V16_bool': _update_vmrv16}         

## START UI THINGS
# create screen
window =  QWidget()
window.setObjectName(u"window")
window.resize(550, 300)

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
gridLayout.addWidget(line, 11, 0, 1, 9)
line_2 = QFrame(window)
line_2.setObjectName(u"line_2")
line_2.setFrameShape(QFrame.HLine)
line_2.setFrameShadow(QFrame.Sunken)
gridLayout.addWidget(line_2, 4, 0, 1, 9)
line_3 = QFrame(window)
line_3.setObjectName(u"line_3")
line_3.setFrameShape(QFrame.HLine)
line_3.setFrameShadow(QFrame.Sunken)
gridLayout.addWidget(line_3, 16, 0, 1, 9)

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
gridLayout.addWidget(filetype_txt, 7, 0, 1, 2)
fil_txt = QLineEdit(window)
fil_txt.setObjectName(u"fil_txt")
gridLayout.addWidget(fil_txt, 3, 0, 1, 9)
dir_txt = QLineEdit(window)
dir_txt.setObjectName(u"dir_txt")
gridLayout.addWidget(dir_txt, 1, 0, 1, 9)
vox_txt = QLabel(window)
vox_txt.setObjectName(u"vox_txt")
gridLayout.addWidget(vox_txt, 12, 0, 1, 3)
tar_txt = QLabel(window)
tar_txt.setObjectName(u"tar_txt")
gridLayout.addWidget(tar_txt, 14, 0, 1, 3)
fram_txt = QLabel(window)
fram_txt.setObjectName(u"fram_txt")
gridLayout.addWidget(fram_txt, 5, 0, 1, 3)
voi_txt = QLabel(window)
voi_txt.setObjectName(u"voi_txt")
gridLayout.addWidget(voi_txt, 9, 0, 1, 3)

miscs = {}
miscs['fram'] = QSpinBox(window)
miscs['fram'].setObjectName(u"fram")
miscs['fram'].setWrapping(False)
miscs['fram'].setMaximum(2048)
gridLayout.addWidget(miscs['fram'], 5, 4, 1, 2)

# set all options - filetypes
buttons = {}
buttons['VMR_bool'] = QCheckBox(window)
buttons['VMR_bool'].setObjectName(u"VMR_bool")
gridLayout.addWidget(buttons['VMR_bool'], 8, 4, 1, 1)
buttons['V16_bool'] = QCheckBox(window)
buttons['V16_bool'].setObjectName(u"V16_bool")
gridLayout.addWidget(buttons['V16_bool'], 8, 7, 1, 1)
buttons['VOI_bool'] = QCheckBox(window)
buttons['VOI_bool'].setObjectName(u"VOI_bool")
gridLayout.addWidget(buttons['VOI_bool'], 7, 4, 1, 1)
buttons['VMR/V16_bool'] = QCheckBox(window)
buttons['VMR/V16_bool'].setObjectName(u"VMR/V16_bool")
gridLayout.addWidget(buttons['VMR/V16_bool'], 7, 7, 1, 1)

# source inf labels
xinf = QLabel(window)
xinf.setObjectName(u"xinf")
gridLayout.addWidget(xinf, 13, 0, 1, 1)
yinf = QLabel(window)
yinf.setObjectName(u"yinf")
gridLayout.addWidget(yinf, 13, 3, 1, 1)
zinf = QLabel(window)
zinf.setObjectName(u"zinf")
gridLayout.addWidget(zinf, 13, 6, 1, 1)
# target inf labels
x2inf = QLabel(window)
x2inf.setObjectName(u"x2inf")
gridLayout.addWidget(x2inf, 15, 0, 1, 1)
y2inf = QLabel(window)
y2inf.setObjectName(u"y2inf")
gridLayout.addWidget(y2inf, 15, 3, 1, 1)
z2inf = QLabel(window)
z2inf.setObjectName(u"z2inf")
gridLayout.addWidget(z2inf, 15, 6, 1, 1)

# fill in source vox
miscs['x_s'] = QLineEdit(window)
miscs['x_s'].setObjectName(u"x_s")
gridLayout.addWidget(miscs['x_s'], 13, 1, 1, 2)
miscs['y_s'] = QLineEdit(window)
miscs['y_s'].setObjectName(u"y_s")
gridLayout.addWidget(miscs['y_s'], 13, 4, 1, 2)
miscs['z_s'] = QLineEdit(window)
miscs['z_s'].setObjectName(u"z_s")
gridLayout.addWidget(miscs['z_s'], 13, 7, 1, 2)
# fill in target vox
miscs['x_t'] = QLineEdit(window)
miscs['x_t'].setObjectName(u"x_t")
gridLayout.addWidget(miscs['x_t'], 15, 1, 1, 2)
miscs['y_t'] = QLineEdit(window)
miscs['y_t'].setObjectName(u"y_t")
gridLayout.addWidget(miscs['y_t'], 15, 4, 1, 2)
miscs['z_t'] = QLineEdit(window)
miscs['z_t'].setObjectName(u"z_t")
gridLayout.addWidget(miscs['z_t'], 15, 7, 1, 2)

# misc xyz for voi
miscs['x'] = QSpinBox(window)
miscs['x'].setObjectName(u"x")
miscs['x'].setWrapping(False)
miscs['x'].setMaximum(9999)
gridLayout.addWidget(miscs['x'], 10, 1, 1, 2)
miscs['y'] = QSpinBox(window)
miscs['y'].setObjectName(u"y")
miscs['y'].setWrapping(False)
miscs['y'].setMaximum(9999)
gridLayout.addWidget(miscs['y'], 10, 4, 1, 2)
miscs['z'] = QSpinBox(window)
miscs['z'].setObjectName(u"z")
miscs['z'].setWrapping(False)
miscs['z'].setMaximum(9999)
gridLayout.addWidget(miscs['z'], 10, 7, 1, 2)

# button settings
buttongo = QPushButton(window)
buttongo.setObjectName(u"buttongo")
gridLayout.addWidget(buttongo, 19, 2, 1, 5)

# check naming regex and sellect automatically
boolz = {'vmr' : buttons['VMR/V16_bool'],
         'v16' : buttons['VMR/V16_bool']}

# automatically check based on loaded file
try: boolz[curfn[-3:]].setChecked(True)
except: pass 

# fit to layout
formLayout.setLayout(0, QFormLayout.LabelRole, gridLayout)

# set information
window.setWindowTitle(u"Isovoxel - Nearest Neighbor Interpolation")

# set namings
vox_txt.setText(u"Source voxel size:")
tar_txt.setText(u"Target voxel size:")
voi_txt.setText(u"VOI bounds (not needed for vmr/v16):")
filetype_txt.setText(u"File Type: ")
fil_inf.setText(u"File Name")
dir_inf.setText(u"Directory Path")
fram_txt.setText(u"Framing Cube Dimension:")
buttons['VMR_bool'].setText(u"VMR")
buttons['V16_bool'].setText(u"V16")
buttons['VOI_bool'].setText(u"VOI")
buttons['VMR/V16_bool'].setText(u"VMR / V16")
buttongo.setText(u"Isovoxel")

# set labels for voxelsizes
xinf.setText(u"X: ")
yinf.setText(u"Y: ")
zinf.setText(u"Z: ")
x2inf.setText(u"X: ")
y2inf.setText(u"Y: ")
z2inf.setText(u"Z: ")

miscs['x'].setPrefix(u"X: ")
miscs['y'].setPrefix(u"Y: ")
miscs['z'].setPrefix(u"Z: ")
miscs['x'].setValue(x_0)
miscs['y'].setValue(y_0)
miscs['z'].setValue(z_0)

# also fatching automatically
dir_txt.setText(curdir)
fil_txt.setText(curfn)
miscs['x_s'].setText(x_s0)
miscs['y_s'].setText(y_s0)
miscs['z_s'].setText(z_s0)

# connect buttons to actually run scripts
buttongo.connect('clicked(bool)', runall)

window.setLayout(gridLayout)
window.show()
