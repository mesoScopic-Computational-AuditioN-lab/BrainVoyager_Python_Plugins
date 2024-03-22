# tool to map POI files and map them to another reference frame using SSM files

###############
## FUNCTIONS ##
###############
import PythonQt.Qt as qt
from PythonQt.QtGui import *
import re
import bvbabel
import numpy as np
from os.path import join, basename, split

def run_mapping():
    """Main function"""   

    # get fns and directories
    dirn = curdir.text
    poi_fn = poidoc.text

    # convert text within ssms to list
    ssmfulllist = ssmlist.toPlainText()
    ssmfulllist = ssmfulllist.split('\n')    

    # load poi file to use for mapping
    poi_head, poi_img = bvbabel.poi.read_poi(join(dirn, poi_fn))  

    # loop over ssm files and run mapping
    for ssm_fn in ssmfulllist:

        # load in current ssm and poi        
        ssm_head, ssm_map = bvbabel.ssm.read_ssm(join(dirn, ssm_fn))

        # map poi file using current ssm
        poi_new = map_poi(poi_img, ssm_map)

        # take prefix of ssmfile and fn of poifile
        ssm_prefix = re.match(r'^(.*)\.ssm$', ssm_fn).group(1)
        poi_suffix = split(poi_fn)[-1]
        # dynamically generate poi filename for saving
        out_poi = f'{ssm_prefix}_{poi_suffix}'

        # update user
        try: bv.print_to_log(f'Mapped poi using: {ssm_fn}\n -output fn: {out_poi}')
        except: pass

        # save the remapped poi
        bvbabel.poi.write_poi(join(dirn, out_poi), poi_head, poi_new)


def map_poi(poi_img, ssm_map):
    """Map POI file to other surface reference frame using SSM mapping file
    
    Input: 
    ------
    poi_img: list of dictonaries
        list of dictionaries as obtained from bvbabel.poi.read_poi 
    ssm_map: numpy array (of length vertices)
        map of vertex to vertex mapping
    
    Return:
    -------
    poi_new: list of dictionaries
        adjusted list of dictionaries with poi within post ssm reference frame"""

    poi_new = []  # predefine new list to store dicts
    
    # loop over pois
    for i in range(len(poi_img)):

        # get current poi
        poi_dict = poi_img[i].copy()

        # create empty array and convert to boolean coding
        data = np.zeros(ssm_map.shape)
        data[poi_dict['Vertices']] = 1

        # map data to new frame of reference
        newdata = data[ssm_map.astype(int)]      # hier problemen
        newidxs = np.nonzero(newdata)[0]

        # populate new poi
        poi_dict['Vertices'] = newidxs
        poi_dict['NrOfVertices'] = len(newidxs)

        poi_new.append(poi_dict)
    
    return poi_new
    
def runhelp():
    msg.exec_()
    
global curdir

# see if a brainvoyager file is opened and use its parameters for text input defaults
try:
    doc = bv.active_document
    curdir = doc.path
except: 
    curdir = "..."

window =  QWidget()

# set information
dirinf =  QLabel("Directory Path")
curdir =  QLineEdit(curdir)
ssminfo = QLabel('SSM transformation file name(s)')
ssmlist = QTextEdit('...')
ssmlist.setAcceptRichText(False)
poiinfo = QLabel('POI Document')
poidoc = QLineEdit('...')
buttongo =  QPushButton("Map POI using SSM(s)")
buttongo.connect('clicked(bool)', run_mapping)
help_but =  QPushButton("Help")
help_but.connect('clicked(bool)', runhelp)

# set layout
layout =  QVBoxLayout()
layout.addWidget(dirinf)
layout.addWidget(curdir)
layout.addWidget(ssminfo)
layout.addWidget(ssmlist)
layout.addWidget(poiinfo)
layout.addWidget(poidoc)
layout.addWidget(buttongo)
layout.addWidget(help_but)

window.setLayout(layout)

# set information
window.setWindowTitle(u"map POI files using SSM(s)")
                    
# add axtra information
msg = QMessageBox()
msg.setStyleSheet("QLabel{min-width: 600px;}");
msg.setText("""Tool to take BrainVoyager POI files and map them to different reference frames using SSM files(s)

Input: 
- Directory path (main parent directory of files): automatically loaded from opened BV file
- SSM transformation filenames: can be one or many, multiple items should be split by new lines (enter)
- POI document filename

Output: Adjusted POI files are saved using a combination of the SSM+POI naming convention, 
if SSM filenames indicate a subdirectory, POI files are saved within this subdirectory
- e.g. ssm:'Sub1/S1_SPH_GROUPALIGNED_INV.ssm' and poi:'Glasser/Glasser2016_LH.poi' will
       result in the new filename 'Sub1/S1_SPH_GROUPALIGNED_INV_Glasser2016_LH.poi'

Tips:
- Mapping of multiple subject in one go is possible using one line per subject within the 'SSM' input section.
- When mapping from standard to per subject surface maps, remember to use '_INV' mappings.
- Mapping should be done within a hemisphere.

See example of use below:""")

msg.setDetailedText("""Case 1: mapping from Altas (Glasser) to group average (single SSM)
-Directory Path: '/MRIData/PreProc'
-SSM: 'GroupAlignedAveragedFoldedCortex_LH_N-5_HIRES_SPH_ALIGNED_TO_HCP-Glasser2016_INV.ssm'
-POI: 'Glasser/HCP-Glasser2016_LH_22grouping.poi'

Case 2: mapping from group average to many participants (many SSMs)
-Directory Path: '/MRIData/PreProc'
-SSM: 
  /S01_SES1/WMGM_LH_Mid-GM_RECO_D300k_HIRES_SPH_GROUPALIGNED_INV.ssm
  /S02_SES1/WMGM_LH_Mid-GM_RECO_D300k_HIRES_SPH_GROUPALIGNED_INV.ssm
  /S03_SES1/WMGM_LH_Mid-GM_RECO_D300k_HIRES_SPH_GROUPALIGNED_INV.ssm
  /S04_SES1/WMGM_LH_Mid-GM_RECO_D300k_HIRES_SPH_GROUPALIGNED_INV.ssm
  /S05_SES1/WMGM_LH_Mid-GM_RECO_D300k_HIRES_SPH_GROUPALIGNED_INV.ssm
  /S06_SES1/WMGM_LH_Mid-GM_RECO_D300k_HIRES_SPH_GROUPALIGNED_INV.ssm
-POI: 'GroupAlignedAveragedFoldedCortex_LH_N-5_HIRES_SPH_ALIGNED_TO_HCP-Glasser2016_INV.ssm_HCP-Glasser2016_LH_22grouping.poi'

""")

window.show()
