#!/bin/bash

# Path to Spark submit
SPARK_SUBMIT="$SPARK_HOME/bin/spark-submit"

# Path to Python script
SCRIPT_PATH="/home/ubuntu/DE_1TD169_project_2025/workload/calculate_rouge_experiments.py"

# HDFS base path
HDFS_BASE="hdfs://192.168.2.23:9000/data"

# Dataset paths
DATA_100="$HDFS_BASE/corpus-webis-tldr-17_10pct.json"           # 100% of 10% (~2 GB)
DATA_50="$HDFS_BASE/corpus-webis-tldr-17_10pct_50pct.json"     # 50% of 10% (~1 GB)
DATA_20="$HDFS_BASE/corpus-webis-tldr-17_10pct_20pct.json"     # 20% of 10% (~0.4 GB)
DATA_10="$HDFS_BASE/corpus-webis-tldr-17_10pct_10pct.json"     # 10% of 10% (~0.2 GB)

# Clear previous log file
echo -e "Dataset\tWorkers\tTime (s)\tRows\tThroughput (rows/s)\tDriver CPU (%)\tDriver Memory (%)" > rouge_experiments.log

# Function to run an experiment
run_exp() {
    local data_path=$1
    local workers=$2
    echo "Running experiment: $data_path with $workers workers"
    $SPARK_SUBMIT --deploy-mode client "$SCRIPT_PATH" \
        --data_path "$data_path" \
        --num_workers "$workers"
}

# Experiment 1
echo "Starting Experiment 1..."
run_exp "$DATA_100" 4  # 100% data, 4 workers
run_exp "$DATA_50"  3  # 50% data, 3 workers
run_exp "$DATA_20"  2  # 20% data, 2 workers
run_exp "$DATA_10"  1  # 10% data, 1 worker

# Experiment 2
echo "Starting Experiment 2..."
run_exp "$DATA_100" 2  # 100% data, 2 workers
run_exp "$DATA_50"  2  # 50% data, 2 workers
run_exp "$DATA_20"  2  # 20% data, 2 workers
run_exp "$DATA_10"  2  # 10% data, 2 workers

echo "Experiments completed. Results are in rouge_experiments.log"