# @brief Analyse predicted data
# @author rohit
import sys
import argparse
from math import sqrt
from collections import defaultdict
from predfilereader import PredFileReader

parser = argparse.ArgumentParser("Prediction analysis")
parser.add_argument("--input", required=True)
parser.add_argument("--summary-file")
parser.add_argument("--metrics", help="names of metrics")
parser.add_argument("--pred-step", type=int, help="0-based index")
parser.add_argument("--debug", action="store_true")
args = parser.parse_args()

# ==========================================================================================================        
class SingleStat:
    def __init__(self):
        self.total=0.0
        self.count=0
        self.sq_total=0.0

    def update(self, value):
        self.total      += value
        self.sq_total   += value*value
        self.count      += 1
        
    def calc(self):
        self.mean       = self.total / self.count
        self.mean_of_sq = self.sq_total / self.count
        self.variance   = self.mean_of_sq - self.mean*self.mean
        self.std_dev    = sqrt(self.variance)
        
# ==========================================================================================================        
class ErrorStatsTracker:
    def __init__ (self,name):
        self.name = name
        self.statdict = defaultdict(SingleStat)  # one per step
        
    def update(self, actual, predicted, step, name):
        if name == self.name: self.statdict[step].update(actual - predicted)

# ==========================================================================================================        
def get_step_stats(statstracker, step, calc=True):
    if calc: statstracker.statdict[step].calc()
    outstr = "%s %d %f %f %f" % (statstracker.name, step, sqrt(statstracker.statdict[step].mean_of_sq),     \
                                statstracker.statdict[step].mean, statstracker.statdict[step].std_dev)
    return outstr
        
def show_all(statstracker):
    for step in sorted(statstracker.statdict.keys()): print(get_step_stats(statstracker, step))
        
# ==========================================================================================================        
class PredictionChecker:
    def __init__(self, inputfilename):
        self.predfilereader = PredFileReader (inputfilename)
        self.actualtracker = ErrorStatsTracker("actual")
        self.errortrackers = []
        #self.verbose = False
        
    def process_input_line(self, values):
        #outstr=""
        for step in range (0, self.predfilereader.npred):
            actual = self.predfilereader.get_actual (values, step)
            #if self.verbose: outstr += "%d\t%f" % (step, actual)
            self.actualtracker.update(actual, predicted=0, step=step, name="actual")
            for metric_idx in range(1, len(self.predfilereader.metrics)):
                predicted = self.predfilereader.get_predicted (values, step, metric_idx - 1)
                #if self.verbose: outstr += "\t%f" % predicted
                metric = self.predfilereader.metrics[metric_idx]
                for errtracker in self.errortrackers:
                    errtracker.update(actual, predicted, step, metric)
            #if self.verbose: outstr += "\n"
        #if self.verbose: print (outstr)
        
# ==========================================================================================================        
checker = PredictionChecker(inputfilename=args.input)
#checker.verbose = args.debug
if args.metrics not in [None, "all"]:
    for metric in args.metrics.split():
        checker.errortrackers.append(ErrorStatsTracker(metric))

# process input file
while True:
    entries = checker.predfilereader.get_next_line()
    if args.metrics == "all":
        for metric in checker.predfilereader.metrics:
            checker.errortrackers.append(ErrorStatsTracker(metric))
        args.metrics = None
    if len(entries) == 0: break
    checker.process_input_line(entries)

# send summary to file
if args.summary_file != None:
    with open(args.summary_file, "w") as outputfile:
        # print actual
        for step in sorted(checker.actualtracker.statdict.keys()): 
            actual_line = get_step_stats(checker.actualtracker, step, calc=False)
            outputfile.write("%s\n" % actual_line)
        for errtracker in checker.errortrackers:
            for step in sorted (errtracker.statdict.keys()):
                error_line = get_step_stats(errtracker, step, calc=False)
                outputfile.write ("%s\n" % error_line)
else:                
# show some stats
    print ("metric step rmse mean stddev")
    if args.pred_step == None:
        show_all(checker.actualtracker)
        for errtracker in checker.errortrackers: show_all(errtracker)
    else:
        if args.pred_step >= 0 and args.pred_step < checker.predfilereader.npred:
            print(get_step_stats(checker.actualtracker, args.pred_step))
            for errtracker in checker.errortrackers: print(get_step_stats(errtracker, args.pred_step))
        else:
            print ("step must be in [0,%d)" % checker.predfilereader.npred)
            