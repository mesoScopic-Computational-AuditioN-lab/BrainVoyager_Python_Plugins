## tool to take brainvoyager VOI files, and make .label or .ctbl documents in order for ITKsnap and 3D-slicer to read VOI labels/colors

###############
## FUNCTIONS ##
###############
import PythonQt.Qt as qt
from PythonQt.QtGui import *
import re
import bvbabel
import numpy as np

def voi_to_ctbl(curdir, curfn, alpha=255):
    """create nifti file from voi file, voi list will be translated to base10 labels (1, 2, 3 etc.)"""
    voi_path = join(curdir, curfn)
    _, img = bvbabel.voi.read_voi(voi_path)
    # set outname based on voi name
    outname = '{}.ctbl'.format(re.search(r'.+(?=.*.voi$)',voi_path)[0])
    # create empy txt file
    with open(outname, 'w') as f:
        # set background label as first line (0s)
        f.write('0 background 0 0 0 0\n')
        # loop over all the labels
        for l in range(len(img)):
            # get important information from dictionary
            value = l+1
            label = re.sub('\s+', '_', img[l]['NameOfVOI'])
            rgb = ' '.join(map(str, img[l]['ColorOfVOI']))
            # create full string and write to file
            temp_str = f'{value} {label} {rgb} {alpha}\n'
            f.write(temp_str)
    return
    
def voi_to_itk(curdir, curfn):
    """create nifti file from voi file, voi list will be translated to base10 labels (1, 2, 3 etc.)"""
    voi_path = join(curdir, curfn)
    _, img = bvbabel.voi.read_voi(voi_path)
    # set outname based on voi name
    outname = '{}.label'.format(re.search(r'.+(?=.*.voi$)',voi_path)[0])
    # create empy txt file
    with open(outname, 'w') as f:
        # set background label as first line (0s)
        f.write('0 0 0 0 0 0 0 "background"\n')
        # loop over all the labels
        for l in range(len(img)):
            # get important information from dictionary
            value = l+1
            label = re.sub('\s+', '_', img[l]['NameOfVOI'])
            rgb = ' '.join(map(str, img[l]['ColorOfVOI']))
            # create full string and write to file
            temp_str = f'{value} {rgb} 1 1 1 "{label}"\n'
            f.write(temp_str)
    return

def runsteps_slicer():
    """run the processing steps"""
    # get the directories from the text fields
    curdir_ = curdir.text
    curfn_ = curdoc.text
    curalp_ = int(curalp.text)
    
    # get a redected fn of vmr (so we can also adjust v16s)
    voi_to_ctbl(curdir_, curfn_, alpha=curalp_)
    
def runsteps_itk():
    """run the processing steps"""
    # get the directories from the text fields
    curdir_ = curdir.text
    curfn_ = curdoc.text
    curalp_ = int(curalp.text)
    
    # get a redected fn of vmr (so we can also adjust v16s)
    voi_to_itk(curdir_, curfn_)

# see if a brainvoyager file is opened and use its parameters for text input defaults
try:
    doc_vmr = bv.active_document
    curdir_ = doc_vmr.path
    curfn_ = "..."
except: 
    curdir_ = "..."
    curfn_ = "..."


global curdir
global curdoc
global curalp


window =  QWidget()

dirinf =  QLabel("Directory Path")
curdir =  QLineEdit(curdir_)
docinf = QLabel("VOI Document")
curdoc = QLineEdit(curfn_)
alpinf = QLabel("VOI Alpha (0 - 255)")
curalp = QLineEdit(255)

buttongo =  QPushButton("Create .ctbl\t - (3D Slicer)")
buttongo.connect('clicked(bool)', runsteps_slicer)

buttongo2 =  QPushButton("Create .label\t - (ITK Snap)")
buttongo2.connect('clicked(bool)', runsteps_itk)

# set layout
layout =  QVBoxLayout()
layout.addWidget(dirinf)
layout.addWidget(curdir)
layout.addWidget(docinf)
layout.addWidget(curdoc)
layout.addWidget(alpinf)
layout.addWidget(curalp)

layout.addWidget(buttongo)
layout.addWidget(buttongo2)
window.setLayout(layout)
window.show()
