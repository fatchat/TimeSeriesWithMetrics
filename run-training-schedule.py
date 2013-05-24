# @brief Run/ resume from a schedule file for running train-and-validate on multiple data sets
# @author rohit
import os
import sys
import argparse
import datetime
import time
import logging

parser = argparse.ArgumentParser("Run/resume from a schedule file for running train-and-validate")
parser.add_argument("--schedule-folder", required=True, help="name of folder holding batch schedule information")
parser.add_argument("--stop-index", type=int, default=-1)
args=parser.parse_args()

schedule_file = args.schedule_folder + "\\schedule.txt"
progress_file = args.schedule_folder + "\\progress.txt"
log_file = args.schedule_folder + "\\logfile.log"
stop_file = args.schedule_folder + "\\stop.txt"

logging.basicConfig(filename=log_file,level=logging.INFO)
print ("logging to %s" % log_file)

last_run = -1
if os.path.exists(progress_file):
    with open(progress_file, "r") as progress:
        lines = progress.readlines()
        if len(lines) > 0:
            last_line = lines[-1]
            c = last_line.split()
            last_run = int(c[0])
            print ("last sched_num was %d" % last_run)
    
with open(schedule_file, "r") as schedule:
    for line in schedule.readlines():
        if line.startswith("#") or line == "": continue
        line = line.strip()
        spc_idx = line.find(" ")
        sched_num = int(line[:spc_idx])
        if (sched_num > last_run and (args.stop_index == -1 or args.stop_index >= sched_num)):
            cmd = line[1+spc_idx:]
            cmd = cmd.replace("\\", "\\" + "\\")
            # start time
            start_time = time.time()
            time_start_str = datetime.datetime.now()
            print ("%s sched_num=%d" % (time_start_str, sched_num))
            logging.info("start:%s:%s" % (time_start_str, cmd))
            os.system(cmd)
            # end time
            end_time = time.time()
            time_end_str = datetime.datetime.now()
            logging.info("end:%s:%s" % (time_end_str, "%f seconds" % (end_time - start_time)))
            # record progress
            with open(progress_file, "a") as progress:
                progress.write("%d\n" % sched_num)
            # stop check
            if os.path.exists(stop_file):
                print("encountered stop file %s, stopping." % stop_file)
                break
