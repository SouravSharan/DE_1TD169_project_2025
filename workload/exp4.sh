#!/bin/bash

# Define the base command for spark-submit
SPARK_SUBMIT="spark-submit --master spark://192.168.2.23:7077"
PYTHON_SCRIPT="/home/ubuntu/DE_1TD169_project_2025/workload/calc_rouge_with_cores.py"

# Define data URLs for each data size (adjust these paths if they differ in your setup)
declare -A DATA_URLS
DATA_URLS["100%"]="hdfs://192.168.2.23:9000/data/corpus-webis-tldr-17_10pct.json"
DATA_URLS["80%"]="hdfs://192.168.2.23:9000/data/corpus-webis-tldr-17_10pct_80pct.json"
DATA_URLS["60%"]="hdfs://192.168.2.23:9000/data/corpus-webis-tldr-17_10pct_60pct.json"
DATA_URLS["40%"]="hdfs://192.168.2.23:9000/data/corpus-webis-tldr-17_10pct_40pct.json"
DATA_URLS["20%"]="hdfs://192.168.2.23:9000/data/corpus-webis-tldr-17_10pct_20pct.json"
DATA_URLS["5%"]="hdfs://192.168.2.23:9000/data/corpus-webis-tldr-17_10pct_5pct.json"

# Define experiment configurations
CORES=(1 2 3 4)
WORKERS=(1 2 3 4)
DATA_SIZES=("100%" "80%" "60%" "40%" "20%" "5%")

# Log file for tracking submissions (optional, complements Python logging)
LOG_FILE="experiment_submission_final_run.log"
echo "Starting experiments at $(date)" > $LOG_FILE

# Iterate over all combinations
for cores in "${CORES[@]}"; do
    for workers in "${WORKERS[@]}"; do
        for data_size in "${DATA_SIZES[@]}"; do
            # Get the corresponding data URL
            data_url=${DATA_URLS[$data_size]}

            # Construct the command
            CMD="$SPARK_SUBMIT --deploy-mode client $PYTHON_SCRIPT --num-workers $workers --cores $cores --data-url $data_url"

            # Log the command and run it
            echo "Running: $CMD" >> $LOG_FILE
            echo "Submitting experiment: Cores=$cores, Workers=$workers, Data Size=$data_size"
            $CMD

            # Optional: Add a small delay to avoid overwhelming the cluster (adjust as needed)
            sleep 10
        done
    done
done

# Wait for all background jobs to complete
wait

echo "All experiments completed at $(date)" >> $LOG_FILE
echo "Experiments finished."
