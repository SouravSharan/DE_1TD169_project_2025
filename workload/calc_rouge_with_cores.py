import argparse
import time
import logging
import psutil
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf
from pyspark.sql.types import StructType, StructField, FloatType
from rouge_score import rouge_scorer

# Logging setup
logging.basicConfig(filename='rouge_experiment_final_run.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

def parse_args():
    parser = argparse.ArgumentParser(description="Calculate ROUGE scores with Spark.")
    parser.add_argument('--num-workers', type=int, required=True, help="Number of Spark executor instances (workers)")
    parser.add_argument('--cores', type=int, required=True, help="Number of CPU cores per executor")
    parser.add_argument('--data-url', type=str, required=True, help="HDFS URL to the input JSON data")
    return parser.parse_args()

def calculate_rouge(summary, content):
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    if not summary or not content:
        return 0.0, 0.0, 0.0
    scores = scorer.score(content, summary)
    return scores['rouge1'].fmeasure, scores['rouge2'].fmeasure, scores['rougeL'].fmeasure

def run_experiment(num_workers, cores, data_url):
    # Extract a simple name from the data URL for output naming
    data_name = data_url.split('/')[-1].replace('.json', '')
    
    # Initialize Spark session
    spark = SparkSession.builder \
        .appName(f"ROUGE_{data_name}_{num_workers}w_{cores}c") \
        .master("spark://192.168.2.23:7077") \
        .config("spark.executor.instances", num_workers) \
        .config("spark.executor.cores", cores) \
        .config("spark.executor.memory", "4g") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()
    
    start_time = time.time()
    start_cpu = psutil.cpu_percent(interval=1)  # More accurate CPU measurement
    start_mem = psutil.virtual_memory().percent
    
    # Read data from the provided URL
    df = spark.read.json(data_url)
    row_count = df.count()
    
    # Define ROUGE UDF
    rouge_schema = StructType([
        StructField('rouge1', FloatType(), True),
        StructField('rouge2', FloatType(), True),
        StructField('rougeL', FloatType(), True)
    ])
    rouge_udf = udf(lambda summary, content: calculate_rouge(summary, content), rouge_schema)
    
    # Calculate ROUGE scores
    df_with_rouge = df.withColumn("rouge_scores", rouge_udf(col('summary'), col('content')))
    df_with_rouge = df_with_rouge.select(
        'author', 'subreddit', 'summary', 'content',
        'rouge_scores.rouge1', 'rouge_scores.rouge2', 'rouge_scores.rougeL'
    )
    
    # Define output path based on input parameters
    output_path = f"hdfs://192.168.2.23:9000/outputs_exp4/rouge_{data_name}_{num_workers}w_{cores}c.json"
    df_with_rouge.write.mode("overwrite").json(output_path)
    
    # Measure performance
    end_time = time.time()
    processing_time = end_time - start_time
    throughput = row_count / processing_time if processing_time > 0 else 0
    end_cpu = psutil.cpu_percent(interval=1)
    end_mem = psutil.virtual_memory().percent
    
    avg_cpu = (start_cpu + end_cpu) / 2
    avg_mem = (start_mem + end_mem) / 2
    
    # Log results
    logging.info(f"Data: {data_name}, Workers: {num_workers}, Cores: {cores}, "
                 f"Time: {processing_time:.2f}s, Rows: {row_count}, Throughput: {throughput:.2f} rows/s, "
                 f"Driver CPU: {avg_cpu:.1f}%, Driver Memory: {avg_mem:.1f}%")
    
    spark.stop()

if __name__ == "__main__":
    args = parse_args()
    run_experiment(args.num_workers, args.cores, args.data_url)
