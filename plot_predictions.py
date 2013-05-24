# @brief plot a predictions file
# @author rohit
import sys
import os
import argparse

parser = argparse.ArgumentParser("Plot a predictions file")
parser.add_argument("--input", required=True)
parser.add_argument("--start", type=int, default=-1, help="starting row number")
parser.add_argument("--end", type=int, default=-1, help="ending row number")
parser.add_argument("--metrics", help="metrics to plot")
parser.add_argument("--pred", type=int, default=0, help="which pred step (0-based index)")
args = parser.parse_args()

def get_row_spec_condition (start, end):
    row_spec = ""
    lb_spec = ""
    ub_spec = ""
    conjunction = ""
    if args.start > 0: lb_spec = "$0 >= %d" % args.start
    if args.end > 0: ub_spec = "$0 <= %d" % args.end
    if lb_spec != "" and ub_spec != "": conjunction = "%s && %s" % (lb_spec, ub_spec)
    if conjunction == "" and lb_spec != "": conjunction = lb_spec
    if conjunction == "" and ub_spec != "": conjunction = ub_spec
    return conjunction    

with open(args.input, "r") as inputfile:
    first_line = inputfile.readline().strip().split()
    if first_line[0].strip() == "version":
        versnum = int(first_line[1])
        npredicted = int(first_line[3])
        metrics = inputfile.readline().strip().split()
    else:
        versnum = 0
        metrics = first_line # incl. "actual"
        npredicted = len(inputfile.readline().strip().split()) / len(metrics)
    if (args.pred >= npredicted):
        print ("--pred must be less than %d" % npredicted)
        sys.exit(1)
    print ("npredicted=%d" % npredicted)

backslashedinput = args.input.replace("\\", "\\" + "\\")

plotcmd = "set grid;"
plotcmd += "set title \"%s\";" % backslashedinput
plotcmd += "set linestyle 1;"
plots = []
conjunction = get_row_spec_condition(args.start, args.end)

def get_column_index (versnum, npred, metric_idx, n_metrics, pred_step):
    if versnum == 0:
        if metric_idx == 0:             # "actual"
            return pred_step            # first actual is @ t_1 not t_0
        else:
            return (npred +             # skip "actual"s
                    metric_idx - 1 +    # metric_idx > 0 since this is not "actual"
                    (n_metrics - 1) * pred_step) # the jump is n-1 because there is no "actual"
    else:
        print ("unsupported versnum %d" % versnum)
        sys.exit(1)
        
for metric in metrics:
    if args.metrics not in [None, "", "all"] and metric not in args.metrics.split():
        continue
    # col index + 1 because gnuplot columns start at 1 ($0 is the row number)
    column_index = 1 + get_column_index(versnum, npredicted, metrics.index(metric), len(metrics), args.pred)
    if conjunction != "":
        row_spec = "(%s ? $%d : 0/0)" % (conjunction, column_index)
    else:
        row_spec = str(column_index)
    plots.append("\"%s\" using %s title \"%s\" with lines" % (backslashedinput, row_spec, metric))

if len(plots) > 0:
    plotcmd += "plot " + ",".join(plots)
    cmd = "gnuplot -p -e \"%s\"" % plotcmd.replace("\"", "\\\"")
    print ("running [%s]" % cmd)
    os.system(cmd)
else:
    print ("nothing to do")
    
