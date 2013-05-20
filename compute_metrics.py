# @brief Compute metrics from (t,v) time-series
# @author rohit
import sys
import argparse

parser = argparse.ArgumentParser("Compute time series derived metrics")
parser.add_argument("--input", required=True, help="input file containing time,value pairs")
parser.add_argument("--alpha", help="moving average alpha", type=float, default=0.3)
parser.add_argument("--show-time", help="display time in output", action="store_true")
parser.add_argument("--show-value", help="display value in output", action="store_true")
parser.add_argument("--show-mvavg", help="display mv. avg. in output", action="store_true")
parser.add_argument("--show-dev", help="display dev. from mv. avg. in output", action="store_true")
parser.add_argument("--show-adjdiff", help="display adj. diffs in output", action="store_true")
parser.add_argument("--show-runningsum", help="display running sum in output", action="store_true")
                    
args = parser.parse_args()
# show headers
output_str = ""
if (args.show_time): output_str += "time "
if (args.show_value): output_str += "value "
if (args.show_mvavg): output_str += "mvavg "
if (args.show_dev): output_str += "dev "
if (args.show_adjdiff): output_str += "adjdiff "
if (args.show_runningsum): output_str += "runningsum "
if (output_str != ""): print (output_str)
# arrays for input and computed time-series
t = [] # time
v = [] # value
m = [] # mv avg
h = [] # dev from mv avg
d = [] # adj diff
s = [] # cum sum of h
n = -1 # index in these arrays
start_time = 0
# open file, load input and compute associated metrics
with open(args.input, "r") as inputfile:
    for line in inputfile.readlines():
        [t_str, v_str] = [x.strip() for x in line.split(',')]
        time = int(t_str)
        value = float(v_str)
        v.append(value)
        n += 1 # highest index for t/v series
        if n == 0:
            start_time = time
            t.append(0)
            m.append(v[0])
            h.append(0)
            d.append(0)
            s.append(0)
        else:
            t.append(time - start_time)
            timediff = t[n] - t[n-1]
            m.append(m[n-1] * (1 - args.alpha) + v[n] * args.alpha)
            h.append(v[n] - m[n])
            d.append(v[n] - v[n-1])
            s.append(s[n-1] + h[n])
            output_str = ""
            if (args.show_time): output_str += ("%5d " % t[n])
            if (args.show_value): output_str += ("%+02.4f " % v[n])
            if (args.show_mvavg): output_str += ("%+02.4f " % m[n])
            if (args.show_dev): output_str += ("%+02.4f " % h[n])
            if (args.show_adjdiff): output_str += ("%+02.4f " % d[n])
            if (args.show_runningsum): output_str += ("%+02.4f " % s[n])
            if (output_str != ""): print (output_str)
