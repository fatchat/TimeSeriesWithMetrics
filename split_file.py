# @brief Split a file into two components
# @author rohit
import sys
import argparse
import random

parser = argparse.ArgumentParser ("Split a file into two components")
parser.add_argument("--input", help="input file", required=True)
parser.add_argument("--output1", help="output file 1", required=True)
parser.add_argument("--output2", help="output file 2", required=True)
parser.add_argument("--ratio", required=True, type=float, help="split ratio")
args = parser.parse_args()

if (args.ratio <= 0 or args.ratio >= 1):
    print ("ratio needs to lie in the open interval (0,1)")
    sys.exit(1)

nlines = 0
with open(args.input, "r") as inputfile:
    nlines = len(inputfile.readlines()) - 1

with open(args.input, "r") as inputfile:
    header = inputfile.readline()
    outputfile1 = open (args.output1, "w")
    outputfile2 = open (args.output2, "w")
    outputfile1.write(header)
    outputfile2.write(header)
    line_index = 0
    for line in inputfile.readlines():
        if line_index < nlines * args.ratio:
            outputfile1.write(line)
            line_index += 1
        else:
            outputfile2.write(line)
                
