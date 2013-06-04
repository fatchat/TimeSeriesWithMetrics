# @brief Module to read PredictedData.txt files
# @author rohit
import os
import sys
# ==========================================================================================================        
class PredFileReader:
    def __init__(self, inputfilename):
        self.inputfile = open(inputfilename, "r")
        self.versnum = 0
        self.npred = None
        self.metrics = []
        self.first_time = True
        
    def get_actual(self, entries, step):
        return float(entries[step])
            
    def get_predicted(self, entries, step, metric_idx):
        if (1 + metric_idx) >= len(self.metrics): raise ValueError
        if self.versnum == 0:
            pred_val = float(entries[self.npred + metric_idx + len(self.metrics) * step])
            return pred_val
        elif self.versnum == 1:
            pred_val = float(entries[step + self.npred * (1 + metric_idx)])
            return pred_val
        else:
            print ("cannot handle version %d, quitting." % self.versnum)
            sys.exit(1)
                
    def get_next_line(self):
        line = self.inputfile.readline().strip().split()
        if line == None: return None
        if self.first_time:
            if line[0] == "version":
                self.versnum = int(line[1])
                self.npred = int(line[3])
                self.metrics = self.inputfile.readline().strip().split()  # including "actual"
            else:
                self.metrics = line
            values = self.inputfile.readline().strip().split()
            if self.versnum == 0:
                self.npred = int(len(values) / len(self.metrics))
            if self.npred <= 0:
                raise InputError
            self.first_time = False
            return values
        else:
            return line
    
