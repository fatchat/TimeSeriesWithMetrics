# @brief Validate the accuracy of our model
# @author rohit
import os
import sys
import argparse
from math import sqrt
from predfilereader import PredFileReader

# ==========================================================================================================        
parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True, help="name of PredictedValues file")
parser.add_argument("--fwd-sigma", type=float)
parser.add_argument("--imm-sigma", type=float)
parser.add_argument("--alpha", type=float)
parser.add_argument("--metric-idx", type=int, default=0)
parser.add_argument("--roc-steps", type=int)
args = parser.parse_args()

# ==========================================================================================================        
def print_if (value, name):
    if value != None: print ("%s is %f" % (name, value))
    
# ==========================================================================================================        
class ConfusionMatrix:
    def __init__ (self, alpha):
        self.alpha = alpha
        self.tp = 0
        self.tn = 0
        self.fp = 0
        self.fn = 0

    def update (self, occurred, predicted):
        if       occurred and     predicted : self.tp += 1
        elif     occurred and not predicted : self.fn += 1
        elif not occurred and     predicted : self.fp += 1
        elif not occurred and not predicted : self.tn += 1
        else:
            raise LogicError    # :-(

    def print_matrix (self):
        print ("TN=%d TP=%d FN=%d FP=%d" % (self.tn, self.tp, self.fn, self.fp))
        ap = self.tp + self.fn  # actual positive
        an = self.tn + self.fp  # actual negative
        pp = self.fp + self.tp  # predicted positive
        pn = self.tn + self.fn  # predicted negative
        print("AP=%d AN=%d PP=%d PN=%d" % (ap, an, pp, pn))
        print("Total=%d" % (ap + an))
        
    # when something happens, how often are we correct?
    # (also called "recall")
    def sensitivity (self):
        ap = self.tp + self.fn
        if ap != 0: return float(self.tp) / ap
        return None

    # when something happens, how often are we wrong? 1 - sensitivity
    def FNR (self):
        ap = self.tp + self.fn # actual positive
        if ap != 0: return float(self.fn) / ap
        return None

    # when something doesn't happen, how often are we correct?
    def specificity (self):
        an = self.tn + self.fp
        if an != 0: return float(self.tn) / an
        return None
  
    # when something doesn't happen, how often are we wrong? 1 - specificity
    def FPR (self):
        an = self.tn + self.fp  # actual negative
        if an != 0: return float(self.fp) / an
        return None
        
    # when we say something happens, how often are we correct?
    def precision (self):
        pp = self.tp + self.fp
        if pp != 0: return float(self.tp) / pp
        return None

    # false discovery rate
    # when we say something happens, how often are we wrong? 1 - precision
    def FDR (self):
        pp = self.tp + self.fp # predicted positive
        if pp != 0: return float(self.fp) / pp
        return None
        
    # Matthews' correlation coefficient
    def MCC (self):
        num = float(self.tp * self.tn - self.fp * self.fn)
        ap = self.tp + self.fn  # actual positive
        an = self.tn + self.fp  # actual negative
        pp = self.fp + self.tp  # predicted positive
        pn = self.tn + self.fn  # predicted negative
        den = sqrt (ap * an * pp * pn)
        if den != 0: return num / den
        return None

    # this is not very useful as is, most values will be around 1
    def alpha_val (self):
        if self.alpha != None:
            den = (self.tn + self.tp + self.fp + self.alpha * self.fn)
            if den != 0 : return (self.tn + self.tp - self.fp - self.alpha * self.fn) / den
        return None

# ==========================================================================================================        
class ForwardAlarmGenerator:
    def __init__ (self, threshold, alpha):
        if threshold <= 0: raise ValueError
        self.threshold = threshold
        self.confusion_matrix = ConfusionMatrix(alpha)

    def update (self, actual, predicted):
        self.confusion_matrix.update(occurred = actual >= self.threshold, predicted = predicted >= self.threshold)

    def show_results (self):
        self.confusion_matrix.print_matrix()
        print_if(self.confusion_matrix.sensitivity(), "sensitivity (high=>few false negatives)")
        print_if(self.confusion_matrix.specificity(), "specificity (high=>few false positives)")
        print_if(self.confusion_matrix.precision(), "precision")
        print_if(self.confusion_matrix.FPR (), "FPR")
        print_if(self.confusion_matrix.FNR (), "FNR")
        print_if(self.confusion_matrix.MCC (), "MCC")
        print_if(self.confusion_matrix.alpha_val (), "alpha-measure")

    def showROC (self):
        tpr = self.confusion_matrix.sensitivity()
        fpr = self.confusion_matrix.FPR()
        if tpr != None and fpr != None:
            print ("%f %f %f" % (fpr, tpr, self.threshold))
            
# ==========================================================================================================        
class ImmediateAlarmGenerator:
    def __init__ (self, sigma=0):
        if sigma < 0: raise ValueError
        self.sigma = sigma
        
    def update (self, actual, predicted):
        pass
        
    def show_results (self):
        pass
                
# ==========================================================================================================        
class AccuracyMeasurer:
    def __init__ (self):
        self.errors = []
        self.abs_errors = []
        self.abs_pctg_errors = []
        self.sq_errors = []

    def update (self, actual, predicted):
        error = actual - predicted
        abs_error = abs(error)
        self.errors.append(error)
        self.abs_errors.append(abs_error)
        if actual != 0: self.abs_pctg_errors.append(abs_error / actual)
        self.sq_errors.append(error * error)
        
    # mean error
    def ME (self):
        N = len(self.errors)
        if N != 0: return sum(self.errors) / N
        return None
    
    # mean abs. error
    def MAD (self):
        N = len(self.abs_errors)
        if N != 0: return sum(self.abs_errors) / N
        return None
        
    def tracking_signal (self):
        mad = self.MAD()
        if mad != None: return sum(self.errors) / mad
        return None
        
    # mean abs. % error
    def MAPE (self):
        N = len(self.abs_pctg_errors)
        if N > 0: return sum(self.abs_pctg_errors) / N
        return None

    # mean sq. error
    def MSE (self):
        N = len(self.sq_errors)
        if N > 0: return sum(self.sq_errors) / N
        return None
        
    # root of mean sq. error
    def RMSE (self):
        mse = self.MSE()
        if mse != None: return sqrt(mse)
        return None
        
    def show_results (self):
        print_if(self.MAD(), "MAD")
        print_if(self.ME(), "ME")
        print_if(self.tracking_signal(), "tracking signal")
        print_if(self.MAPE(), "MAPE")
        print_if(self.MSE(), "MSE")
        print_if(self.RMSE(), "RMSE")
        
# ==========================================================================================================        
class MinMaxTracker:
    def __init__(self):
        self.actual_max = sys.float_info.min
        self.actual_min = sys.float_info.max
        self.predicted_max = sys.float_info.min
        self.predicted_min = sys.float_info.max

    def update(self, actual, predicted):
        self.actual_max     = max(self.actual_max, actual)
        self.actual_min     = min(self.actual_min, actual)
        self.predicted_max  = max(self.predicted_max, predicted)
        self.predicted_min  = min(self.predicted_min, predicted)
        
    def show_results(self):
        print ("Actual: [%f, %f] Predicted: [%f, %f]" % (self.actual_min, self.actual_max, self.predicted_min, self.predicted_max))
        
# ==========================================================================================================        
class PredictionChecker:
    def __init__(self, inputfilename, metric_idx):
        self.predfilereader = PredFileReader (inputfilename)
        self.metric_idx = metric_idx
        self.processors = []
        
    def process_input_line(self, values):
        for step in range (0, self.predfilereader.npred):
            actual      = self.predfilereader.get_actual (values, step)
            predicted   = self.predfilereader.get_predicted (values, step, self.metric_idx)
            for processor in self.processors:
                processor.update(actual, predicted)
            
    def process_file(self):
        while True:
            values = self.predfilereader.get_next_line()
            if len(values) == 0: break
            self.process_input_line(values)
            # skip next npred-1 lines
            for i in range (1, self.predfilereader.npred): self.predfilereader.inputfile.readline()

    def show_results(self):
        print("metric is %s" % (self.predfilereader.metrics[1 + self.metric_idx]))
        for p in self.processors: p.show_results()
        
# ==========================================================================================================        
# -- start --
if args.roc_steps != None:
    for fwd_sigma in range (1, 1 + args.roc_steps):
        pred_checker = PredictionChecker(args.input, args.metric_idx)
        fwd_alarm_gen = ForwardAlarmGenerator(0.01 * fwd_sigma, None)
        pred_checker.processors = [fwd_alarm_gen]
        pred_checker.process_file()
        fwd_alarm_gen.showROC()
else:
    processors = [MinMaxTracker()]
    if args.fwd_sigma != None: processors.append(ForwardAlarmGenerator(args.fwd_sigma, args.alpha))
    if args.imm_sigma != None: processors.append(ImmediateAlarmGenerator(args.imm_sigma))
    processors.append(AccuracyMeasurer())

    pred_checker = PredictionChecker(args.input, args.metric_idx)
    pred_checker.processors = processors
    pred_checker.process_file()
    pred_checker.show_results()
