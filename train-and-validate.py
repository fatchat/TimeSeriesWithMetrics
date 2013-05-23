# @brief Split the CPU data, traing a neural network and evaluate the predictive ability
# @author rohit
import sys
import argparse
import os
import logging
parser = argparse.ArgumentParser("Train a neural network and evaluate its predictive ability on a time-series")
parser.add_argument("--input", required=True)
parser.add_argument("--ratio", type=float, default=0.5, help="split ratio")
parser.add_argument("--alpha", type=float, default=0.5, help="weight for mv avg")
#parser.add_argument("--show-time", help="display time in output", action="store_true")
#parser.add_argument("--use-value", help="use the value metric", action="store_true", default=True)
parser.add_argument("--use-mvavg", help="use the mv. avg. metric", action="store_true")
parser.add_argument("--use-dev", help="use the dev. from mv. avg. metric", action="store_true")
parser.add_argument("--use-adjdiff", help="use the adj. diffs metric", action="store_true")
parser.add_argument("--use-runningsum", help="use the running sum metric", action="store_true")
parser.add_argument("--output-dir", required=True)
parser.add_argument("--history", type=int, required=True)
parser.add_argument("--predictions", type=int, required=True)
args = parser.parse_args()

inputfile = args.input

# output dir is a subdirectory of args.output_dir
files = os.listdir(args.output_dir)
index = 1 + len(files)
output_dir = "%s\\%d" % (args.output_dir, index)
os.makedirs(output_dir)

# resolve dependencies between metrics
args.use_value = True
if args.use_dev: args.use_mvavg = True
if args.use_adjdiff: args.use_value = True
if args.use_runningsum: args.use_mvavg = True

logging.basicConfig(filename="%s\\LOG-train-and-validate.log" % output_dir,level=logging.INFO)
logging.info("start: output-dir=%s history=%d predictions=%d split-ratio=%f alpha=%f" % (output_dir, args.history, args.predictions, args.ratio, args.alpha))
logging.info("metrics: use-value=%s use-mvavg=%s use-dev=%s use-adjdiff=%s use-runningsum=%s" % (args.use_value, args.use_mvavg, args.use_dev, args.use_adjdiff, args.use_runningsum))

# Step 1. Split into training and validation sets
trainingfile = "%s\\TrainingData.txt" % output_dir
validationfile = "%s\\ValidationData.txt" % output_dir
cmd = "python C:\\TimeSeriesWithMetrics\\split_file.py --input %s --ratio %f --output1 %s --output2 %s" % (inputfile, args.ratio, trainingfile, validationfile)
print ("splitting input into training and validation sets -> %s, %s" % (trainingfile, validationfile))
logging.info(cmd)
os.system(cmd)

# Step 2. Compute associated metrics on both sets
cmd_stem = "python C:\\TimeSeriesWithMetrics\\compute_metrics.py --alpha %f " % args.alpha
if args.use_value: cmd_stem += "--show-value "
if args.use_mvavg: cmd_stem += "--show-mvavg "
if args.use_dev: cmd_stem += "--show-dev "
if args.use_adjdiff: cmd_stem += "--show-adjdiff "
if args.use_runningsum: cmd_stem += "--show-runningsum "
training_metrics = "%s\\TrainingData.Metrics.txt" % output_dir
validation_metrics = "%s\\ValidationData.Metrics.txt" % output_dir
cmd = "%s --input %s > %s" % (cmd_stem, trainingfile, training_metrics)
print ("computing metrics on training set -> %s" % training_metrics)
logging.info(cmd)
os.system(cmd)
cmd = "%s --input %s > %s" % (cmd_stem, validationfile, validation_metrics)
print ("computing metrics on validation set -> %s" % validation_metrics)
logging.info(cmd)
os.system(cmd)

# Step 3. Transform into historical vectors
training_historical = "%s\\TrainingData.History.txt" % output_dir
validation_historical = "%s\\ValidationData.History.txt" % output_dir
cmd = "python C:\\TimeSeriesWithMetrics\\add_history.py --input %s --history %d > %s" % (training_metrics, args.history + args.predictions, training_historical)
print ("creating history vectors on training set -> %s" % training_historical)
logging.info(cmd)
os.system(cmd)
cmd = "python C:\\TimeSeriesWithMetrics\\add_history.py --input %s --history %d > %s" % (validation_metrics, args.history + args.predictions, validation_historical)
print ("creating history vectors on validation set -> %s" % validation_historical)
logging.info(cmd)
os.system(cmd)

# Step 4. Insert the training set into a SQL table
uniq_name = output_dir.replace(" ", "").replace("\\", "").replace(":","")
training_tablename = "[%s.%d]" % (uniq_name, index)
cmd = "python C:\\TimeSeriesWithMetrics\\sql_insert.py --input %s -t %s" % (training_historical, training_tablename)
print ("inserting training set into SQL table %s" % training_tablename)
logging.info(cmd)
os.system(cmd)
    
# Step 5. Manually create the DSV from withing SSAS
#print ("==> Create the data source view for the table %s, then type \"continue\"" % training_tablename)
#continue_str = ""
#while continue_str != "continue": continue_str = sys.stdin.readline().strip()

data_source = "With Metrics"
model_name = "%s%d" % (uniq_name, index)

# Step 6. Create and train the mining model
cmd = "C:\\Utils\\neural-network.exe --action MetricTrain --model-name %s --data-source \"%s\" --sql-table-name \"%s\" --query-data %s --predictions %d" % (model_name, data_source, training_tablename, validation_historical, args.predictions)
print ("creating and training mining model")
logging.info(cmd)
os.system(cmd)

# Step 7. Validate the trained model against the validation set
predicted_values = "%s\\PredictedData.txt" % output_dir
cmd = "C:\\Utils\\neural-network.exe --action MetricQuery --model-name %s --query-data %s --predictions %d --output-file %s" % (model_name, validation_historical, args.predictions, predicted_values)
print ("predicting values using validation set %s" % validation_historical)
logging.info(cmd)
os.system(cmd)

# Step 8. Compute statistics on the predictions vs. actual values
summary_file = "%s\\Summary.txt" % output_dir
print ("computing accuracy statistics using predicted values %s" % predicted_values)
for pred_step in range(0, args.predictions):
    cmd = "python C:\\TimeSeriesWithMetrics\\analyze-predictions.py --input %s --summary-file %s --pred-step %d" % (predicted_values, summary_file, 1 + pred_step)
    logging.info(cmd)
    os.system(cmd)
