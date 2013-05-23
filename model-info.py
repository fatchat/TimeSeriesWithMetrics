# @brief Show information on the training model
# @author rohit
import os
import sys
import argparse
import re
from collections import defaultdict

parser = argparse.ArgumentParser("show model info")
parser.add_argument("--input", help="input folder")
parser.add_argument("--parent", help="parent folder")
parser.add_argument("--multi-line-rmse", action="store_true", help="multi-line output for RMSE (single file input only)")
args = parser.parse_args()

def get_value(line, key):
    start_index = line.find(key) + len(key)
    end_index = line.find(" ", start_index)
    return line[start_index:end_index]

def get_folder_info (folder):
    logfile = folder + "\\LOG-train-and-validate.log"
    if not os.path.exists(logfile):
        logfile = folder + "\\train-and-validate.log"
    if not os.path.exists(logfile):
        return ""
    output_line = "log=%s " % logfile
    with open(logfile, "r") as inputfile:
        start_line= inputfile.readline()
        metrics_line = inputfile.readline()
        if metrics_line.startswith("INFO:root:metrics:"):
            split_line = inputfile.readline()
        else:
            split_line = metrics_line
            metrics_line = ""

        npreds = int(get_value(start_line, "predictions="))
        for key in ["history", "predictions"]: # "output-dir", 
            output_line += "%s=%s " % (key, get_value(start_line, key+"="))
        output_line += "input-file=%s " % get_value(split_line, "--input ")
        if metrics_line != "":
            output_line += metrics_line[metrics_line.find(" "):].strip() + " "

    summary_file = folder + "\\Summary.txt"
    if os.path.exists(summary_file):
        inputfile = open(summary_file, "r")
        mean = 0
        for line in inputfile.readlines():
            [metric, pred_step, rmse, total] = line.strip().split()
            output_line += "RMSE-%s-%s=%s " % (metric, pred_step, rmse)
            if mean == 0: mean = float(total)
        output_line += "mean=%f " % mean

    return output_line

def print_multi_line_rmse(info):
    parts = info.split(' ')
    rmse_info = defaultdict(dict)
    regex = re.compile("RMSE-([^-]+)-([^=]+)=([^ ]+)")
    for part in parts:
        if part.startswith("RMSE-"):
            # RMSE-<metric>-<step>=<value>
            groups = regex.match(part).groups()
            metric = groups[0]
            step = groups[1]
            value = groups[2]
            rmse_info[step][metric] = value
    # create the header contiaining metric names
    arbit_step = list(rmse_info)[0]
    format_str = "%8s\t" * len(rmse_info[arbit_step].keys())
    print ("\t" + format_str % tuple(sorted(rmse_info[arbit_step].keys())))
    # iterate over steps
    format_str = "%+3.5f\t" * len(rmse_info[arbit_step].keys())
    for step in sorted(rmse_info.keys()):
        line="%s\t" % step
        for metric in sorted(rmse_info[step].keys()):
            line += "%+1.5f\t" % float(rmse_info[step][metric])
        print (line)


            
# ###### start ######
if args.input != None:
    info = get_folder_info (args.input)
    if info != "":
        if args.multi_line_rmse:
            print_multi_line_rmse(info)
        else:
            print (info)
elif args.parent != None:
    for folder in os.listdir(args.parent):
        info = get_folder_info(args.parent + "\\" + folder)
        if info != "": print (info)
else:
    print ("--input or --parent is required")
    
