# @brief Create a schedule file for running train-and-validate on multiple data sets
# @author rohit
import os
import sys
import argparse

parser = argparse.ArgumentParser("Create a schedule file for running train-and-validate")
parser.add_argument("--schedule-folder", required=True, help="name of folder holding batch schedule information")
parser.add_argument("--input-file-list", required=True, help="file containing list of input files")
parser.add_argument("--history-start", type=int, required=True, help="start of history range")
parser.add_argument("--history-end", type=int, required=True, help="end of history range")
parser.add_argument("--npreds-start", type=int, required=True, help="start of npreds range")
parser.add_argument("--npreds-end", type=int, required=True, help="end of npreds range")
args=parser.parse_args()

schedule_file = args.schedule_folder + "\\schedule.txt"
with open (schedule_file, "w") as schedulefile:
    with open(args.input_file_list, "r") as inputfilelist:
        sched_num = 0
        for inputfilename in inputfilelist.readlines():
            inputfilename = inputfilename.strip()
            if not inputfilename.startswith("#"):
                #inputfilename = inputfilename.replace("\\", "\\" + "\\")
                if os.path.exists(inputfilename):
                    for hist in range (args.history_start, args.history_end):
                        for pred in range(args.npreds_start, args.npreds_end):
                            cmd = "python C:\\TimeSeriesWithMetrics\\train-and-validate.py --input %s --use-mvavg --use-dev --use-adjdiff --use-runningsum --output-dir %s --history %d --predictions %d\n" % (inputfilename, args.schedule_folder, hist, pred)
                            schedulefile.write("%d %s" % (sched_num, cmd))
                            sched_num += 1
                else:
                    print ("cannot find file %s, continuing" % inputfilename)
