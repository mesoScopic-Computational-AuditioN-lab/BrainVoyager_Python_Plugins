## tool to take brainvoyager VOI files, and make .label or .ctbl documents in order for ITKsnap and 3D-slicer to read VOI labels/colors

###############
## FUNCTIONS ##
###############
import PythonQt.Qt as qt
from PythonQt.QtGui import *
import re
import bvbabel
import numpy as np

import struct
from bvbabel.utils import read_variable_length_string
from bvbabel.utils import write_variable_length_string

def runsteps():
    """run the processing steps"""
    # get the directories from the text fields
    curdir_ = curdir.text
    curfn_ = curdoc.text
    curbb_ = int(curbb.text)
    
    # get a redected fn of vmr (so we can also adjust v16s)
    bbox_nifti(curdir_, curfn_, curbb_)

def bbox_nifti(curdir, curfn, bbox, inbox_val=0, outbox_val=100):
    """create nifti file with a bounding box drawn based on vtc.
    inside values will be set to 0 (by default), outside values will be set to 100"""

    # load header information of vtc
    vtc_path = join(curdir, curfn)
    head = read_vtc_header(vtc_path)

    # create array with sellected bounding box
    img = np.ones([bbox, bbox, bbox], dtype=np.uint8)
    img *= outbox_val
    # populate inside of vtc with 0's
    img[-head['ZEnd'] : -head['ZStart'],
       -head['XEnd'] : -head['XStart'], 
       -head['YEnd'] : -head['YStart']] = inbox_val
    # transform to nifti
    img = nibabel.Nifti1Image(img, affine=np.eye(4))
    newname = re.search(r'.+(?=.*.vtc$)',curfn)[0]    # strip filename from naming
    if len(newname) > 17: newname = newname[:17]      # shorten naming somewhat if needed
    nibabel.save(img, '{}_BoundingBox.nii.gz'.format(join(curdir, newname)))
    return

def read_vtc_header(filename):
    """Read BrainVoyager VTC file.
    Parameters
    ----------
    filename : string
        Path to file.
    Returns
    -------
    header : dictionary
        Pre-data and post-data headers.
    """
    header = dict()
    with open(filename, 'rb') as f:
        # Expected binary data: short int (2 bytes)
        data, = struct.unpack('<h', f.read(2))
        header["File version"] = data

        # Expected binary data: variable-length string
        data = read_variable_length_string(f)
        header["Source FMR name"] = data

        # Expected binary data: short int (2 bytes)
        data, = struct.unpack('<h', f.read(2))
        header["Protocol attached"] = data

        if header["Protocol attached"] > 0:
            # Expected binary data: variable-length string
            data = read_variable_length_string(f)
            header["Protocol name"] = data
        else:
            header["Protocol name"] = ""

        # Expected binary data: short int (2 bytes)
        data, = struct.unpack('<h', f.read(2))
        header["Current protocol index"] = data
        data, = struct.unpack('<h', f.read(2))
        header["Data type (1:short int, 2:float)"] = data
        data, = struct.unpack('<h', f.read(2))
        header["Nr time points"] = data
        data, = struct.unpack('<h', f.read(2))
        header["VTC resolution relative to VMR (1, 2, or 3)"] = data

        data, = struct.unpack('<h', f.read(2))
        header["XStart"] = data
        data, = struct.unpack('<h', f.read(2))
        header["XEnd"] = data
        data, = struct.unpack('<h', f.read(2))
        header["YStart"] = data
        data, = struct.unpack('<h', f.read(2))
        header["YEnd"] = data
        data, = struct.unpack('<h', f.read(2))
        header["ZStart"] = data
        data, = struct.unpack('<h', f.read(2))
        header["ZEnd"] = data

        # Expected binary data: char (1 byte)
        data, = struct.unpack('<B', f.read(1))
        header["L-R convention (0:unknown, 1:radiological, 2:neurological)"] = data
        data, = struct.unpack('<B', f.read(1))
        header["Reference space (0:unknown, 1:native, 2:ACPC, 3:Tal, 4:MNI)"] = data

        # Expected binary data: char (4 bytes)
        data, = struct.unpack('<f', f.read(4))
        header["TR (ms)"] = data

        # Prepare dimensions of VTC data array
        VTC_resolution = header["VTC resolution relative to VMR (1, 2, or 3)"]
        DimX = (header["XEnd"] - header["XStart"]) // VTC_resolution
        DimY = (header["YEnd"] - header["YStart"]) // VTC_resolution
        DimZ = (header["ZEnd"] - header["ZStart"]) // VTC_resolution
        DimT = header["Nr time points"]

    return header

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
global curbb


window =  QWidget()

dirinf =  QLabel("Directory Path")
curdir =  QLineEdit(curdir_)
docinf = QLabel("VTC Document")
curdoc = QLineEdit(curfn_)
alpinf = QLabel("Bounding Box")
curbb = QLineEdit(512)

buttongo =  QPushButton("Create NifTi Bounding Box")
buttongo.connect('clicked(bool)', runsteps)

# set layout
layout =  QVBoxLayout()
layout.addWidget(dirinf)
layout.addWidget(curdir)
layout.addWidget(docinf)
layout.addWidget(curdoc)
layout.addWidget(alpinf)
layout.addWidget(curbb)

layout.addWidget(buttongo)
window.setLayout(layout)
window.show()
