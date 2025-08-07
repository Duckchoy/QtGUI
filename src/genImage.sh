#!/bin/bash

#************************************************#
#             run.sh (bash v4.3.48)              #
#             Date: Sep-Nov, 2022                #
#                                                #
#  This file is copied over as 'run.sh' into     #
#  other directories where user specified env    #
#  variables are modified. The main job of this  #
#  script is to automate three tasks:            #
#          (1) EM sim *NF.tcl                    #
#          (2) EM sim *.in	                     #
#          (3) EM sim *image.tcl                 #
#  The final results are aerial intensities      #
#************************************************#

working_dir=$(basename $PWD)
update_freq=60	# frequency (in seconds) for posting updates from MPI run 

# ===================================================== #
#               1. Some useful functions                #
# ===================================================== #

# ---------------------------------------------------------------------- #
#                            1. remove()                                 #
#  This enables (inside `trap`) removing the jobs from the server        #
#  whenever a SIGINT (Ctrl+C) signals are received                       #
#  Inputs: None, Returns: 0 on success, otherwise 1 is returned          #
# ---------------------------------------------------------------------- #
remove () {
  echo; echo "[SIGINT Caught] Job IDs $JobID_x and $JobID_y will be removed from server.."
  <mpi> remove --target $pool "$JobID_x"
  <mpi> remove --target $pool "$JobID_y"
  rm -f *pre_exec_*
  #  kill -s SIGTERM $!   # handling kill [pid] type termination
  exit 130    # 130: User requested job termination (Ctrl+C evnt)
}

# ---------------------------------------------------------------------- #
#                           Parse__stdout()                              #
#  Pings server and captures a custom STDOUT from it. This is parsed     #
#  further to extract parameters to be used in loggings & computations   #
#  Input: Job ID; Returns: 'stdout_id' array and its members             #
# ---------------------------------------------------------------------- #
Parse__stdout() {
  local status= # status querry goes here
  local status_id=$status\"$1\"
  eval stdout_id=\$\($status_id\)
  IFS=',' read -r -a std_arr <<< "$stdout_id"

  SubmitTime=${std_arr[0]}
  PreExecExitStatus=${std_arr[1]}
  TimeInRunning=${std_arr[2]}
  ExitStatus=${std_arr[3]}
}

# ---------------------------------------------------------------------- #
#                             progress()                                 #
#  grep iteration counts from the log file of EM sim run. The last line  #
#  reports the current count (of total counts). Get a rounded percentage #
#  value of current count/total count.                                   #
#  Input: Name of the log file (string)                                  #
#  Returns: rounded progress percentage (int)                            #
# ---------------------------------------------------------------------- #
progress() {
  log_file="$1"
  iter_line=$( grep "Iteration  = " "$log_file" 2>/dev/null | tail -1 )
  # grep won't return any STDERR when log files have not been created
  # $iter_line is an empty variable when there is no log file or until
  # the iterations have begun. This is captured in the IF below.

  if [[ -n "$iter_line" ]]; then
    IFS=' ' read -r -a ifs_array <<< "$iter_line"
    curr_iter=${ifs_array[2]}
    all_iters=${ifs_array[4]}
    # getting rounded percentage progress is a bit convoluted in bash
    progress=$((200*$curr_iter/$all_iters % 2 + 100*$curr_iter/$all_iters))
  else
    # Progress is zero while the job is being submitted
    progress=0
  fi
}

# ===================================================== #
#               2. Launch Jobs on Server                #
# ===================================================== #

# 2.0: This block checks if any *pre_exec_* files exist before a  run is submitted
# Cause then user must be attempting to launch multiple sessions. For this reason  
# all *pre_exec_* files are deleted before any (zero or non-zero) exit modes
stat -t *pre_exec_* >/dev/null 2>&1
if [[ $? -eq 0 ]]; then         # `stat` returns 0 (1) if it can (not) find the file
	echo "[Run aborted] Only one set of jobs can be launched from the same directory. 
  Please wait for the current jobs to complete or create a new session."
  exit 132    # 128+4: Illegal instruction: user attempted more than one session
else
  # Remove any pre-existing em_*.log files which may interfere with the new runs
  rm -f -- em_*.log    # `-f` mode turns off any stderr if files do not exist
fi   

# 2.1: Launch MPI and get the job IDs corresponding to x & y input files
mpiq_x=$($Q --log-file em_x.log $EMsim em_*_x_1.in)
IFS=' ,' read -r -a get_id <<< "$mpiq_x"
JobID_x=${get_id[6]}

mpiq_y=$($Q --log-file em_y.log $EMsim em_*_y_1.in)
IFS=' ,' read -r -a get_id <<< "$mpiq_y"
JobID_y=${get_id[6]}

echo "Jobs submitted to $pool pool. Waiting for evaluation to start.."; echo

# 2.2: Catch any termination signals
trap remove SIGINT

# 2.3: Check if submission went fine.
# 2.3.1: Exit if there is any typo in submission command (job id is none)
if [[ "$JobID_x" -eq "not" ]]; then
  echo "Job submission failed! Please check for typos in PDS settings."; echo
  exit 127    # 127: Command not found, check for typos
fi

# 2.3.2: Exit if PreExecExitStatus in non-zero
Parsestdout "$JobID_x"

if [[ "$PreExecExitStatus" -eq 0 ]]
  then
    echo "JobID (X, Y) successfully generated [from ${working_dir} dir] at "${SubmitTime} ": ("${JobID_x}", "${JobID_y}")"; echo
  else
    echo "Something failed in job submission"
    exit 126  # 126: Command could not be executed, pre-execution script failed
fi

# Buffer time for jobs to be docked
sleep 20

# 2.4: Launch an infinite loop running until  job ends
# TODO: Future scope of improvements:
#   1. Remove repeated code-blocks (IF-FI)
#   2. Generalize this loop for handling multiple jobs
#   3. Parallelize this so each job is checked independently
Xflag=1
Yflag=1
while true; do
  # First two IF-FI blocks check whether the jobs corresponding to X & Y files 
  # have completed or not. They prevent any further status checking & logging once
  # their corresponding flags have been raised. 
  # The nested IF-FI inside them checks if $ExitStatus is finite. Until the job
  # completes on the  server, this remains an empty variable. This is used as
  # a (numeric) proxy for knowing whether the job has completed. In case something
  # fails on  server this $ExitStatus is also returned as an ExitCode.
  # The third IF-FI block reports the overall status of the jobs & helps break out
  # of the WHILE loop once both X & Y flags have been raised (all jobs complete).

  if [ $Xflag == "1" ]; then
    if [ "$ExitStatus_x" ] ; then
      echo; echo $(date +"%Y-%m-%d %r")": [X] Job $JobID_x Complete. Exiting with code "${ExitStatus_x}
      Xflag=0
    else
      Parsestdout "$JobID_x"
      ExitStatus_x=$ExitStatus
    fi
  fi 

  if [ $Yflag == "1" ]; then
    if [ "$ExitStatus_y" ] ; then
      echo; echo $(date +"%Y-%m-%d %r")": [Y] Job $JobID_y Complete. Exiting with code "${ExitStatus_y}
      Yflag=0
    else   
      Parsestdout "$JobID_y"
      ExitStatus_y=$ExitStatus
    fi 
  fi

  # Occasionally the above if-fi fail to catch ExitStatus and if the jobs undock then that empties out
  # ExitStatus, resetting  the flags to 1. The if condition below aims to prevent that.
    if ([ "$Xflag" == "0" ] && [ "$Yflag" == "0" ]) || ([ "$progress_x" == "100" ] && [ "$progress_y" == "100" ]) ; then
      echo; echo $(date +"%Y-%m-%d %r")": All jobs complete in ${working_dir} dir. See report in em.log"
    break 1
  else
    progress "em_x.log"
    progress_x=$progress
    progress "em_y.log"
    progress_y=$progress
    echo -ne $TimeInRunning": Jobs in progress... [X: ${JobID_x},Y: ${JobID_y}] = ["$progress_x"%,"$progress_y"%]    \r"
  fi

  # Pause the while loop in background; wait for the last PID ($!) to be completed
  sleep $update_freq &    
  wait $!
done

# ===================================================== #
#               3. EM sim on image.tcl                 #
# ===================================================== #

echo; echo "Generating aerial images.."
$EMsim image.tcl 2>/dev/null > image.log
echo $(date +"%Y-%m-%d %r")": Aerial Intensities generated successfully in ${working_dir}/AZ_0.0."; echo

# All Went Well
rm -f *pre_exec_*
exit 0    # 0: Success!
