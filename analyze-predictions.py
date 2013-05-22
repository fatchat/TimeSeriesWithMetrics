# @brief Analyse predicted data
# @author rohit
import sys
import argparse
from math import sqrt

def show_stats (metrics, metric, inputfilename, show_vals, pred_step, top_n):
    mse = 0
    total = 0
    count = 0
    with open(inputfilename, "r") as inputfile:
        metric_idx = metrics.index(metric)
        inputfile.readline() # discard header
        npred = 0
        if show_vals:
            print("%10s\t%8s\t%8s\t%8s\t%8s" % ("metric", "actual", "pred", "error", "error%"))
            print ("=" * 80)
        for line in inputfile.readlines():
            c = line.strip().split()
            if npred==0:
                npred = int(len(c) / (len(metrics) + 1))
                #print ("len(c)=%d len(metrics)=%d npred=%d" % (len(c), len(metrics), npred))
                if pred_step >= npred:
                    raise IndexError("pred_step must be <= %d" % npred)
            actual_val = float(c[pred_step])
            pred_val = float(c[npred + metric_idx + len(metrics) * pred_step])
            error_val = actual_val - pred_val
            mse += (error_val * error_val)
            count += 1
            total += actual_val
            if show_vals:
                error_pctg = error_val / actual_val * 100 if actual_val != 0 else 0
                print ("%10s\t%02.5f\t%02.5f\t%+02.5f\t%+03.2f" % (metric, actual_val, pred_val, error_val, error_pctg))
            if top_n > 0 and count == top_n:
                break
        if count == 0:
            print ("no data")
            return
        mse /= count
        total = abs(total/count)
        rmse = sqrt (mse)
        if show_vals:
            print ("=" * 80)
        print ("RMSE for %10s, %d steps ahead, is %3.5f on a mean of %5.5f" % (metric, pred_step + 1, rmse, total))

def get_metrics (inputfilename):
    with open(inputfilename, "r") as inputfile:
        header = inputfile.readline().strip()
        return header.split()[1:] # discard "actual" (which is always there)

parser = argparse.ArgumentParser("Prediction analysis")
parser.add_argument("--input", required=True)
parser.add_argument("--metric", required=True, help="name of metric, or list-all, or all")
parser.add_argument("--pred-step", default=1, type=int, help="number of steps ahead to predict (that step only)")
parser.add_argument("--show-vals", action="store_true")
parser.add_argument("--top-n", type=int, metavar="N", default=0, help="process only the top N rows")
args = parser.parse_args()

metrics = get_metrics(args.input)
if args.metric == "list-all":
    print (", ".join(metrics))
elif args.metric == "all":
    for metric in metrics:
        show_stats (metrics, metric, args.input, args.show_vals, args.pred_step - 1, args.top_n)
else:
    show_stats (metrics, args.metric, args.input, args.show_vals, args.pred_step - 1, args.top_n)
