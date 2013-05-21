# @brief Split the CPU data, traing a neural network and evaluate the predictive ability
# @author rohit
import sys
import argparse
import os
import logging
parser = argparse.ArgumentParser("Train a neural network and evaluate its predictive ability on a split of CPU.smooth.r")
parser.add_argument("--ratio", type=float, default=0.5, help="split ratio")
parser.add_argument("--alpha", type=float, default=0.5, help="weight for mv avg")
#parser.add_argument("--show-time", help="display time in output", action="store_true")
parser.add_argument("--show-value", help="display value in output", action="store_true")
parser.add_argument("--show-mvavg", help="display mv. avg. in output", action="store_true")
parser.add_argument("--show-dev", help="display dev. from mv. avg. in output", action="store_true")
parser.add_argument("--show-adjdiff", help="display adj. diffs in output", action="store_true")
parser.add_argument("--show-runningsum", help="display running sum in output", action="store_true")
parser.add_argument("--output-dir", required=True)
parser.add_argument("--history", type=int, required=True)
parser.add_argument("--predictions", type=int, required=True)
args = parser.parse_args()

# fixed input file for now
inputfile = "F:\\TextData\\CPU.smooth.r.txt"

# output dir is a subdirectory of args.output_dir
files = os.listdir(args.output_dir)
index = 1 + len(files)
output_dir = "%s\\%d" % (args.output_dir, index)
os.makedirs(output_dir)

logging.basicConfig(filename="%s\\train-and-validate.log" % output_dir,level=logging.INFO)
logging.info("start: output-dir=%s history=%d predictions=%d split ratio=%f alpha=%f" % (args.output_dir, args.history, args.predictions, args.ratio, args.alpha))

# Step 1. Split into training and validation sets
trainingfile = "%s\\TrainingData.txt" % output_dir
validationfile = "%s\\ValidationData.txt" % output_dir
cmd = "python C:\\TimeSeriesWithMetrics\\split_file.py --input %s --ratio %f --output1 %s --output2 %s" % (inputfile, args.ratio, trainingfile, validationfile)
logging.info(cmd)
os.system(cmd)

# Step 2. Compute associated metrics on both sets
cmd_stem = "python C:\\TimeSeriesWithMetrics\\compute_metrics.py --alpha %f " % args.alpha
if args.show_value: cmd_stem += "--show-value "
if args.show_mvavg: cmd_stem += "--show-mvavg "
if args.show_dev: cmd_stem += "--show-dev "
if args.show_adjdiff: cmd_stem += "--show-adjdiff "
if args.show_runningsum: cmd_stem += "--show-runningsum "
training_metrics = "%s\\TrainingData.Metrics.txt" % output_dir
validation_metrics = "%s\\ValidationData.Metrics.txt" % output_dir
cmd = "%s --input %s > %s" % (cmd_stem, trainingfile, training_metrics)
logging.info(cmd)
os.system(cmd)
cmd = "%s --input %s > %s" % (cmd_stem, validationfile, validation_metrics)
logging.info(cmd)
os.system(cmd)

# Step 3. Transform into historical vectors
training_historical = "%s\\TrainingData.History.txt" % output_dir
validation_historical = "%s\\ValidationData.History.txt" % output_dir
cmd = "python C:\\TimeSeriesWithMetrics\\add_history.py --input %s --history %d > %s" % (training_metrics, args.history + args.predictions, training_historical)
logging.info(cmd)
os.system(cmd)
cmd = "python C:\\TimeSeriesWithMetrics\\add_history.py --input %s --history %d > %s" % (validation_metrics, args.history + args.predictions, validation_historical)
logging.info(cmd)
os.system(cmd)

# Step 4. Insert the training set into a SQL table
training_tablename = "[Training.%d]" % index
cmd = "python C:\\TimeSeriesWithMetrics\\sql_insert.py --input %s -t %s" % (training_historical, training_tablename)
logging.info(cmd)
os.system(cmd)
    
# Step 5. Manually create the DSV and the model. Train the model from withing SSAS
print ("Manually create the DSV and the model. Train the model from withing SSAS. Then type \"continue\"")
continue_str = ""
while continue_str != "continue": continue_str = sys.stdin.readline().strip()

print ("enter the model name used")
model_name = sys.stdin.readline().strip()

# Step 6. Validate the trained model against the validation set
predicted_values = "%s\\PredictedData.txt" % output_dir
cmd = "C:\\Utils\\neural-network.exe --action MetricQuery --model-name %s --query-data %s --predictions %d --output-file %s" % (model_name, validation_historical, args.predictions, predicted_values)
logging.info(cmd)
os.system(cmd)

# Step 7. Compute statistics on the predictions vs. actual values
validation_report = "%s\\Report.txt" % output_dir
