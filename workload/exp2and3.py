import argparse
import time
import logging
import psutil
import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from rouge_score import rouge_scorer

# Logging setup
logging.basicConfig(filename='rouge_experiments_2_and_3.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

data_paths = {
    "100%": "hdfs://192.168.2.23:9000/data/corpus-webis-tldr-17_10pct.json",
    "50%": "hdfs://192.168.2.23:9000/data/corpus-webis-tldr-17_10pct_50pct.json",
    "20%": "hdfs://192.168.2.23:9000/data/corpus-webis-tldr-17_10pct_20pct.json",
    "10%": "hdfs://192.168.2.23:9000/data/corpus-webis-tldr-17_10pct_10pct.json"
}

experiments = {
    "exp2": {"100%": 4, "50%": 3, "20%": 2, "10%": 1},
    "exp3": {"100%": 2, "50%": 2, "20%": 2, "10%": 2}
}

def run_experiment(exp_name, data_size, num_workers):
    data_path = data_paths[data_size]
    
    spark = SparkSession.builder \
        .appName(f"ROUGE_{exp_name}_{data_size}_{num_workers}_workers") \
        .master("spark://192.168.2.23:7077") \
        .config("spark.executor.instances", num_workers) \
        .config("spark.executor.cores", 2) \
        .config("spark.executor.memory", "4g") \
        .getOrCreate()
    
    start_time = time.time()
    start_cpu = psutil.cpu_percent()
    start_mem = psutil.virtual_memory().percent
    
    df = spark.read.json(data_path)
    row_count = df.count()
    
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    
    def calculate_rouge(summary, content):
        if not summary or not content:
            return 0.0, 0.0, 0.0
        scores = scorer.score(content, summary)
        return scores['rouge1'].fmeasure, scores['rouge2'].fmeasure, scores['rougeL'].fmeasure
    
    from pyspark.sql.functions import udf
    from pyspark.sql.types import StructType, StructField, FloatType
    
    rouge_schema = StructType([
        StructField('rouge1', FloatType(), True),
        StructField('rouge2', FloatType(), True),
        StructField('rougeL', FloatType(), True)
    ])
    
    rouge_udf = udf(lambda summary, content: calculate_rouge(summary, content), rouge_schema)
    df_with_rouge = df.withColumn("rouge_scores", rouge_udf(col('summary'), col('content')))
    df_with_rouge = df_with_rouge.select(
        'author', 'subreddit', 'summary', 'content',
        'rouge_scores.rouge1', 'rouge_scores.rouge2', 'rouge_scores.rougeL'
    )
    
    output_path = f"hdfs://192.168.2.23:9000/outputs/rouge_{exp_name}_{data_size}_{num_workers}w.json"
    df_with_rouge.write.mode("overwrite").json(output_path)
    
    end_time = time.time()
    processing_time = end_time - start_time
    throughput = row_count / processing_time
    end_cpu = psutil.cpu_percent()
    end_mem = psutil.virtual_memory().percent
    
    avg_cpu = (start_cpu + end_cpu) / 2
    avg_mem = (start_mem + end_mem) / 2
    
    logging.info(f"{exp_name}, {data_size}, Workers: {num_workers}, Time: {processing_time:.2f}s, "
                 f"Rows: {row_count}, Throughput: {throughput:.2f} rows/s, "
                 f"Driver CPU: {avg_cpu:.1f}%, Driver Memory: {avg_mem:.1f}%")
    
    spark.stop()

# Run all experiments
for exp_name, exp_config in experiments.items():
    for data_size, workers in exp_config.items():
        run_experiment(exp_name, data_size, workers)
