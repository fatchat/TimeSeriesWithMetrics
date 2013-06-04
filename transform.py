import sys
import os
from math import sqrt
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--output")
parser.add_argument("--input-delim", default=" ")
parser.add_argument("--delim", default=',', help="OUTPUT delimiter")
parser.add_argument("--normalize", action="store_true")
parser.add_argument("--alpha", type=float, default=0.5, help="parameter for moving average and moving variance computation")
parser.add_argument("--column", type=int, required=True)
parser.add_argument("--compute-static-msigma", action="store_true")
args = parser.parse_args()

mean = None
var = None

if args.compute_static_msigma and args.normalize:
    with open(args.input, "r") as inputfile:
        total = 0
        count = 0
        sq_total = 0
        vmax = sys.float_info.min
        vmin = sys.float_info.max
        for line in inputfile.readlines():
            #print (line)
            entry = line.strip().split(args.input_delim)[args.column]
            #print ("[%s]" % entry)
            value = float(entry)
            total += value
            sq_total += (value * value)
            vmax = max(vmax, value)
            vmin = min(vmin, value)
            count += 1
        mean = float(total / count)
        var = float(sq_total / count) - float (mean * mean)
        print ("mean=%f var=%f max=%f=>%f min=%f=>%f 100=>%f" % (mean, var, vmax, (vmax-mean)/sqrt(var), vmin, (vmin-mean)/sqrt(var), (100-mean)/sqrt(var)))
        
if args.output != None:
    with open(args.input, "r") as inputfile:
        tval = 0
        outputfile = open(args.output, "w")
        for line in inputfile.readlines():
            value = float(line.strip().split(args.input_delim)[args.column])
            if args.normalize:
                if not args.compute_static_msigma:
                    if mean == None:
                        mean = value
                        var = 0.0
                    else:
                        mean = mean * (1 - args.alpha) + value * (args.alpha)
                        var = var * (1 - args.alpha) + (value - mean) * (value - mean) * (args.alpha)
                value = (value - mean) / sqrt(var) if var > 0 else None
            if value != None: outputfile.write ("%d%c%f\n" % (tval, args.delim, value))
            tval += 1
