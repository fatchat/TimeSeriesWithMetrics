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
parser.add_argument("--pred-step", required=True, help="number of steps ahead to predict (that step only, 1-based), or \"all\"")
parser.add_argument("--show-vals", action="store_true")
parser.add_argument("--top-n", type=int, metavar="N", default=0, help="process only the top N rows")
args = parser.parse_args()

def get_metrics (inputfilename):
    with open(inputfilename, "r") as inputfile:
        headers = inputfile.readline().strip().split()
        if headers[0] == "version":
            headers = inputfile.readline().strip().split()
        return headers[1:] # discard "actual" (which is always there)

def RaiseError(message):
    print (message)
    sys.exit(1)

# ============================================================================================================
class PredictionCalculator:
    def __init__(self, metrics):
        self.metrics = metrics
        self.versnum = 0
        self.npred = 0
        self.mse        = defaultdict(float)    # change this to defaultdict(defaultdict(float)) and key on step & metric TODO
        self.total      = defaultdict(float)    # one per step
        self.sq_total   = defaultdict(float)    # one per step
        self.mean       = defaultdict(float)    # one per step
        self.mean_of_sq = defaultdict(float)    # one per step
        self.std_dev    = defaultdict(float)    # one per step
        self.show_vals = False
        
    def get_npred (self, c):
        if self.versnum == 0:
            return int(len(c) / (len(self.metrics) + 1)) # no "actual" in metrics
        else:
            print ("cannot handle version %d, quitting." % self.versnum)
            sys.exit(1)

    def get_actual(self, entries, step):
        return float(entries[step])
            
    def get_predicted(self, entries, step, metric_idx):
        if self.versnum == 0:
            pred_val = float(entries[self.npred + metric_idx + len(self.metrics) * step])
        elif self.versnum == 1:
            pred_val = float(entries[step + self.npred * (1 + metric_idx)])
        else:
            RaiseError ("cannot handle version %d, quitting." % self.versnum)
        return pred_val
        
    def update_stats(self, entries, pred_step, metric_idx):
        pred_val = self.get_predicted(entries, pred_step, metric_idx)
        actual_val = self.get_actual(entries, pred_step)
        error_val = actual_val - pred_val
        self.mse[pred_step] += (error_val * error_val)
        self.total[pred_step] += actual_val
        self.sq_total[pred_step] += (actual_val * actual_val)
        if self.show_vals:
            error_pctg = error_val / actual_val * 100 if actual_val != 0 else 0
            print ("%10s\t%02.5f\t%02.5f\t%+02.5f\t%+03.2f" % (self.metrics[metric_idx], actual_val, pred_val, error_val, error_pctg))

    def calc_stats (self, count):
        for step in self.mse.keys():
            self.mse[step] /= (count-1) # unbiased estimator
            self.mse[step] = sqrt (self.mse[step])
            self.mean[step] = self.total[step] / count
            self.mean_of_sq[step] = self.sq_total[step] / count
            self.std_dev[step] = sqrt(self.mean_of_sq[step] - self.mean[step] * self.mean[step])        # beware of "catastrophic cancellation"

    def process_file (self, metric, inputfilename, pred_step, top_n, summary_file):
        count = 0
        with open(inputfilename, "r") as inputfile:
            metric_idx = self.metrics.index(metric)
            headers = inputfile.readline().strip().split()
            if headers[0] == "version":
                self.versnum = int(headers[1])
                self.npred = int(headers[3])
                if pred_step >= self.npred: RaiseError("pred-step must be less than %d" % (1 + self.npred))
                inputfile.readline() # discard next line (metrics)
            if self.show_vals:
                print("%10s\t%8s\t%8s\t%8s\t%8s" % ("metric", "actual", "pred", "error", "error%"))
                print("=" * 80)
            for line in inputfile.readlines():
                c = line.strip().split()
                if self.npred==0:
                    self.npred = self.get_npred(c)
                    if pred_step >= self.npred: RaiseError("pred-step must be less than %d" % (self.npred + 1))
                if pred_step == -1:
                    for step in range(0, self.npred):
                        self.update_stats(c, step, metric_idx)
                else:
                    self.update_stats(c, pred_step, metric_idx)
                count += 1
                if top_n > 0 and count == top_n:
                    break
            if count == 0: RaiseError("No data")
            if count == 1: RaiseError("Need more than 1 line of data")
            self.calc_stats(count)
            if self.show_vals:
                print ("=" * 80)
            for step in sorted (self.mse.keys()):
                #pass
                print ("RMSE for %10s, %d steps ahead, is %3.5f on a mean of %3.5f and a std. dev of %3.5f" % (metric, step + 1, self.mse[step], self.mean[step], self.std_dev[step]))
            if summary_file not in [None, ""]:
                with open(summary_file, "a") as outputfile:
                    for step in sorted (self.mse.keys()):
                        outputfile.write("%s %d %f %f %f\n" % (metric, step + 1, self.mse[step], self.mean[step], self.std_dev[step]))
        
        
# ########### start #############
if args.show_vals and args.pred_step == "all":
    print ("--show-vals and --pred-step all are mutually exclusive")
    sys.exit(1)
metrics = get_metrics(args.input)
if args.metric == "list-all":
    print (", ".join(metrics))
else:
    pred_calc = PredictionCalculator(metrics)
    pred_calc.show_vals = args.show_vals
    pred_step = 0 if args.pred_step == "all" else int(args.pred_step)
    if args.metric == "all":
        for metric in metrics:
            pred_calc.process_file (metric, args.input, pred_step - 1, args.top_n, args.summary_file)
    else:
        pred_calc.process_file (args.metric, args.input, pred_step - 1, args.top_n, args.summary_file)
