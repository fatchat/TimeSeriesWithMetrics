# @brief Take a time series vector of values & metrics, and compute a historical series
# @author rohit
import sys
import argparse
# command-line args
parser = argparse.ArgumentParser("Compute time series with a history")
parser.add_argument("--input", required=True, help="input file containing time,value,metrics tuples")
parser.add_argument("--history", required=True, type=int, help="history length")
args = parser.parse_args()
# read data
with open(args.input, "r") as inputfile:
    headerline = inputfile.readline().strip()
    headers = headerline.split(' ')
    has_time = (headers[0] == "time")
    # hold (history * # non-time headers) values. insert at end, remove from front
    buffer = []
    packet_size = len(headers)
    if has_time: packet_size -= 1
    buffer_size = args.history * packet_size
    # read time vector series 
    for line in inputfile.readlines():
        components = line.strip().split(' ')
        if has_time: components = components[1:]
        buffer += components
        if (len(buffer) == buffer_size):
            print(" ".join(buffer))
            buffer=buffer[packet_size:]
            
