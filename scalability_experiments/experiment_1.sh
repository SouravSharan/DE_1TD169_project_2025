#!/bin/bash
for workers in 1 2 3 4; do
    $SPARK_HOME/bin/spark-submit --deploy-mode client \
        ../scripts/calculate_rouge_experiments.py \
        --data_path hdfs://192.168.2.23:9000/data/corpus-webis-tldr-17_10pct_50pct.json \
        --num_workers $workers
done
