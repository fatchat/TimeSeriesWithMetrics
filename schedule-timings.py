# @brief Timings from a schedule log
# @author rohit
import os
import sys
import argparse
import datetime
import time
import logging

parser = argparse.ArgumentParser("Show run timings for a schedule")
parser.add_argument("--schedule-folder", required=True, help="name of folder holding batch schedule information")
parser.add_argument("--file")
parser.add_argument("--history", type=int)
args=parser.parse_args()

log_file = args.schedule_folder + "\\logfile.log"
#INFO:root:start:2013-05-25 16:12:24.115015:python C:\\TimeSeriesWithMetrics\\train-and-validate.py --input F:\\TextData\\ECG_data\\Column_1_Normalized\\S.1.txt --use-mvavg --use-dev --use-adjdiff --use-runningsum --output-dir f:\\ScheduledTraining\\ECG_1 --history 20 --predictions 10
#INFO:root:end:2013-05-25 16:16:40.054262:255.939247 seconds

with open(log_file, "r") as logfile:
    while True:
        start_line = logfile.readline().strip().split()
        end_line = logfile.readline().strip().split()
        if start_line ==[]: break
        #print (start_line)
        input_file = start_line[4].replace("\\" + "\\", "\\")
        if args.file != None and args.file != input_file:
            continue
        history = int(start_line[-3])
        if args.history != None and args.history != history:
            continue
        npreds = int(start_line[-1])
        time = float(end_line[1].split(':')[-1])
        print ("%20s %5d %5d %15.5f seconds" % (input_file, history, npreds, time))
        