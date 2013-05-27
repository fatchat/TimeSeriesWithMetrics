# @brief simple wrapper around gnuplot -e. plot specified columns and rows. useful for TrainingData.History.txt files
# @author rohit
import os
import sys
import argparse
parser=argparse.ArgumentParser("gnuplot wrapper")
parser.add_argument("--input", required=True)
parser.add_argument("--col-start",type=int, default=1)
parser.add_argument("--col-end", type=int, required=True)
parser.add_argument("--row-start", type=int, default=0)
parser.add_argument("--row-end", type=int, default=0)
args=parser.parse_args()

def get_row_spec_condition (start, end):
    row_spec = ""
    lb_spec = ""
    ub_spec = ""
    conjunction = ""
    if start > 0: lb_spec = "$0 >= %d" % start
    if end > 0: ub_spec = "$0 <= %d" % end
    if lb_spec != "" and ub_spec != "": conjunction = "%s && %s" % (lb_spec, ub_spec)
    if conjunction == "" and lb_spec != "": conjunction = lb_spec
    if conjunction == "" and ub_spec != "": conjunction = ub_spec
    return conjunction    

backslashedinput = args.input.replace("\\", "\\" + "\\")
plotcmd = "set grid;"
plotcmd += "set title \"%s\";" % backslashedinput
plotcmd += "set linestyle 1;"
plots = []
conjunction = get_row_spec_condition(args.row_start, args.row_end)
for col in range(args.col_start, args.col_end):
	if conjunction != "":
		row_spec = "(%s ? $%d : 0/0)" % (conjunction, col)
	else:
		row_spec = str(col)
	plots.append("\"%s\" using %s title \"%s\" with lines" % (backslashedinput, row_spec, str(col)))

if len(plots) > 0:
    plotcmd += "plot " + ",".join(plots)
    cmd = "gnuplot -p -e \"%s\"" % plotcmd.replace("\"", "\\\"")
    print ("running [%s]" % cmd)
    os.system(cmd)
else:
    print ("nothing to do")
    
