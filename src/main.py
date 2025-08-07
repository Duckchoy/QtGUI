#!/usr/bin/python3.8

# ************************************************ #
#              main.py (Python v3.8)               #
#               Date: Sep-Nov, 2022                #
#                                                  #
#  This file validates user inputs and transforms  #
#  some of the parameters and the GDS file.        #
#  After completing execution this over-writes or  #
#  creates the following dirs or files:            #
#      (1) config.ini   (min/max, mpiq, location)  #
#      (2) mask.gds     (scales/ translates)       #
#      (3) genImage.sh  (monitor for jobs)         #
#      (4) ./control/{2-3}     (defect-free files) #
#                                                  #
# ************************************************ #

import os
import shutil
import utils
import datetime
import logging
import subprocess as sp
import errno
import sys
import glob
import psutil
# import gdspy

# Variable from outer space; when True, stop before launching sims
try:
    inspect_bool = int(sys.argv[1])
except IndexError:  # when used from command line without any argv
    inspect_bool = 0

# --------- CONSTANTS --------- #
#
LOG_FILE = "validation.log"
CONTROL_DIR = 'control'
OUT_GDS_FILE = "mask.gds"
CONFIG_IN_FILE = 'config.ini'
DEFECT_SIM_SRC = 'defect.py'
DEFECT_SIM_LOG = 'defect.log'
DATA_REPO_PREFIX = "run_"
MTV_GZIP_FILE = "mask3d_por.mtvdat.gz"
MPI_EM_SHELL_PIPE = "genImage.sh"

STALE_DIR_THRESHOLD = 12  # max working directories warning
WARN_MIN_SPAN_NM = 150  # min required span of a mask
WARN_MAX_SPAN_NM = 750  # max allowed span of a mask
MAX_GRID_PCT = 2  # max compute grid size as pct of span
GEN_NF_LD_LINE = 81  # line num with L/D specs in gen_NF.tcl

# ===================================================== #
#              1.1 Files/Dirs path Setup                #
# ===================================================== #

# Record launch time
launch_time = datetime.datetime.now()
print(f'\n\n ============= {launch_time.strftime("%d-%b-%Y %H:%M:%S")} ============\n')
# print(f'\nApplication launched at: \n')

curr_working_dir = os.getcwd()
# Files existing in the current directory
ctrl_dir_path = os.path.join(curr_working_dir, CONTROL_DIR)
config_in_path = os.path.join(curr_working_dir, CONFIG_IN_FILE)
data_repo = DATA_REPO_PREFIX + launch_time.strftime("%y%m%d%H%M%S")
data_repo_path = os.path.join(curr_working_dir, data_repo)

abs_path_src_dir = os.path.abspath(os.path.dirname(__file__))
# Files existing in the src directory
defect_sim_src_path = os.path.join(abs_path_src_dir, DEFECT_SIM_SRC)
gen_nf_tcl_path = os.path.join(abs_path_src_dir, "gen_NF.tcl")
gen_image_tcl_path = os.path.join(abs_path_src_dir, "gen_image.tcl")
mpi_em_shell_path = os.path.join(abs_path_src_dir, MPI_EM_SHELL_PIPE)

# Files existing in the data repository
defect_sim_log_path = os.path.join(data_repo_path, DEFECT_SIM_LOG)
out_gds_path = os.path.join(data_repo_path, OUT_GDS_FILE)
run_config_path = os.path.join(data_repo_path, CONFIG_IN_FILE)

# ===================================================== #
#              1.2 Setting up the logger                #
# ===================================================== #

# Configuring the logging module
logging.basicConfig(
    level=logging.INFO,
    filename=LOG_FILE, filemode='w',
    format='[%(levelname)s: %(name)s] %(message)s'
)

# Setup different logger names
GlobalInfo = logging.getLogger(name=LOG_FILE)  # file-level information
EnvLog = logging.getLogger(name='Environment')  # tools environment setting
LayLog = logging.getLogger(name='Layout')  # layout file related logs
DefectLog = logging.getLogger(name='Defect')  # defect related logs
ModelLog = logging.getLogger(name='Model')  # model settings related logs
SimLog = logging.getLogger(name='Simulation')  # issues encountered during simulations

# Counters of Errors & Warnings
err_count, warn_count = 0, 0

# Timestamp: BEGIN
GlobalInfo.info(
    f'Run launched at: {launch_time.strftime("%d-%b-%Y %H:%M:%S")} '
    f'\n ==========================================================\n')
# TODO: Ideally all the stream (prints) should also go to logger.

# ===================================================== #
#             1.3 Prepping the environment              #
# ===================================================== #

if not os.path.exists(config_in_path):
    err_count += 1
    err_message = "Could not locate 'config.ini' file. \n"
    EnvLog.critical(err_message)
    utils.safe_exit(errno.ENOENT, err_message)

(tools_env, mask_data, defect_info, set_compute, set_pds
 ) = utils.unpack_config_dicts(config_in_path)

layer_id = mask_data["layer_id"]

# Validate the 2 essential tools are available
if not os.path.exists(tools_env["em"]):
    err_count += 1
    err_message = "Could not locate the em version. \n"
    EnvLog.error(err_message)
    print(err_message)

if not os.path.exists(tools_env["EM"]):
    err_count += 1
    err_message = "Could not locate the EM version. \n"
    EnvLog.error(err_message)
    print(err_message)

# Ensuring one of the large memory machines is used
host_check = sp.run('hostname', shell=True, capture_output=True, text=True)
host_name = host_check.stdout
if host_name[:3] not in ["tor", "tsc"]:
    err_message = "Jobs may fail on this machine. Please use a tapeout machine.\n"
    EnvLog.critical(err_message)
    utils.safe_exit(errno.ENOMEM, err_message, data_repo_path)

# Ensuring SLES 12+ is used to avoid conflict with MZ or MPI
grep_os_version = sp.run("grep '^VERSION_ID' /etc/os-release",
                         shell=True, capture_output=True, text=True)
grep_return = grep_os_version.stdout
version_id = float(grep_return[12:-2])
if version_id < 12:
    err_message = f"OS version {version_id} may cause conflicts. "
    f"Please use a SLES 12+ machine.\n"
    EnvLog.critical(err_message)
    utils.safe_exit(errno.EACCES, err_message, data_repo_path)

# Ensuring user has permission to do rwx (=4+2+1) on this system
umask_check = sp.run("umask", shell=True, capture_output=True, text=True)
umask = umask_check.stdout
owner_permissions = umask[1]
if owner_permissions != "0":
    err_message = f"User may not have sufficient permission to work here. "
    f"User `umask` permission level is {owner_permissions}. "
    f"Consider changing it to 0.\n"
    EnvLog.critical(err_message)
    utils.safe_exit(errno.EACCES, err_message, data_repo_path)

print("All system requirements are satisfied \n")

# ===================================================== #
#       1.4 Create data repository & runtime env        #
# ===================================================== #

# The gen_NF.tcl needs to have the correct L/D on its line #81
# Make a copy of src/gen_NF at the CWD, edit it, send to others
shutil.copy2(gen_nf_tcl_path, curr_working_dir)
local_gen_nf_path = os.path.join(curr_working_dir, "gen_NF.tcl")

utils.replace_file_lines(
    fnam=local_gen_nf_path,
    line_nums=[GEN_NF_LD_LINE],
    replace_text_list=[
        f"gds_layer layer={layer_id[0]} datatype={layer_id[1]} deposit"
    ]
)

try:
    # create a timestamped working directory from $PWD
    os.mkdir(data_repo_path)
    print(f"Directory '{data_repo}' was created for saving all the data\n")
except FileNotFoundError:
    err_message = "Unable to locate parent directory.\n"
    EnvLog.critical(err_message)
    utils.safe_exit(errno.ENOENT, err_message)
else:
    shutil.copy2(config_in_path, data_repo_path)
    shutil.copy2(local_gen_nf_path, data_repo_path)
    shutil.copy2(gen_image_tcl_path, data_repo_path)
    shutil.copy2(mpi_em_shell_path, data_repo_path)

# Once all tests passed, create an environment for all subprocess pipes
runtime_env = utils.update_env(tools_env, set_pds)

# Update the PDS field with the full MPIQ string
utils.update_config(run_config_path,
                    section_name="PDS",
                    add_dict={"mpiq": f'\"{runtime_env["MPIQ"]}\" '}
                    )

# Ensuring there are not too many stale working directories
stale_dirs = utils.get_dir_start_pattern(path='.',
                                         pattern=DATA_REPO_PREFIX)
if len(stale_dirs) >= STALE_DIR_THRESHOLD:
    err_message = "I found too many stale directories. Consider purging.\n"
    EnvLog.warning(err_message)
    print(err_message)

    # TODO: Let this be a button for the user to do
    # utils.clean_up(stale_dirs[:-2], ignore_err=True)
    # print("Purging 10 of the stale directories")

# ===================================================== #
#       2.1 GDS data validation & transformation        #
# ===================================================== #

gds_file_path = mask_data["gds_file"]
gds_file = os.path.basename(gds_file_path)

print(f"Starting validation and transformation of '{gds_file}': \n")

# Existence checking of the file
if not os.path.exists(gds_file_path):
    err_message = f"Specified GDS file '{gds_file}' was not located, " \
                  f"check INI file for possible typos \n"
    LayLog.critical(err_message)
    utils.safe_exit(errno.ENOENT, err_message, data_repo_path)

# Format checking the input file
if not gds_file.endswith('.gds'):
    err_message = "Please provide a file in GDS format only \n"
    LayLog.critical(err_message)
    utils.safe_exit(errno.ENOENT, err_message, data_repo_path)

# Imposing a 100000 byte cutoff on the file size
if utils.is_file_big(gds_file_path):
    warn_count += 1
    LayLog.warning("GDS file seems quite large, consider clipping it. \n")

mask = utils.MaskFile(gds_file_path, layer_id)
# gdspy.LayoutViewer(library=None, cells=mask.cell)

mask.remove_unwanted_layers()
# gdspy.LayoutViewer(library=None, cells=mask.cell)

cell_man = utils.CellManager(mask.cell, layer_id)

# Layer existence check
if not cell_man.is_valid_layer():
    err_count += 1
    err_message = f"Layer {cell_man.layer_id} does not exist in \'{gds_file}\' \n"
    LayLog.critical(err_message)
    utils.safe_exit(errno.EIO, err_message, data_repo_path)

info_message = f"Wafer unit: {mask.unit}, GDS precision: {mask.precision}, Global DBU: {mask.dbu}\n"
LayLog.info(info_message)
print(info_message)

mask.get_dimensions()

# Update the configuration file with "real" span params
try:
    [max_x, max_y] = utils.to_wafer_units(mask.span)
except Exception as e:
    err_count += 1
    LayLog.error(e)
    LayLog.error("Could not extract the size of the mask.\n")
else:
    if max_x < WARN_MIN_SPAN_NM or max_y < WARN_MIN_SPAN_NM:  # in nanometers
        warn_count += 1
        LayLog.warning(f"Layout seems very small (<{WARN_MIN_SPAN_NM}nm). "
                       f"Consider using a larger clip.\n")

    if max_x > WARN_MAX_SPAN_NM or max_y > WARN_MAX_SPAN_NM:  # in nanometers
        warn_count += 1
        LayLog.warning(f"Layout seems very large (>{WARN_MAX_SPAN_NM}nm). "
                       f"Consider using a smaller clip.\n")

    info_message = f"SW coordinates: {utils.to_wafer_units(mask.SW)}nm"
    LayLog.info(info_message)
    print(info_message)
    info_message = f"NE coordinates: {utils.to_wafer_units(mask.NE)}nm"
    LayLog.info(info_message)
    print(info_message)
    info_message = f"[x,y] axes span: [{max_x}, {max_y}]nm \n"
    LayLog.info(info_message)
    print(info_message)

    utils.update_config(run_config_path,
                        section_name="MASK",
                        add_dict={"max_x": max_x,
                                  "max_y": max_y}
                        )

    # The model script throws errors for very large grid size
    [delta_x, delta_y, delta_z] = set_compute["fdtd_grid_size"]
    x_grid_threshold = int(max_x * MAX_GRID_PCT)
    y_grid_threshold = int(max_y * MAX_GRID_PCT)

    if delta_x > x_grid_threshold:
        warn_count += 1
        ModelLog.warning(f"X-axis grid size is very large (set below {x_grid_threshold})."
                         f" Defect simulation may break.\n")

    if delta_y > y_grid_threshold:
        warn_count += 1
        ModelLog.warning(f"Y-axis grid size is very large (set below {y_grid_threshold})."
                         f" Defect simulation may break.\n")

# This ensures the SW point is set to origin and the layer of interest is loaded, removing other unused layers.
mask.translate_cell([-mask.SW[0], -mask.SW[1]])
mask.get_dimensions()

info_message = "[After transformation]"
LayLog.info(info_message)
print(info_message)
info_message = f"SW coordinates: {utils.to_wafer_units(mask.SW)}nm"
LayLog.info(info_message)
print(info_message)
info_message = f"NE coordinates: {utils.to_wafer_units(mask.NE)}nm \n"
LayLog.info(info_message)
print(info_message)

# Double-check the SW point is at the origin indeed
if any(mask.SW):
    err_count += 1
    LayLog.error(f"SW corner of the layout, {mask.SW}, in not at the origin: "
                 f"Cell translation failed. Please report.\n")

# create a new GDS file with the transformed layer
mask.write_new_file(out_gds_path=out_gds_path)

# ===================================================== #
#              2.2 Defect data validation               #
# ===================================================== #

info_message = f"Defect coordinate is set to the center of the layout: " \
               f"{utils.to_wafer_units(mask.center)}nm \n"
DefectLog.info(info_message)

defect_size = defect_info["size"]

if any(dim > 100 for dim in defect_size):
    warn_count += 1
    DefectLog.warning("Defect size seems unusually large. "
                      "10nm-20nm is more typical.\n")

if any(dim < 10 for dim in defect_size):
    warn_count += 1
    DefectLog.warning("Defect size seems unusually small. "
                      "10nm-20nm is more typical.\n")

# Get defect location w.r.t the SW corner as origin
defect_loc_gds_units = [round(p / 1000, 4) for p in defect_info["location"]]
defect_coords = [round(sum(x), 4) for x in zip(defect_loc_gds_units, mask.center)]

for c, s in zip(defect_coords, mask.span):
    if abs(c) >= s:
        err_count += 1
        err_message = f"Defect location is outside the mask layout!\n"
        print(err_message)
        DefectLog.error(err_message)

utils.update_config(run_config_path,
                    section_name="DEFECT",
                    add_dict={"location": utils.to_wafer_units(defect_coords)}
                    )

# ===================================================== #
#           2.4 Finishing validation steps              #
# ===================================================== #

message = f"{err_count} Errors, {warn_count} Warnings found so far\n"
GlobalInfo.info(message)
print(message)

if err_count:
    sys.exit("Validation has failed!\n")

if inspect_bool:
    print("Inspection completed successfully. Press RUN to launch simulations. \n")
    print("Please close the GDS viewer to continue. \n")
    cell_man.view_gds(defect_location=defect_coords,
                      defect_radius=utils.wafer_to_gds_units(defect_size[0:-1], 0.001))

    # No need to keep the data repo when just inspecting
    shutil.rmtree(data_repo_path, ignore_errors=True)
    print(f"Directory '{data_repo}' was removed.")
    print("------------------------------------\n")
    sys.exit(0)
else:
    print(f"Transformed GDS file was saved as 'mask.gds' in {data_repo}\n")

    message = "Moving on to launch the em & EM simulations.. \n"
    GlobalInfo.info(message)
    print(message)

# ===================================================== #
#         2.5 Generating the control directory          #
# ===================================================== #

# A new control directory is created (and shell pipe is executed)
# only when the user asked for it or when control dir does not exist.

ctrl_dir_exists = os.path.isdir(ctrl_dir_path)  # control dir exists?
usr_req_new_ctrl = set_compute["gen_control"]  # user request

# switch for whether to create a new set of control files
gen_new_ctrl = (not ctrl_dir_exists) or usr_req_new_ctrl

# when there is no pre-existing control or when user requested a new control
if gen_new_ctrl:

    # TEMP: This is needed until we align gen_NF & python stack
    mask.scale_cell(round(1. / mask_data['mag_scale'], 3))

    # Remove pre-existing control dir, ignore if it does not exist (ignore_err=True)
    if ctrl_dir_exists:
        try:
            shutil.rmtree(ctrl_dir_path)
        except OSError:
            err_message = "The 'control' directory from the previous run is currently being used. " \
                          " Uncheck 'Generate defect-free images' or use a different destination."
            utils.safe_exit(errno.EBUSY, err_message)

        print("User requested new set of defect-free images.\n"
              "I am deleting the pre-existing 'control' directory\n")

    try:
        os.mkdir(ctrl_dir_path)
        print("Created a new 'control' directory for benchmarking\n")
    except Exception as e:
        err_num, _ = e.args
        if err_num == errno.EEXIST:
            err_count += 1
            EnvLog.error("Unable to delete the control directory. Server "
                         "may be busy. Please re-run or restart the application.\n")

        if err_num in (errno.EPERM, errno.EACCES, errno.EROFS):
            err_count += 1
            EnvLog.error("Working directory may be write protected. "
                         "Change permissions (chmod) to `rwx`.\n")
    else:
        # create a copy of the current layout inside CD; called mask.gds for gen_NF
        mask.write_new_file(out_gds_path=ctrl_dir_path + '/' + OUT_GDS_FILE)

        # Copy the shell & tcl files into CD
        shutil.copy2(local_gen_nf_path, ctrl_dir_path)
        shutil.copy2(gen_image_tcl_path, ctrl_dir_path)
        shutil.copy2(mpi_em_shell_path, ctrl_dir_path)
        os.remove(local_gen_nf_path)


# ===================================================== #
#            3. Launching All the Simulations           #
# ===================================================== #

print("------------------------------------")
print("\tLaunching simulations")
print("------------------------------------\n")

# ===================================================== #
#        3.1 Defect sim & em gen_NF (parallel)         #
# ===================================================== #

# Launch defect.py & em in control (when needed) in parallel
try:
    defect_sim_sp = sp.Popen(f"python {defect_sim_src_path} &> {defect_sim_log_path}",
                             shell=True, cwd=data_repo_path)
    defect_sim_pid = defect_sim_sp.pid
    procs_list = [psutil.Process(defect_sim_pid)]
    print(f"> Launching defect simulation [PID: {defect_sim_pid}] in {data_repo}..\n")

    if gen_new_ctrl:
        ctrl_em_sp = sp.Popen("$em gen_NF.tcl &> em.log", shell=True,
                               cwd=ctrl_dir_path, env=runtime_env)
        ctrl_em_pid = ctrl_em_sp.pid
        procs_list += [psutil.Process(ctrl_em_pid)]
        print(f"> Launching em [PID: {ctrl_em_pid}] in control directory..\n")

    # psutil.wait_procs returns the jobs in the order of completion
    dead, alive = psutil.wait_procs(procs_list,
                                    timeout=None,
                                    callback=utils.psutil_terminate_callback)
    print("Defect simulation completed successfully, see defect.log\n")

    if gen_new_ctrl:
        print("EM Input files generated successfully, see em.log\n")

    assert not alive, "Not all processes were fully terminated."

except KeyboardInterrupt:  # Catch if any SIGINT is received
    if gen_new_ctrl:
        utils.sigint_action(ctrl_em_sp, remove_dir=ctrl_dir_path)
    utils.sigint_action(defect_sim_sp)

#
print(f"Compressing the MTV file (with defect) to \'{MTV_GZIP_FILE}\'\n")
mtv_files = glob.glob(f'{data_repo_path}/Binary_mask_2u*')
if len(mtv_files) != 1:
    err_message = "Did not detect a unique MTV file for compressing, relaunch the run.\n"
    print(err_message)
    SimLog.critical(err_message)
    utils.safe_exit(errno.EEXIST, err_message)

# Option -f (--force): force overwrite of output file
# Option -c (--stdout): write on stdout, keep original files unchanged
sp.Popen(f"gzip -fc {mtv_files[0]} > {MTV_GZIP_FILE}",
         shell=True, cwd=data_repo_path)

print("Copying the EM input files from 'control' directory..\n")
copy_emsim_in_sp = sp.run(f"cp {ctrl_dir_path}/emsim_*.in {data_repo_path}",
                          shell=True, capture_output=True, text=True)
if copy_emsim_in_sp.returncode != 0:
    err_message = "Did not find the EM input files. em might have failed.\n"
    print(err_message)
    SimLog.critical(err_message)
    utils.safe_exit(errno.ENOENT, err_message)

# Launching MPI from the working (& control) directory
try:
    defect_mpi_sp = sp.Popen(f"bash {MPI_EM_SHELL_PIPE}",
                            shell=True, cwd=data_repo_path, env=runtime_env)
    defect_mpi_pid = defect_mpi_sp.pid
    procs_list = [psutil.Process(defect_mpi_pid)]
    print(f"> Launching EM simulation [PID: {defect_mpi_pid}] on MPI from {data_repo}..\n")

    if gen_new_ctrl:
        ctrl_mpi_sp = sp.Popen(f"bash {MPI_EM_SHELL_PIPE}",
                              shell=True, cwd=ctrl_dir_path, env=runtime_env)
        ctrl_mpi_pid = ctrl_mpi_sp.pid
        procs_list += [psutil.Process(ctrl_mpi_pid)]
        print(f"> Launching EM simulation [PID: {ctrl_mpi_pid}] on MPI from control directory..\n")

    # psutil.wait_procs returns the jobs in the order of completion
    dead, alive = psutil.wait_procs(procs_list,
                                    timeout=None,
                                    callback=utils.psutil_terminate_callback)

    assert not alive, "Not all processes were fully terminated."

except KeyboardInterrupt:
    if gen_new_ctrl:
        utils.sigint_action(ctrl_mpi_sp)
    utils.sigint_action(defect_mpi_sp)

# Cleaning up the run files
sp.run("rm *tcl *sh *in", shell=True, cwd=data_repo_path)

print("All tasks completed")
print("===================")
