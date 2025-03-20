import argparse
import time
import logging
import psutil
import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from rouge_score import rouge_scorer

# Set up logging with tab-separated format
logging.basicConfig(filename='rouge_experiments.log', level=logging.INFO,
                    format='%(message)s')  # Custom format without timestamp

# Argument parsing
parser = argparse.ArgumentParser(description="Run ROUGE score calculation experiments")
parser.add_argument('--data_path', type=str, required=True,
                    help="HDFS path to input dataset")
parser.add_argument('--num_workers', type=int, required=True, choices=[1, 2, 3, 4],
                    help="Number of Spark workers (1-4)")
args = parser.parse_args()

# Initialize Spark session
spark = SparkSession.builder \
    .appName(f"ROUGE_Experiment_{args.num_workers}_workers") \
    .master("spark://192.168.2.23:7077") \
    .config("spark.executor.instances", args.num_workers) \
    .config("spark.executor.cores", 2) \
    .config("spark.executor.memory", "4g") \
    .getOrCreate()

# Start timing and resource monitoring
start_time = time.time()
start_cpu = psutil.cpu_percent(interval=None)
start_mem = psutil.virtual_memory().percent

# Load the data from HDFS
df = spark.read.json(args.data_path)
row_count = df.count()

# ROUGE calculation
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

# Save results
output_path = f"hdfs://192.168.2.23:9000/outputs/rouge_results_{args.num_workers}w_{args.data_path.split('/')[-1]}"
df_with_rouge.write.mode("overwrite").json(output_path)

# End timing and resource monitoring
end_time = time.time()
processing_time = end_time - start_time
throughput = row_count / processing_time
end_cpu = psutil.cpu_percent(interval=None)
end_mem = psutil.virtual_memory().percent

# Average driver CPU/memory
avg_cpu = (start_cpu + end_cpu) / 2
avg_mem = (start_mem + end_mem) / 2

# Log metrics in tab-separated format
logging.info(f"{args.data_path}\t{args.num_workers}\t{processing_time:.2f}\t{row_count}\t{throughput:.2f}\t{avg_cpu:.1f}\t{avg_mem:.1f}")

# Fetch executor metrics via REST API (optional)
try:
    response = requests.get("http://192.168.2.23:8080/api/v1/applications")
    if response.status_code == 200:
        app_id = response.json()[0]["id"]
        executor_info = requests.get(f"http://192.168.2.23:8080/api/v1/applications/{app_id}/executors")
        if executor_info.status_code == 200:
            for executor in executor_info.json():
                if executor["id"] != "driver":
                    mem_used_mb = executor["memoryUsed"] / 1024 / 1024
                    logging.info(f"Executor {executor['id']} Memory Used: {mem_used_mb:.1f} MB")
        else:
            logging.warning("Failed to fetch executor info from REST API")
    else:
        logging.warning("Failed to fetch application ID from REACTOR API")
except Exception as e:
    logging.warning(f"REST API error: {str(e)}")

# Stop Spark session
spark.stop()