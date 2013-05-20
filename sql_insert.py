# @brief Insert history vectors into an SQL table
# @author rohit
import sys
import argparse

if "C:\\Scripts" not in sys.path:
    sys.path.append("C:\\scripts")
import tablegenerator
# globals
dbname = "NeuralNetInput"
# command-line args
parser = argparse.ArgumentParser("Insert time series vectors into SQL table")
parser.add_argument("--input", required=True, help="input file")
parser.add_argument("-t", "--tablename", required=True)
parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument("-d", "--dryrun", action="store_true")
args = parser.parse_args()
# read headers
with open(args.input, "r") as inputfile:
    headerline = inputfile.readline().strip()
    headers = headerline.split(' ')
    nextline = inputfile.readline().strip()
    components = nextline.split(' ')
    history = len(components) / len(headers)
    if history != float(int(history)):
        print ("number of components should be an integral multiple of the number of headers")
        sys.exit(1)
    history = int(history)
# create table
tg = tablegenerator.TableGenerator()
tg.verbose = args.verbose
tg.dryrun = args.dryrun
try:
    tg.connect(dbname)
except pypyodbc.DatabaseError:
    print ("Could not connect to db [%s]" % dbname)
    sys.exit(1)
column_spec = []
for i in range(0, history):
    for header in headers:
        column_spec.append({'name':"%s_%d" % (header, i)          , 'type':'float'})
tg.create(args.tablename, column_spec)

# insert data 
with open(args.input, "r") as inputfile:
    headerline = inputfile.readline().strip()
    row_num = 0
    for line in inputfile.readlines():
        # key_col
        row = [row_num]
        # input values
        row += line.strip().split(' ')
        # insert into table
        tg.insert(row) 
        row_num += 1
