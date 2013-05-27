# @brief Analyse predicted data
# @author rohit
import sys
import argparse
from math import sqrt
from collections import defaultdict

parser = argparse.ArgumentParser("Prediction analysis")
parser.add_argument("--input", required=True)
parser.add_argument("--summary-file", help="append summary to file")
parser.add_argument("--metric", default="all", help="name of metric, or list-all, or all")
parser.add_argument("--pred-step", help="number of steps ahead to predict (that step only, 1-based), or \"all\"")
parser.add_argument("--show-vals", action="store_true")
parser.add_argument("--top-n", type=int, metavar="N", default=0, help="process only the top N rows")
args = parser.parse_args()

def get_metrics (inputfilename):
    with open(inputfilename, "r") as inputfile:
        headers = inputfile.readline().strip().split()
        if headers[0] == "version":
            headers = inputfile.readline().strip().split()
        return headers[1:] # discard "actual" (which is always there)

def get_npred (versnum, c, metrics):
    if versnum == 0:
        #print ("len(c)=%d len(metrics)=%d npred=%d" % (len(c), len(metrics), npred))
        return int(len(c) / (len(metrics) + 1)) # no "actual" in metrics
    else:
        print ("cannot handle version %d, quitting." % versnum)
        sys.exit(1)

def get_actual_and_predicted(versnum, entries, pred_step, npred, metric_idx, metrics):
    if versnum == 0:
        actual_val = float(entries[pred_step])
        pred_val = float(entries[npred + metric_idx + len(metrics) * pred_step])
        return [actual_val, pred_val]
    elif versnum == 1:
        actual_val = float(entries[pred_step])
        #print (entries[pred_step + npred * (1 + metric_idx)])
        pred_val = float(entries[pred_step + npred * (1 + metric_idx)])
        return [actual_val, pred_val]
    else:
        print ("cannot handle version %d, quitting." % versnum)
        sys.exit(1)
        
def show_stats (metrics, metric, inputfilename, show_vals, pred_step, top_n, summary_file):
    mse = defaultdict(float)
    total = 0
    count = 0
    versnum = 0
    npred = 0
    sq_total = 0
    with open(inputfilename, "r") as inputfile:
        metric_idx = metrics.index(metric)
        headers = inputfile.readline().strip().split()
        if headers[0] == "version":
            versnum = int(headers[1])
            npred = int(headers[3])
            inputfile.readline() # discard next line (metrics)
        if show_vals:
            print("%10s\t%8s\t%8s\t%8s\t%8s" % ("metric", "actual", "pred", "error", "error%"))
            print("=" * 80)
        for line in inputfile.readlines():
            c = line.strip().split()
            if npred==0: npred = get_npred(versnum, c, metrics)
            if pred_step >= npred:
                return False
            #print (c)
            if pred_step == -1:
                for step in range(0, npred):
                    [actual_val, pred_val] = get_actual_and_predicted(versnum, c, step, npred, metric_idx, metrics)
                    error_val = actual_val - pred_val
                    mse[step] += (error_val * error_val)
            else:
                [actual_val, pred_val] = get_actual_and_predicted(versnum, c, pred_step, npred, metric_idx, metrics)
                error_val = actual_val - pred_val
                mse[pred_step] += (error_val * error_val)
                if show_vals:
                    error_pctg = error_val / actual_val * 100 if actual_val != 0 else 0
                    print ("%10s\t%02.5f\t%02.5f\t%+02.5f\t%+03.2f" % (metric, actual_val, pred_val, error_val, error_pctg))
            count += 1
            total += actual_val
            sq_total += (actual_val * actual_val)
            if top_n > 0 and count == top_n:
                break
        if count == 0:
            print ("no data")
            return True
        for step in mse.keys():
            mse[step] /= count
            mse[step] = sqrt (mse[step])
        mean = abs(total/count)
        mean_of_sq = sq_total / count
        std_dev = sqrt(mean_of_sq - mean * mean)
        if show_vals:
            print ("=" * 80)
        for step in sorted (mse.keys()):
            pass
            #print ("RMSE for %10s, %d steps ahead, is %3.5f on a std. dev of %3.5f" % (metric, step + 1, mse[step], std_dev))
        if summary_file not in [None, ""]:
            with open(summary_file, "a") as outputfile:
                for step in sorted (mse.keys()):
                    outputfile.write("%s %d %f %f %f\n" % (metric, step + 1, mse[step], mean, std_dev))
        return True
        
# ########### start #############
if args.show_vals and args.pred_step == "all":
    print ("--show-vals and --pred-step all are mutually exclusive")
    sys.exit(1)
metrics = get_metrics(args.input)
if args.metric == "list-all":
    print (", ".join(metrics))
elif args.metric == "all":
    for metric in metrics:
        if args.pred_step == "all":
            show_stats (metrics, metric, args.input, args.show_vals, -1, args.top_n, args.summary_file)
        else:
            show_stats (metrics, metric, args.input, args.show_vals, int(args.pred_step) - 1, args.top_n, args.summary_file)
else:
    if args.pred_step == "all":
        show_stats (metrics, args.metric, args.input, args.show_vals, -1, args.top_n, args.summary_file)
    else:
        show_stats (metrics, args.metric, args.input, args.show_vals, int(args.pred_step) - 1, args.top_n, args.summary_file)
