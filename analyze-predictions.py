# @brief Analyse predicted data
# @author rohit
import sys
import argparse
from math import sqrt

def stats (metric, inputfilename, show_vals):
    mse = 0
    count = 0
    with open(inputfilename, "r") as inputfile:
        for line in inputfile.readlines():
            if line.startswith (metric):
                c = line.strip().split()
                pred_val = float(c[1])
                actual_val = float(c[2])
                error_val = actual_val - pred_val
                mse += (error_val * error_val)
                count += 1
                if show_vals:
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

parser = argparse.ArgumentParser("Prediction analysis")
parser.add_argument("--input", required=True)
parser.add_argument("--metric", required=True, help="name of metric, or list-all, or all")
parser.add_argument("--show-vals", action="store_true")
args = parser.parse_args()

if args.metric == "list-all":
    print (", ".join(get_metrics(args.input)))
elif args.metric == "all":
    for metric in get_metrics(args.input):
        stats (metric, args.input, args.show_vals)
else:
    stats (args.metric, args.input, args.show_vals)
        

#
def display_stats (error_seq):
    nreadings = len(error_seq[error_seq.keys()[0]])
    display_stats_upto(error_seq, nreadings/4*1)
    display_stats_upto(error_seq, nreadings/4*2)
    display_stats_upto(error_seq, nreadings/4*3)
    display_stats_upto(error_seq, nreadings/4*4)

def display_stats_upto(error_seq, nreadings):
    metrics = error_seq.keys()

    errors = dict()
    best_worst = dict()

    for reading_idx in range(0,nreadings):
        for metric in metrics:
            errors[metric] = error_seq[metric][reading_idx]

            
##            for (int reading_idx = 0; reading_idx < nreadings; ++reading_idx)
##            {
##                foreach (string metric in metrics) errors[metric] = error_seq[metric][reading_idx];
##                // best and worsts
##                var sorted = errors.OrderBy(a => Math.Abs(a.Value));
##                string best_metric = sorted.ElementAt(0).Key;
##                string worst_metric = metrics.Contains("MvAvg") ? sorted.ElementAt(metrics.Count() - 2).Key : sorted.ElementAt(metrics.Count() - 1).Key;
##                Tuple<int, double, int, double> best = best_worst_metric[best_metric];
##                Tuple<int, double, int, double> worst = best_worst_metric[worst_metric];
##                best_worst_metric[best_metric] = System.Tuple.Create(best.Item1 + 1, best.Item2 + Math.Abs(errors[best_metric]), best.Item3, best.Item4);
##                best_worst_metric[worst_metric] = System.Tuple.Create(worst.Item1, worst.Item2, worst.Item3 + 1, worst.Item4 + Math.Abs(errors[worst_metric]));
##
##            }
##            Console.WriteLine("Using {0} readings:", nreadings);
##            Console.WriteLine("== Best & Worst==");
##            Console.WriteLine("{0,20} {1,14} {2,15} {3,14} {4,15} {5,15}", "Metric", "Freq (Best)", "Abs-Err (Best)", "Freq (Worst)", "Abs-Err (Worst)", "Freq (Best-Worst)");
##            foreach (var el in best_worst_metric.OrderByDescending(a => a.Value.Item1))
##            {
##                Console.WriteLine("{0,20} {1,14} {2,15:F5} {3,14} {4,15:F5} {5,15}", el.Key,
##                    best_worst_metric[el.Key].Item1, best_worst_metric[el.Key].Item2 / best_worst_metric[el.Key].Item1,
##                    best_worst_metric[el.Key].Item3, best_worst_metric[el.Key].Item4 / best_worst_metric[el.Key].Item3,
##                    best_worst_metric[el.Key].Item1 - best_worst_metric[el.Key].Item3);
##            }
##            // R-statistics
##            Dictionary<string, double> sum_abs_error = new Dictionary<string, double>();
##            foreach (string metric in metrics)
##            {
##                sum_abs_error[metric] = error_seq[metric].Take(nreadings).Select(e => Math.Abs(e)).Sum();
##            }
##            double total_sum = sum_abs_error.Sum(a => a.Value);
##            Console.WriteLine("== R-score ==");
##            foreach (var el in sum_abs_error.OrderBy(a => a.Value))
##            {
##                Console.WriteLine("{0,20} {1:F5}", el.Key, el.Value / total_sum);
##            }
##        }
