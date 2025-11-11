import PythonQt.Qt as Qt
from PythonQt.QtGui import *
import os
import numpy as np

# ==============================
# BIDS STRUCTURE CREATOR
# ==============================

def runbids():
    """Main function to create an empty BIDS folder hierarchy"""
    parent_dir = bids_misc['parent_txt'].text
    nsubs = bids_misc['sub_spin'].value
    nses = bids_misc['ses_spin'].value
    selected_types = [key for key, cb in bids_buttons.items() if cb.isChecked()]

    if not parent_dir or parent_dir.strip() in ["...", ""]:
        bv.print_to_log('\nPlease specify a valid parent directory.\n')
        return
    if len(selected_types) == 0:
        bv.print_to_log('\nPlease select at least one datatype.\n')
        return

    bv.print_to_log(f"\nCreating BIDS folder structure in:\n  {parent_dir}\n"
                    f" - Subjects: {nsubs}\n - Sessions: {nses}\n - Datatypes: {', '.join(selected_types)}")

    os.makedirs(parent_dir, exist_ok=True)

    for s in range(1, nsubs + 1):
        sub_name = f"sub-{s:02d}"
        sub_path = os.path.join(parent_dir, sub_name)
        if nses > 1:
            for se in range(1, nses + 1):
                ses_name = f"ses-{se:02d}"
                ses_path = os.path.join(sub_path, ses_name)
                for dt in selected_types:
                    os.makedirs(os.path.join(ses_path, dt), exist_ok=True)
        else:
            for dt in selected_types:
                os.makedirs(os.path.join(sub_path, dt), exist_ok=True)

    bv.print_to_log("\nBIDS structure successfully created.\n")


def runhelp():
    msg.exec_()


# ==============================
# CREATE GUI
# ==============================

# top-level window
window = QWidget()
window.setObjectName(u"window")
window.resize(320, 480)
window.setWindowTitle(u"BIDS Structure Generator")

# layout grid
formLayout = QFormLayout(window)
formLayout.setObjectName(u"formLayout")
gridLayout = QGridLayout()
gridLayout.setObjectName(u"gridLayout")

# ----------------------------
# GUI ELEMENTS
# ----------------------------

# title
title = QLabel(window)
title.setObjectName(u"title")
title.setText(u"BIDS Folder Structure Generator")
gridLayout.addWidget(title, 0, 0, 1, 5)

# separator line
line = QFrame(window)
line.setFrameShape(QFrame.HLine)
line.setFrameShadow(QFrame.Sunken)
gridLayout.addWidget(line, 1, 0, 1, 5)

# parent path input
parent_label = QLabel(window)
parent_label.setText(u"Parent Project Directory:")
gridLayout.addWidget(parent_label, 2, 0, 1, 3)

bids_misc = {}
bids_misc['parent_txt'] = QLineEdit(window)
bids_misc['parent_txt'].setObjectName(u"parent_txt")
bids_misc['parent_txt'].setPlaceholderText(u"/path/to/myProject")
gridLayout.addWidget(bids_misc['parent_txt'], 3, 0, 1, 5)

# datatypes
dtype_label = QLabel(window)
dtype_label.setText(u"Select Data Types:")
gridLayout.addWidget(dtype_label, 4, 0, 1, 3)

bids_buttons = {}
dtype_list = ['anat', 'func', 'fmap', 'dwi', 'perf',
              'eeg', 'meg', 'ieeg', 'beh', 'pet', 'micr', 'nirs', 'motion', 'mrs']

for i, dtype in enumerate(dtype_list):
    bids_buttons[dtype] = QCheckBox(window)
    bids_buttons[dtype].setObjectName(u"bids_" + dtype)
    bids_buttons[dtype].setText(dtype)
    gridLayout.addWidget(bids_buttons[dtype], 5 + (i // 5), i % 5, 1, 1)

# subjects and sessions
sub_label = QLabel(window)
sub_label.setText(u"Number of Subjects:")
gridLayout.addWidget(sub_label, 9, 0, 1, 2)

bids_misc['sub_spin'] = QSpinBox(window)
bids_misc['sub_spin'].setRange(1, 999)
bids_misc['sub_spin'].setValue(1)
gridLayout.addWidget(bids_misc['sub_spin'], 9, 2, 1, 1)

ses_label = QLabel(window)
ses_label.setText(u"Number of Sessions:")
gridLayout.addWidget(ses_label, 10, 0, 1, 2)

bids_misc['ses_spin'] = QSpinBox(window)
bids_misc['ses_spin'].setRange(1, 999)
bids_misc['ses_spin'].setValue(1)
gridLayout.addWidget(bids_misc['ses_spin'], 10, 2, 1, 1)

# separator line
line2 = QFrame(window)
line2.setFrameShape(QFrame.HLine)
line2.setFrameShadow(QFrame.Sunken)
gridLayout.addWidget(line2, 11, 0, 1, 5)

# buttons
bids_run = QPushButton(window)
bids_run.setObjectName(u"bids_run")
bids_run.setText(u"Generate BIDS Structure")
gridLayout.addWidget(bids_run, 12, 0, 1, 3)

help_but = QPushButton(window)
help_but.setObjectName(u"help_but")
help_but.setText(u"Help")
gridLayout.addWidget(help_but, 12, 3, 1, 2)

# ----------------------------
# CONNECT BUTTONS
# ----------------------------
bids_run.connect('clicked(bool)', runbids)
help_but.connect('clicked(bool)', runhelp)

# ----------------------------
# HELP MESSAGE
# ----------------------------
msg = QMessageBox()
msg.setStyleSheet("QLabel{min-width: 600px;}")
msg.setText("""BIDS Structure Generator

This tool creates an empty BIDS-compliant folder hierarchy.

Steps:
  1. Specify a parent project directory (existing or new).
  2. Select which datatypes to include (anat, func, fmap, etc.).
  3. Set number of subjects and sessions.
  4. Press 'Generate BIDS Structure' to create the folders.

Example output:
  myProject/
  ├── sub-01/
  │   ├── anat/
  │   └── func/
  └── sub-02/
      ├── anat/
      └── func/
""")

# fit layout and show window
formLayout.setLayout(0, QFormLayout.LabelRole, gridLayout)
window.setLayout(gridLayout)
window.show()