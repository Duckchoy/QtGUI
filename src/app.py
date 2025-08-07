#!/usr/bin/python3.8

# ************************************************ #
#               app.py (Python v3.8)               #
#              Date: Nov-Dec, 2022                 #
#                                                  #
#  The main executable file that calls the GUI.    #
#  It contains all the action methods for it.      #
# ************************************************ #

"""
v2.2
- Bug Fixes with defect & main scripts
- Defect is also shown on the GDS viewer (with specified dimensions)
- A button to toggle GDS file
- Center of defect is available
- Previous bug about GDSWriter
- implement max_time (iteration control)
"""


from MainApp import MainUI
from PySide2 import QtWidgets, QtCore, QtGui
import subprocess as sp
import json
import configparser as cp
import signal
import shlex
import sys
import os
import psutil
import datetime
import utils


class GuiMain(QtWidgets.QMainWindow):
    """ A superclass of the GUI layout class (imported from QtDesigner).
    Contains all the action methods for forms and buttons.
    """
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.MainWindow = MainUI()
        self.MainWindow.setupUi(self)
        self.MainWindow.closeEvent = self.closeEvent    # For handling 'X' (close) app

        self.CONFIG_FILE = "config.ini"
        self.mainProc = None
        self.GDSfile = None
        self.is_config_valid = True     # Flag for checking valid input arguments
        self.dictJobs = dict()

    def activate_key_shortcut(self, key_sequence, callable):
        """ Map a key_sequence to an action callable
        """
        key_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(key_sequence), self)
        key_shortcut.activated.connect(callable)

    @staticmethod
    def kill_child_procs(pids: list, kill_signal=signal.SIGINT):
        """ Terminates all children & parent processes for all PIDs in the list.
        """
        if pids:
            parents = [psutil.Process(pid) for pid in pids]
            for parent in parents:
                # recursive=True: parent's descendants of all levels
                for child in parent.children(recursive=True):
                    os.kill(child.pid, kill_signal)
                os.kill(parent.pid, kill_signal)
                # Same as parent.kill() but it sends SIGKILL (it can't be trapped)
            print(f""
                  f"Terminated PID(s) {pids} ..\n")
        else:   # when list is empty
            pass

    def closeEvent(self, event):
        """ Overwriting the QtGui.closeEvent() to handle 'X' (close). Terminates all
            (if any) background processes and quits the application.
        """
        live_procs = self.find_live_procs()

        if live_procs:       # if there's any live process
            butQuit = QtWidgets.QMessageBox.question(
                        self.MainWindow.pushQuit, "Exit?",
                        f"Quit all {len(live_procs)} jobs and close the app?")
            if butQuit == QtWidgets.QMessageBox.Yes:
                self.kill_child_procs(live_procs)
                event.accept()
            else:
                event.ignore()
        else:
            print("--------------------------------------------------------")
            print("No active process found, quitting application. Good bye!\n")
            event.accept()

    def find_live_procs(self) -> list:
        """ Returns a list of PIDs that are still active (running). If an old PID has
            terminated or been removed by the OS (raise psutil.NoSuchProcess) they are
            deleted from the PID dictionary.
        """

        all_live_pids = list(self.dictJobs.keys())

        for pid in all_live_pids:
            try:
                proc_status = psutil.Process(pid).status()
            except psutil.NoSuchProcess:
                del self.dictJobs[pid]
            else:
                # SP launches a lot of zombie processes, trap them.
                if proc_status == psutil.STATUS_ZOMBIE:
                    print(f"PID {pid} is removed")
                    del self.dictJobs[pid]
                else:
                    print(f"PID {pid} is active \n")

        all_live_pids = list(self.dictJobs.keys())
        return all_live_pids

    def get_gds_file(self):
        """ Opens a dialog to read GDS files and sets the file name into lineGDS
        """
        gds_fullpath, _ = QtWidgets.QFileDialog.getOpenFileName(
            parent=self.MainWindow.pushGDS,
            caption='Upload file', dir='.', filter='*.gds'
        )

        if gds_fullpath:
            self.GDSfile = os.path.basename(gds_fullpath)
            self.MainWindow.lineGDS.setText(gds_fullpath)

    @staticmethod
    def view_gds_file():
        """ Launches the GDS file viewer (with the defect). Being a low priority function, any error
            encountered while launching is simply ignored. The code-block in the try statement
            is directly copied from main.py
        """
        try:
            curr_working_dir = os.getcwd()
            config_in_path = os.path.join(curr_working_dir, "config.ini")
            (_, mask_data, defect_info, _, _) = utils.unpack_config_dicts(config_in_path)

            gds_file_path = mask_data["gds_file"]
            layer_id = mask_data["layer_id"]
            defect_size = defect_info["size"]
            mask = utils.MaskFile(gds_file_path, layer_id)

            defect_loc_gds_units = [round(p/1000, 4) for p in defect_info["location"]]
            mask.get_dimensions()
            defect_coords = [round(sum(x), 4) for x in zip(defect_loc_gds_units, mask.center)]

            cell_man = utils.CellManager(mask.cell, layer_id)
            cell_man.view_gds(defect_location=defect_coords,
                              defect_radius=utils.wafer_to_gds_units(defect_size[0:-1], 0.001))

        except Exception:
            print("Either there is nothing to show or something is broken.")

    def quit_clicked(self):
        """ Action of QUIT button is to just quit all the jobs (if any)
        """
        live_procs = self.find_live_procs()

        if live_procs:  # if there's any live process
            butQuit = QtWidgets.QMessageBox.question(
                self.MainWindow.pushQuit, "Quit?",
                f"Terminate all {len(live_procs)} jobs?")
            if butQuit == QtWidgets.QMessageBox.Yes:
                self.kill_child_procs(live_procs)
        else:
            QtWidgets.QMessageBox.information(self.MainWindow.pushQuit, "Quit?", "There is no job running.")

    def run_clicked(self, inspect):
        """ When RUN is clicked, it sends signal to self.set_config_ini
            to correctly read the GUI form and write it to "config.ini".
            If it receives a self.is_config_valid=True then launches job.
            inspect=1 is the action of INSPECT button: Just do a validation
            check in main.py, do not run other server simulations.
        """
        ui.set_config_ini()     # write config.ini

        if self.is_config_valid:
            # main_process = "sleep 60"  # dummy process for testing

            abs_path_src_dir = os.path.abspath(os.path.dirname(__file__))
            main_file_path = os.path.join(abs_path_src_dir, "main.py")
            main_process = f"python {main_file_path} {inspect}"
            self.mainProc = sp.Popen(shlex.split(main_process))
            launch_time = datetime.datetime.now()
            self.dictJobs.update(
                {self.mainProc.pid:
                     [self.GDSfile,
                      launch_time.strftime("%d-%b-%Y %H:%M:%S")]}
            )
        else:
            print("Something went wrong with the configuration file. Please fix any issues or restart the app.\n")

    def set_config_ini(self):
        """ Called inside self.run_clicked. Creates a dictionary
            that gets writen as the configuration file.
        """

        config_dict = dict()

        def _empty_field_check(param_name, param_string):
            """ Prevents any missing (text type) fields in the GUI form
                to pass to the config.ini file. Raises 'critical' warning
                and does not let RUN proceed.
            """
            param_raw_value = param_name.text()
            if param_raw_value:
                param_value = str(param_raw_value)
                return param_value
            else:
                self.is_config_valid = False
                QtWidgets.QMessageBox.critical(
                    param_name,
                    "Missing Field",
                    f"{param_string} is empty! \nPlease fix before launching.")
                return

        config_dict.update({"TOOLS":
            {
                "EMsim": "<path-to-simulator>"
            }
        })

        config_dict.update({"MASK":
            {
                "gds_file": _empty_field_check(self.MainWindow.lineGDS, "GDS file"),
                "layer_id": [self.MainWindow.boxL.value(),
                             self.MainWindow.boxD.value()],
                "pos_tone": 1 if self.MainWindow.radioTP.isChecked() else 0,
                "mag_scale": 4      # TODO: Not linked to GUI for now
            }
        })

        config_dict.update({"DEFECT":
            {
                "seed": self.MainWindow.boxSeed.value(),
                "size": [self.MainWindow.boxDX.value(),
                         self.MainWindow.boxDY.value(),
                         self.MainWindow.boxDZ.value()],
                "location": [self.MainWindow.boxPosX.value(),
                             self.MainWindow.boxPosY.value()]
            }
        })

        config_dict.update({"COMPUTE":
            {
                "thermal_diffusivity": _empty_field_check(
                    self.MainWindow.boxAlpha, "Thermal Diffusivity"),
                "fdtd_grid_size": [self.MainWindow.boxGridX.value(),
                                   self.MainWindow.boxGridY.value(),
                                   self.MainWindow.boxGridZ.value()],
                "max_time": 100,     # TODO: Not linked to GUI for now
                "gen_control": '1' if self.MainWindow.checkGenCtrl.isChecked() else '0'
            }
        })

        config_dict.update({"PDS":
            {
                "pool": _empty_field_check(self.MainWindow.linePool, "Pool name"),
                "class": _empty_field_check(self.MainWindow.lineClass, "Class name"),
                "queue": _empty_field_check(self.MainWindow.lineQueue, "Queue name"),
                "slots": self.MainWindow.boxSlots.value(),
                "hosts": self.MainWindow.boxHosts.value(),
                "mail": "E" if self.MainWindow.checkEmail.isChecked() else "no"
            }
        })

        if self.is_config_valid:
            config = cp.ConfigParser()
            config.read_dict(config_dict)
            with open(self.CONFIG_FILE, 'w') as cfg:
                config.write(cfg)

    def import_clicked(self):
        """ QFileDialog is launched when IMPORT button is clicked.
            The dialog receives only INI files, which is passed further.
        """
        cnfg_file, ok_pressed = QtWidgets.QFileDialog.getOpenFileName(
            parent=self.MainWindow.pushImport,
            caption='Upload file', dir='.', filter='*.ini')

        if ok_pressed:       # for handling "cancel"
            ui.get_config_data(cnfg_file)

    def get_config_data(self, config_file):
        """ Read the configuration (INI) file received from IMPORT dialog.
            Check acceptable keys & corresponding data types and fill those
            to the GUI form.        
        """

        def _fill_valid_key_value(
                QObject, setType, parent_key, child_key, idx=None, check=None):
            """ Checks from 5 types of errors after reading the user provided config
                file -- KeyError (invalid key), TypeError (wrong data type),
                IndexError (when fewer data is provided), parsing errors from json & ini
            """

            # A default string to be printed with any error message
            err_string = f"Error found in \n Section name : '{parent_key}'\n " \
                         f"Variable name: '{child_key}'\n "

            try:
                self.GDSfile = os.path.basename(config["MASK"]["gds_file"])
                key_value = config[parent_key][child_key]

                if setType == "text":
                    # The case for vars: gds_file, thermal_diffusivity, pool, class, queue
                    QObject.setText(
                        QtCore.QCoreApplication.translate("RBDS", key_value, None))
                elif setType == "value":
                    # The case of vars: layer_id, fdtd_grid_size, size, seed, slots, hosts
                    key_value = json.loads(key_value)   # jsonify to correctly handle format
                    key_value = key_value if idx is None else key_value[idx]
                    QObject.setValue(key_value)
                elif setType == "check":
                    QObject.setChecked(key_value == str(check))

            except KeyError:
                self.is_config_valid = False
                QtWidgets.QMessageBox.information(
                    self.MainWindow.pushImport, "Missing key",
                    "Typo or missing keys in INI file:\n\n " + err_string
                )
            except IndexError:
                self.is_config_valid = False
                QtWidgets.QMessageBox.information(
                    self.MainWindow.pushImport, "Inadequate Data",
                    f"Position {idx+1} in the following key is missing.\n\n " + err_string
                )
            except TypeError:
                self.is_config_valid = False
                QtWidgets.QMessageBox.information(
                    self.MainWindow.pushImport, "Invalid DataType",
                    f"Data format is incorrect, use numbers or strings (no quotes)\n\n" + err_string
                )
            except json.decoder.JSONDecodeError as js_err:
                self.is_config_valid = False
                QtWidgets.QMessageBox.information(
                    self.MainWindow.pushImport, "Invalid Data",
                    f"{js_err.msg} at line {js_err.lineno}, column {js_err.colno} \n\n" + err_string
                )

            else:
                self.is_config_valid = True

        config_file_basename = os.path.basename(config_file)
        try:
            config = cp.ConfigParser()
            config.read(config_file)
        except cp.Error as cp_err:
            self.is_config_valid = False
            QtWidgets.QMessageBox.information(
                self.MainWindow.pushImport, "Broken INI file",
                f"{cp_err.__class__.__name__} in '{config_file_basename}':\n"
                f"{cp_err.message}"
            )
        else:
            # mask
            _fill_valid_key_value(self.MainWindow.lineGDS, "text", "MASK", "gds_file")
            _fill_valid_key_value(self.MainWindow.boxL, "value", "MASK", "layer_id", 0)
            _fill_valid_key_value(self.MainWindow.boxD, "value", "MASK", "layer_id", 1)
            _fill_valid_key_value(self.MainWindow.radioTP, "check", "MASK", "pos_tone", check='1')
            _fill_valid_key_value(self.MainWindow.radioTN, "check", "MASK", "pos_tone", check='0')
            # compute
            _fill_valid_key_value(self.MainWindow.boxAlpha, "text", "COMPUTE", "thermal_diffusivity")
            _fill_valid_key_value(self.MainWindow.boxGridX, "value", "COMPUTE", "fdtd_grid_size", 0)
            _fill_valid_key_value(self.MainWindow.boxGridY, "value", "COMPUTE", "fdtd_grid_size", 1)
            _fill_valid_key_value(self.MainWindow.boxGridZ, "value", "COMPUTE", "fdtd_grid_size", 2)
            _fill_valid_key_value(self.MainWindow.checkGenCtrl, "check", "COMPUTE", "gen_control", check='1')
            # defect
            _fill_valid_key_value(self.MainWindow.boxSeed, "value", "DEFECT", "seed")
            _fill_valid_key_value(self.MainWindow.boxDX, "value", "DEFECT", "size", 0)
            _fill_valid_key_value(self.MainWindow.boxDY, "value", "DEFECT", "size", 1)
            _fill_valid_key_value(self.MainWindow.boxDZ, "value", "DEFECT", "size", 2)
            _fill_valid_key_value(self.MainWindow.boxPosX, "value", "DEFECT", "location", 0)
            _fill_valid_key_value(self.MainWindow.boxPosY, "value", "DEFECT", "location", 1)
            # PDS
            _fill_valid_key_value(self.MainWindow.linePool, "text", "PDS", "pool")
            _fill_valid_key_value(self.MainWindow.lineClass, "text", "PDS", "class")
            _fill_valid_key_value(self.MainWindow.lineQueue, "text", "PDS", "queue")
            _fill_valid_key_value(self.MainWindow.boxSlots, "value", "PDS", "slots")
            _fill_valid_key_value(self.MainWindow.boxSlots, "value", "PDS", "hosts")
            _fill_valid_key_value(self.MainWindow.checkEmail, "check", "PDS", "mail", check="E")

    def abort_clicked(self):
        """ Launches a QInputDialog that allows the user to selectively kill jobs
        """

        class AbortSelectPID(QtWidgets.QDialog):
            def __init__(self):
                super(AbortSelectPID, self).__init__()
                layout = QtWidgets.QVBoxLayout(self)
                self.setLayout(layout)
                self.setMinimumWidth(500)

                self.selected_pid = None

            def JobsDialog(self, jobs_list):
                """ QInputDialog displays job details (received as a list of strings).
                    Then parses the selected item and stores its PID
                """
                item, ok_pressed = QtWidgets.QInputDialog.getItem(
                    self, "Abort PID", "Which job do you want to terminate?", jobs_list, 0, False)

                if ok_pressed and item:
                    item_pid = item.split(":")[0]
                    self.selected_pid = item_pid.split(" ")[1]

        live_procs = self.find_live_procs()
        if live_procs:
            format_jobs_list = list()
            for pid in live_procs:
                format_job_str = f"PID {pid}: Launched at {self.dictJobs[pid][1]} ({self.dictJobs[pid][0]})"
                format_jobs_list += [format_job_str]
            dialogPID = AbortSelectPID()
            dialogPID.JobsDialog(format_jobs_list)
            if dialogPID.selected_pid is not None:      # To handle "cancel" of QInputDialog
                self.kill_child_procs([int(dialogPID.selected_pid)])
        else:   # No job running
            QtWidgets.QMessageBox.information(
                self.MainWindow.pushAbort, "Abort?", "There is no job running.")


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    ui = GuiMain()

    ui.MainWindow.pushGDS.clicked.connect(ui.get_gds_file)
    ui.activate_key_shortcut('Ctrl+O', ui.get_gds_file)

    ui.MainWindow.viewGDS.clicked.connect(ui.view_gds_file)
    ui.activate_key_shortcut('Ctrl+G', ui.view_gds_file)

    ui.MainWindow.pushImport.clicked.connect(ui.import_clicked)
    ui.activate_key_shortcut('Ctrl+I', ui.import_clicked)

    ui.MainWindow.pushInspect.clicked.connect(lambda: ui.run_clicked(inspect=1))
    ui.activate_key_shortcut('Ctrl+N', lambda: ui.run_clicked(inspect=1))

    ui.MainWindow.pushRun.clicked.connect(lambda: ui.run_clicked(inspect=0))
    ui.activate_key_shortcut('Ctrl+R', lambda: ui.run_clicked(inspect=0))

    ui.MainWindow.pushAbort.clicked.connect(ui.abort_clicked)
    ui.activate_key_shortcut('Ctrl+K', ui.abort_clicked)

    ui.MainWindow.pushQuit.clicked.connect(ui.quit_clicked)
    ui.activate_key_shortcut('Ctrl+Q', ui.quit_clicked)

    ui.show()
    ret = app.exec_()
    sys.exit(ret)
