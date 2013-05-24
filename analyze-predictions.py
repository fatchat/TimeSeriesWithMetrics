# @brief Analyse predicted data
# @author rohit
import sys
import argparse
from math import sqrt

parser = argparse.ArgumentParser("Prediction analysis")
parser.add_argument("--input", required=True)
parser.add_argument("--summary-file", help="output summary to text file")
parser.add_argument("--metric", default="all", help="name of metric, or list-all, or all")
parser.add_argument("--pred-step", default=1, type=int, help="number of steps ahead to predict (that step only)")
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
        return int(len(c) / (len(metrics) + 1))
    else:
        print ("cannot handle version %d, quitting." % versnum)
        sys.exit(1)

def get_actual_and_predicted(versnum, c, pred_step, npred, metric_idx, metrics):
    actual_val = float(c[pred_step])
    pred_val = float(c[npred + metric_idx + len(metrics) * pred_step])
    return [actual_val, pred_val]
        
def show_stats (metrics, metric, inputfilename, show_vals, pred_step, top_n, summary_file):
    mse = 0
    total = 0
    count = 0
    versnum = 0
    with open(inputfilename, "r") as inputfile:
        metric_idx = metrics.index(metric)
        header = inputfile.readline() # discard header
        if header.strip().split()[0] == "version":
            versnum = int(header.strip().split()[1])
            inputfile.readline() # discard next line (metrics)
        npred = 0
        if show_vals:
            print("%10s\t%8s\t%8s\t%8s\t%8s" % ("metric", "actual", "pred", "error", "error%"))
            print("=" * 80)
        for line in inputfile.readlines():
            c = line.strip().split()
            if npred==0:
                npred = get_npred(versnum, c, metrics)
                if pred_step >= npred:
                    raise IndexError("pred_step must be <= %d" % npred)
            [actual_val, pred_val] = get_actual_and_predicted(versnum, c, pred_step, npred, metric_idx, metrics)
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
        if summary_file not in [None, ""]:
            with open(summary_file, "a") as outputfile:
                outputfile.write("%s %d %f %f\n" % (metric, pred_step + 1, rmse, total))

# ########### start #############
metrics = get_metrics(args.input)
if args.metric == "list-all":
    print (", ".join(metrics))
elif args.metric == "all":
    for metric in metrics:
        show_stats (metrics, metric, args.input, args.show_vals, args.pred_step - 1, args.top_n, args.summary_file)
else:
    show_stats (metrics, args.metric, args.input, args.show_vals, args.pred_step - 1, args.top_n,args.summary_file)
