# tool to take the dnn labelmap (splitted in rh+lh) and save it as two wmgm files (per hemisphere)

###############
## FUNCTIONS ##
###############
import PythonQt.Qt as qt
from PythonQt.QtGui import *
import re
import bvbabel
import numpy as np
from os.path import join, basename

def voi_to_vmr():
    """create vmr file from voi files, per hemisphere save as vmr"""
    # fetch files
    dirn = curdir.text
    voifn = voidoc.text
    vmrfn = vmrdoc.text
 
   # reading the voi file
    _, img = bvbabel.voi.read_voi(join(dirn, voifn))
    # read the vmr dummy file for header
    hdummy, _ = bvbabel.vmr.read_vmr(join(dirn, vmrfn))

    # set hemispher and xyz info
    hemispheres = ['LH', 'RH']
    x, y, z = hdummy['DimX'], hdummy['DimY'], hdummy['DimZ']

    # loop over hemispheres
    for hemisphere in hemispheres:
    
        # take name of vois
        voinms = [img[i]['NameOfVOI'] for i in range(len(img)) if img[i]['NameOfVOI'].endswith(hemisphere)]
        # split wm
        val100 = [voi for voi in voinms if voi.startswith('Grey')]
        val150 = [voi for voi in voinms if not voi.startswith('Grey')]
    
        # define new img
        new_img = np.zeros([x, y, z], dtype=np.uint8)

        for it in img:
            # check if desired voi
            if it['NameOfVOI'] in val100:
                new_img = _draw_img(new_img, it['Coordinates'], 100)

            if it['NameOfVOI'] in val150: 
                new_img = _draw_img(new_img, it['Coordinates'], 150)
    
        # set output filename
        outfn = f'WMGM_{hemisphere}.vmr'

        # convert to niftistyle so writevmr works proprarly
        new_img = np.transpose(new_img, (2,0,1))
        new_img = new_img[::-1, ::-1, ::-1]    

        # save file
        bvbabel.vmr.write_vmr(join(dirn,outfn), hdummy, new_img)

def _draw_img(img, coordinates, val):
    # get single dim coordinates
    xind = coordinates[:,0]
    yind = coordinates[:,1]
    zind = coordinates[:,2]
    # populate
    img[xind, yind, zind] = val
    return(img)
    
global curdir
global curvmrfn
global curvoifn

# see if a brainvoyager file is opened and use its parameters for text input defaults
try:
    doc = bv.active_document
    curdir = doc.path
    curvmrfn = doc.file_name
    curvoifn = basename(doc.voi_file)
except: 
    curdir = "..."
    curvmrfn = "..."
    curvoifn = "..."

window =  QWidget()

# set information
dirinf =  QLabel("Directory Path")
curdir =  QLineEdit(curdir)
voiinf = QLabel("VOI Document")
voidoc = QLineEdit(curvoifn)
vmrinf = QLabel("VMR File For Header")
vmrdoc = QLineEdit(curvmrfn)

buttongo =  QPushButton("Convert VOI LH-RH Labels to VMR")
buttongo.connect('clicked(bool)', voi_to_vmr)

# set layout
layout =  QVBoxLayout()
layout.addWidget(dirinf)
layout.addWidget(curdir)
layout.addWidget(voiinf)
layout.addWidget(voidoc)
layout.addWidget(vmrinf)
layout.addWidget(vmrdoc)

layout.addWidget(buttongo)
window.setLayout(layout)
window.show()
