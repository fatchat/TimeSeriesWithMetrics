# @brief plot a predictions file
# @author rohit
import sys
import os
import argparse


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

parser = argparse.ArgumentParser("Plot a predictions file")
parser.add_argument("--input", required=True)
parser.add_argument("--start", type=int, default=-1, help="starting row number")
parser.add_argument("--end", type=int, default=-1, help="ending row number")
parser.add_argument("--metric", help="metric to plot")
args = parser.parse_args()

inputfile = open(args.input, "r")
headers = inputfile.readline().strip().split()
backslashedinput = args.input.replace("\\", "\\" + "\\")

plotcmd = "set grid;"
plotcmd += "set title \"%s\";" % backslashedinput
plots = []
conjunction = get_row_spec_condition(args.start, args.end)
for header in headers:
    if args.metric not in [None, "", "all"] and args.metric != header:
        continue
    if conjunction != "":
        row_spec = "(%s ? $%d : 0/0)" % (conjunction, 1 + headers.index(header))
    else:
        row_spec = str(1 + headers.index(header))
    plots.append("\"%s\" using %s title \"%s\"" % (backslashedinput, row_spec, header))

inputfile.close()

if len(plots) > 0:
    plotcmd += "plot " + ",".join(plots)
    cmd = "gnuplot -p -e \"%s\"" % plotcmd.replace("\"", "\\\"")
    print ("running [%s]" % cmd)
    os.system(cmd)
else:
    print ("nothing to do")
    
