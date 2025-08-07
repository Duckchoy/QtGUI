# Defect Simulator
The main objective of the application is to simulate image intensities (for a GDS file) in presence of an EUV buried defect using rigorous EM solver.

## Package contents
    App
    ├── README.md           (start here)
    ├── requirements.txt    (modules in the venv)
    ├── __pycache__         (bytecode)
    ├── config_demo.ini     (input configuration demo)
    ├── src/
    ├   ├── __pycache__     (bytecode)
    ├   ├── MainApp.ui      (GUI xml file, QtDesigner generated)
    ├   ├── MainApp.py      (GUI generator script, mapped from xml)
    ├   ├── app.py          (launch script for GUI)
    ├   ├── main.py         (main script for all actions)
    ├   ├── utils.py        (contains all utility functions)
    ├   ├── defect.py       (simulates buried defect in mask)
    ├   ├── genImage.sh     (serializes process flow & monitors NB)
    ├   ├── *.tcl           (TCL scripts for running rigoros EM sim)
    ├   ├── *.csv/.dat      (supporting scripts for defect.py)
    ├── Examples/
    ├   ├── square/
    ├   ├── gratings/
    ├   ├── multilayer/

## Process Flow
    1. Control file generation: This step generates the nearfield images corresponding to a defect-free mask. The steps are:
        a. Need to check whether the initial coordinates are in 1X or 4X ? If not 4X, then scale the layout then launch the next steps.
        b. Rigorous EM simulation of the mask (material stack + geometry) to produce the input files for the EM run.
        [OPTIONAL]
        c. Run EM sim on the input files to produce NF amplitude and phase files (.gz).
        d. Run EM sim again to obtain the aerial images for a given projection optics settings (.tcl).
    
    2. Defect 3D mask generation:
        a. Readying the input mask files:
            I. Check the SW corner of the gds file has (0,0) coordinate: [shift operation] 
            II. Check the technology DBU is 1e-09: [scale operation]
            III. Read the stack information.
        b. Run main (this bypasses the previously used tcl)
        d. Copy the INI files from the `control` directory
        e. Rename & compresss the new 3D mask (data) file to match `load_grid file` line
