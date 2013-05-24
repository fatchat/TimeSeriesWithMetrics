# @brief plot future values
# @author rohit
import sys
import os
import argparse

parser=argparse.ArgumentParser("Plot future values")
parser.add_argument("--input", required=True, help="input file")
parser.add_argument("--output", required=True, help="output file")
parser.add_argument("--future", required=True, type=int, help="future time as row number (>= 0)")
args = parser.parse_args()

# print up to 10 actual values before the future time
# going forward from the future time print npredicted values for all available metrics

prior_vals = []
line = ""

with open(args.input, "r") as inputfile:
    headers = inputfile.readline().strip().split()
    if headers[0] == "version":
        versnum = int(headers[1])
        if versnum > 0:
            print ("this script needs to be updated for versions > 0")
            sys.exit(1)
        headers = inputfile.readline().strip().split()
    else:
        versnum = 0
    line = inputfile.readline().strip().split()
    metrics = headers[1:]
    npredicted = int(len(line) / len(headers))
    f = args.future
    while f > 0:
        prior_vals.append(float(line[0]))
        line = inputfile.readline().strip().split()
        f -= 1
    if len(prior_vals) != args.future: raise IndexError

prior_vals = prior_vals[-5:]

print ("npredicted=%d metrics=%s" % (npredicted, ",".join(metrics)))
print (line)
# now the line contains (val @ future, val @ future + 1, ..., val @ future + npredicted - 1,
#                        metric_1 @ future, metric_2 @ future, .. , metric_p @ future
#                        metric_1 @ future+1, metric_2 @ future+1, .. , metric_p @ future+1,...)
with open(args.output, "w") as outputplotfile:
    outputplotfile.write(" ".join(headers) + "\n")
    outputplotfile.write("%f %s\n" % (prior_vals[0], "0 " * len(metrics)))
    for i in range(1, len(prior_vals)):
        outputplotfile.write(str(prior_vals[i]))
    format_str = ("%f " * (1 + len(metrics))) + "\n"
    for i in range(0, npredicted):
        vals = []
        vals.append(float(line[i])) # val
        for j in range(0, len(metrics)):
            vals.append(float(line[npredicted + i * len(metrics) + j]))
        if len(vals) != 1 + len(metrics): raise IndexError ("%d != 2 + %d" % (len(vals), npredicted))
        outputplotfile.write(format_str % tuple(vals))

os.system("python C:\\TimeSeriesWithMetrics\\plot_predictions.py --input %s" % args.output)
