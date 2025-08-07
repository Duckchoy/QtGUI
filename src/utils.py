#!/usr/bin/python3.8

# ************************************************ #
#             utils.py (Python v3.8)               #
#              Date: Sep-Nov, 2022                 #
#                                                  #
#  Contains various utility methods and classes    #
#  which are used in other Python scripts, namely  #
#  main.py and defect.py                           #
#                                                  #
# ************************************************ #

from __future__ import annotations
import os
import json
import gdspy
import sys
import shutil
import signal
import subprocess as sp
import psutil
import configparser as cp
from typing import List, Tuple, Union, Literal
import stat
import errno

__all__ = [
    "convert_pct_to_real_layer", "unpack_config_dicts", "update_env",
    "replace_file_lines", "is_file_big", "to_wafer_units", "safe_exit",
    "wafer_to_gds_units", "update_config", "CellManager", "MaskFile",
    "get_dir_start_pattern", "clean_up", "sigint_action",
    "psutil_terminate_callback"
    ]


def convert_pct_to_real_layer(pct: float, max_layers: int = 167) -> int:
    """ Converts a percentage value of layer to a real layer value
    (with respect to max_layers being at 100%--resist surface)
    """

    # TODO: Automate getting max_layers from stack file

    # Truncate any accidental unreal seed value
    pct = 100 if pct > 100 else pct

    # Redefine the range from 1 to MAX_LAYERS-1 to avoid "mishandling"
    real_layer = 1 + int((max_layers - 2) * pct / 100.)
    return real_layer


def unpack_config_dicts(config_file: Union[str, bytes, os.PathLike],
                     ) -> Tuple[dict, dict, dict, dict, dict]:
    """ Unpacks the configuration (INI) file into a set of dictionaries
    """

    config = cp.ConfigParser()
    config.read(config_file)

    tools = { # made private
        'EM*': config["TOOLS"]['EM*'],
        'EM*': config["TOOLS"]['EM*']
    }

    try:
        tools.update({'MPIQ': config["TOOLS"]['MPIQ']
                      })
    except KeyError:
        pass    # ignore it since it is written later in main.py

    mask = {
        'gds_file': config["MASK"]['gds_file'],
        'layer_id': json.loads(config["MASK"]['layer_id']),
        'pos_tone': bool(json.loads(config["MASK"]['pos_tone'])),
        'mag_scale': int(config["MASK"]['mag_scale'])
    }

    try:
        mask.update({'max_x': int(config["MASK"]['max_x']),
                     'max_y': int(config["MASK"]['max_y'])
                     })
    except KeyError:
        pass    # ignore it since it is written later in main.py

    defect = {
        'seed': json.loads(config["DEFECT"]['seed']),
        'location': json.loads(config["DEFECT"]['location']),
        'size': json.loads(config["DEFECT"]['size']),
    }

    compute = {
        'thermal_diffusivity': float(config["COMPUTE"]['thermal_diffusivity']),
        'fdtd_grid_size': json.loads(config["COMPUTE"]['fdtd_grid_size']),
        'max_time': int(config["COMPUTE"]['max_time']),
        'gen_control': bool(json.loads(config["COMPUTE"]['gen_control']))
    }

    pds = {
        'pool': config["PDS"]['pool'],
        'class': config["PDS"]['class'],
        'queue': config["PDS"]['queue'],
        'slots': int(config["PDS"]['slots']),
        'hosts': int(config["PDS"]['hosts']),
        'mail': config["PDS"]['mail']
    }

    return tools, mask, defect, compute, pds


def update_config(config_file: Union[str, bytes, os.PathLike],
                  section_name: str,
                  add_dict: dict) -> None:
    """ Updates the input configuration (INI) file. First, reads the
    whole file. Enumerates over the add_dict and adds these elements
    to the parser handle (for the given section). Then the handle
    overwrites the config.ini file.
    """
    parser = cp.ConfigParser()
    parser.read(config_file)
    for k, v in add_dict.items():
        parser.set(section_name, str(k), str(v))

    with open(config_file, "w+") as configfile:
        parser.write(configfile)

    return


def update_env(tools_env_dict: dict, set_pds_dict: dict) -> dict:
    """ Updates the current shell environment settings by adding the
    input settings. This method is not generic, contains hardcoded strings.
    """

    env = os.environ.copy()
    # update the current environment with the tools environments
    env.update(tools_env_dict)

    # Generate the string for MPI command MPIQ
    mpiq_cmd = \
        f"mpijob run --target {set_pds_dict['pool']}" + \
        f" --class {set_pds_dict['class']}" + \
        f" --qslot {set_pds_dict['queue']}" + \
        f" --mail {set_pds_dict['mail']}" + \
        f" --parallel slots={set_pds_dict['slots']},slots_per_host={set_pds_dict['hosts']}"

    misc_settings = {
        'OMP_NUM_THREADS': '8',
        'KMP_AFFINITY': "noverbose, norespect, compact",
        'MPIQ': mpiq_cmd,
        'pool': set_pds_dict['pool']
    }
    env.update(misc_settings)

    return env


def replace_file_lines(fnam: Union[str, bytes, os.PathLike],
                       line_nums: List[int],
                       replace_text_list: List[str]) -> None:
    """ Replaces pre-existing lines for a list of line numbers in file fnam.
    Suitable for smaller files only, not very memory efficient
    """

    if len(line_nums) != len(replace_text_list):
        print("[Error:utils.py] list lengths disagree")
        return

    with open(fnam, 'r') as foo:  # read all lines of the file
        lines = foo.readlines()

    for seq, line in enumerate(line_nums):
        lines[line - 1] = replace_text_list[seq] + '\n'  # replace line

    with open(fnam, 'w') as foo:  # and write everything back
        foo.writelines(lines)

    return


def is_file_big(in_file: Union[str, bytes, os.PathLike],
                size_cap: int = 100000) -> bool:
    """ Checks if the byte size of a file exceeds a size cap.
    """

    size_bytes = os.path.getsize(in_file)    # size in bytes
    is_big = size_bytes > size_cap
    return is_big


def to_wafer_units(gds_coords: List[float],
                   factor: int = 1000) -> List[int]:
    """ Converts` the elements in a list of coordinates to wafer unit in nm
    """
    wafer_coords = [int(coord * factor) for coord in gds_coords]
    return wafer_coords


def wafer_to_gds_units(wafer_coord: List[float], dbu: float) -> List[int]:
    """ Converts a wafer coordinate to GDS unit
    """
    gds_coords = [(round(coord*dbu, 6)) for coord in wafer_coord]
    return gds_coords


def safe_exit(errno_symbol: int,
              message: str,
              *paths: Union[str, os.PathLike]) -> None:
    """ Abort when a critical error is encountered. Throw an exit code
    along with the error message. Delete any file/dir provided in `paths`
    """

    err_number = int(errno_symbol)
    err_str = os.strerror(errno_symbol)

    err_message = f"[Errno {err_number}] {err_str}: {message}"

    # for path in paths:
    clean_up(paths)

    print("Validation Failed! \n")
    # Make this message pop in the UI
    sys.exit(err_message)  # raises a SystemExit


def _get_gds_wafer_units(gds_file: Union[str, bytes, os.PathLike]
                         ) -> Tuple[int, int, float]:
    """ Wafer coordinates are in unit of "u" (unit) meters.
    GDS file has grids of size "p" (precision) meters,
    Function obtains p, u, and the ratio of the two (DBU factor)

    Ex: A GDS file with precision=1nm stores wafer coordinate of [unit=1um]
    (1.0512, 0.0001)um = (1051.2, 0.1)nm as [after rounding to the nearest
    integer] (1051, 0). For precision=0.01nm this becomes (105120, 10)

    Returns: unit, precision, gds-to-wafer conversion factor
    """
    u, p = gdspy.get_gds_units(gds_file)
    p_u = round(1000 * p / u, 3)        # DBU
    # To go from GDS coordinate to Wafer, multiply p_u with GDS

    return u, p, p_u


def _get_cells_from_file(gds_file: Union[str, bytes, os.PathLike]
                         ) -> gdspy.Cell:
    """ Extracts the _last_ cell in the list of cells in a GDS file.
    There is some redundancy built into the gdspy library. Last one is
    the only relevant cell (contains all the desired layers).
    """

    gdsii = gdspy.GdsLibrary(infile=gds_file)
    cell_names = list(gdsii.cells.keys())
    coup_cell = gdsii.cells[cell_names[-1]]
    return coup_cell


class CellManager:
    """ A class to handle the gdspy.Cell object corresponding to a
    layer ID. Inputs: gdspy.Cell object, Layer ID [L,D]
    """

    def __init__(self, cell: gdspy.Cell, layer_id: [int, int]):

        self.cell = cell
        self.layer_id = layer_id
        self.layer, self.data_type = layer_id

    def is_valid_layer(self) -> bool:
        """ Checks if a given [L,D] layer exists in the cell
        """

        is_valid = False
        for _, poly in enumerate(self.cell.polygons):
            if (poly.layers[0] == self.layer and
                    poly.datatypes[0] == self.data_type):
                is_valid = True
                break
        return is_valid

    def view_gds(self, defect_location: List, defect_radius: List) -> None:
        """ Launches the native gdspy viewer to see a cell layout.
        Viewer settings are hard-coded.

        "   The view can be scrolled vertically with the mouse wheel, and horizontally by holding the shift key and using
        the mouse wheel. Dragging the 2nd mouse button also scrolls the view, and if control is held down, it scrolls
        10 times faster. You can zoom in or out using control plus the mouse wheel, or drag a rectangle on the window
        with the 1st mouse button to zoom into that area. A ruler is available by clicking the 1st mouse button anywhere
        on the view and moving the mouse around. The distance is shown in the status area. Double-clicking on any polygon
        gives some information about it. Color and pattern for each layer/datatype specification can be changed by left
        and right clicking on the icon in the layer/datatype list. Left and right clicking the text label changes the
        visibility. "
        """

        defect_cell = gdspy.Round(center=tuple(defect_location),
                                  radius=tuple(defect_radius),
                                  number_of_points=32,       # more points make the curve smoother
                                  layer=1 + self.layer,
                                  datatype=1 + self.data_type
                                  )

        gdspy.LayoutViewer(library=None, cells=self.cell.add(defect_cell),
                           pattern={'default': 7},
                           background='#FFFFFF',
                           width=1000, height=750)

    def get_poly_set(self) -> gdspy.PolygonSet:
        """ Returns all the polygons for a given cell & layer ID as a PolygonSet.
        """
        polys_in_layer = self.cell.get_polygons(by_spec=self.layer_id)
        poly_set = gdspy.PolygonSet(polys_in_layer,
                                    layer=self.layer,
                                    datatype=self.data_type)

        return poly_set


class MaskFile:
    """ A class to handle the GDS file and obtain its various attributes
    """

    def __init__(self,
                 gds_file: Union[str, os.PathLike, List[str]],
                 layer_id: [int, int],
                 mag_x: float = 1,
                 tone: Literal[0, 1] = 0):

        self.gds_file = gds_file
        self.layer_id = layer_id
        self.mag_x = mag_x
        self.tone = tone

        self.unit, self.precision, self.dbu = _get_gds_wafer_units(gds_file)

        self.cell = _get_cells_from_file(gds_file)

        [self.SW, self.NE] = [[None, None], [None, None]]
        self.span = [None, None]
        self.center = [None, None]

    def remove_unwanted_layers(self):
        """ Remove all the layers that are not relevant to defect analysis
        """
        self.cell.remove_polygons(lambda p, l, d:
                                  l != self.layer_id[0] or
                                  d != self.layer_id[1]
                                  )

    def get_dimensions(self) -> None:
        """ Computes corners of a cell, its X & Y span and center coordinates
        """

        # SW:=[x_min, y_min]; NE:=[x_max, y_max]
        [self.SW, self.NE] = self.cell.get_bounding_box()

        self.span = self.NE - self.SW
        self.center = [round(p / 2, 5) for p in self.SW + self.NE]

    def translate_cell(self, distance: [float, float]) -> None:
        """ Wrapper over gdspy.PolygonSet.translate() method.
        This does the same thing as BShift of MZ: 2D translate a cell.
        The output layer is over-written on the input layer.

        Inputs: translation distance 2D list (preferably in GDS units)
        Returns: updates the member 'cell' in the self object
        """
        poly_set = CellManager(self.cell, self.layer_id).get_poly_set()
        poly_set.translate(distance[0], distance[1])

        # Empty out the current cell and then add ONLY the layer
        self.cell.remove_polygons(lambda p, l, d: True)
        self.cell.add(poly_set)

    def scale_cell(self, mag: float) -> None:
        """ Wrapper over gdspy.PolygonSet.scale() method.
        This does the same thing as BScale of MZ: 2D scale a cell
        The 'center' of scaling is frozen to origin and X & Y axes are scaled
        equally. The output layer is over-written on the input layer.

        Inputs: scaling magnitude (preferably in GDS units)
        Returns: updates the member 'cell' in the self object
        """
        poly_set = CellManager(self.cell, self.layer_id).get_poly_set()
        poly_set.scale(scalex=mag, scaley=None, center=(0, 0))

        # Empty out the current cell and then add ONLY the layer
        self.cell.remove_polygons(lambda p, l, d: True)
        self.cell.add(poly_set)

    def write_new_file(self,
                       out_gds_path: Union[str, bytes, os.PathLike]) -> None:
        """ Writes a new GDS file based off of whatever cell object is available.
        """

        writer = gdspy.GdsWriter(out_gds_path, unit=self.unit, precision=self.precision)
        writer.write_cell(self.cell)
        writer.close()


def get_dir_start_pattern(path: Union[str, bytes, os.PathLike],
                          pattern: str) -> List[str]:
    """ Get the list of directories in a path that match a starting pattern
    """
    dirs = []
    for obj in os.scandir(path):
        if obj.is_dir() and obj.name.startswith(pattern):
            dirs.append(obj.name)

    return dirs


def clean_up(objects: Union[str, os.PathLike, List[str], List[os.PathLike], Tuple[str], Tuple[os.PathLike]],
             ignore_err: bool = True) -> None:
    """ Wrapper around shutil.rmtree to remove all objects inside a
    list/tuple of directories. Set ignore_err=True to ignore any errors.
    """

    if type(objects) is list or tuple:
        for obj in objects:
            shutil.rmtree(obj, ignore_errors=ignore_err)
    else:
        shutil.rmtree(objects, ignore_errors=ignore_err)


def sigint_action(popen_obj:  Union[sp.Popen[bytes], sp.Popen],
                  remove_dir: Union[str, bytes, os.PathLike, None] = None
                  ) -> None:
    """ When a SIGINT (Ctrl+C) event is passed to a subprocess pipe it is
    passed to the popen_obj and any cleaning required is performed.
    """
    print("\nJob cancelled by user, please wait till complete termination..")
    print("")
    try:
        popen_obj.send_signal(signal.SIGINT)
        print("All processes have terminated now.\n")
    except ProcessLookupError:
        pass

    if remove_dir:
        shutil. rmtree(remove_dir, ignore_errors=True)

    popen_obj.wait()
    sys.exit(1)


def psutil_terminate_callback(proc: psutil.Process) -> None:
    """ Callback function for process termination by psutil.wait_procs()
    """
    exit_code = proc.returncode
    exit_string = 'Failure!' if exit_code else 'Success!'
    print(f"PID {proc.pid} has terminated with Exit Code {exit_code} ({exit_string})\n")

    if exit_code:
        sys.exit(f"Non-zero exit from PID {proc.pid}. Exiting application.")
