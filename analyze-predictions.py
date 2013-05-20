# @brief Analyse predicted data
# @author rohit
import sys
import argparse
from math import sqrt
parser = argparse.ArgumentParser("Prediction analysis")
parser.add_argument("--input", required=True)
parser.add_argument("--metric", required=True, help="name of metric, or list-all, or all")
parser.add_argument("--show-vals", action="store_true")
args = parser.parse_args()

def stats (metric, inputfilename, show_vals):
    mse = 0
    count = 0
    with open(inputfilename, "r") as inputfile:
        for line in inputfile.readlines():
            if line.startswith (metric):
                c = line.strip().split()
                error_val = float(c[2])
                mse += (error_val * error_val)
                count += 1
                if show_vals:
                    pred_val = float(c[1])
                    actual_val = pred_val + error_val
                    error_pctg = error_val / actual_val * 100
                    print ("%10s\t%02.5f\t%02.5f\t%+02.5f\t%+03.2f" % (metric, actual_val, pred_val, error_val, error_pctg))
              
        mse /= count
        rmse = sqrt (mse)
        print ("RMSE for %s is %f" % (metric, rmse))

def get_metrics (inputfilename):
    with open(inputfilename, "r") as inputfile:
        names = dict()
        for line in inputfile.readlines():
            c = line.strip().split()[0]
            names[c] = 1
        return names.keys()

if args.metric == "list-all":
    print (", ".join(get_metrics(args.input)))
elif args.metric == "all":
    for metric in get_metrics(args.input):
        stats (metric, args.input, args.show_vals)
else:
    stats (args.metric, args.input, args.show_vals)
        
