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
parser.add_argument("--redo-summary", action="store_true")
parser.add_argument("--history", type=int)
parser.add_argument("--npreds", type=int)
parser.add_argument("--multi-line-rmse", action="store_true", help="multi-line output for RMSE")
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
        return None
    folder_info = dict()
    folder_info['log'] = logfile
    with open(logfile, "r") as inputfile:
        start_line= inputfile.readline()
        metrics_line = inputfile.readline()
        if metrics_line.startswith("INFO:root:metrics:"):
            split_line = inputfile.readline()
        else:
            split_line = metrics_line
            metrics_line = None

        npreds = int(get_value(start_line, "predictions="))
        history = int(get_value(start_line, "history="))
        if args.npreds != None and args.npreds != npreds: return None
        if args.history != None and args.history != history: return None
        folder_info['predictions'] = npreds
        folder_info['history'] = history
        folder_info['input-file'] = get_value(split_line, "--input ")
        if metrics_line != None:
            for metric_data in metrics_line[metrics_line.find(" "):].split():
                (metric, true_false) = metric_data.split('=')
                folder_info[metric] = true_false

    rmse_info = defaultdict(dict)
    summary_file = folder + "\\Summary.txt"
    predictions_file = folder + "\\PredictedData.txt"
    if args.redo_summary and os.path.exists(summary_file):
        os.unlink(summary_file)
    if args.redo_summary or not os.path.exists(summary_file):
        cmd = "python C:\\TimeSeriesWithMetrics\\analyze-predictions.py --input %s --summary-file %s --pred-step all" % (predictions_file, summary_file)
        os.system(cmd)        
    if os.path.exists(summary_file):
        inputfile = open(summary_file, "r")
        mean = 0
        stddev = 0
        for line in inputfile.readlines():
            components = line.strip().split()
            metric = components[0]
            pred_step = components[1]
            rmse = components[2]
            o_mean = components[3]
            if len(components) > 4:
                o_stddev = components[4]
            else:
                o_stddev = 0
            rmse_info[int(pred_step)][metric] = float(rmse)
            if mean == 0: mean = float(o_mean)
            if stddev == 0: stddev = float(o_stddev)
        folder_info['mean'] = mean
        if stddev > 0: folder_info['stddev'] = stddev

    return (folder_info, rmse_info)

def print_multi_line_rmse(rmse_info):
    # create the header containing metric names
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

def print_folder_info(folder_info):
    for key in sorted(folder_info.keys()):
        print ("%s=%s " % (str(key), str(folder_info[key])))
            
# ###### start ######
if args.input != None:
    info = get_folder_info (args.input)
    if info != None:
        if args.multi_line_rmse:
            print_multi_line_rmse(info[1])
        else:
            print_folder_info(info[0])
elif args.parent != None:
    for folder in os.listdir(args.parent):
        info = get_folder_info(args.parent + "\\" + folder)
        if info != None:
            if args.multi_line_rmse:
                print_multi_line_rmse(info[1])
            else:
                print_folder_info(info[0])
else:
    print ("--input or --parent is required")
    parser.print_help()
    
