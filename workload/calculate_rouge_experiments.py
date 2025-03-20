import argparse
import time
import logging
import psutil  # For driver-side CPU/memory monitoring
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from rouge_score import rouge_scorer

# Set up logging
logging.basicConfig(filename='rouge_experiments.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

# Argument parsing
parser = argparse.ArgumentParser(description="Run ROUGE score calculation experiments")
parser.add_argument('--data_path', type=str, required=True,
                    help="HDFS path to input dataset (e.g., hdfs://192.168.2.23:9000/small_data/mini_data_20pct.json)")
parser.add_argument('--num_workers', type=int, required=True, choices=[1, 2, 3, 4],
                    help="Number of Spark workers (1-4)")
args = parser.parse_args()

# Initialize Spark session with dynamic worker configuration
spark = SparkSession.builder \
    .appName(f"ROUGE_Experiment_{args.num_workers}_workers") \
    .master("spark://192.168.2.23:7077") \
    .config("spark.executor.instances", args.num_workers) \
    .config("spark.executor.cores", 2) \
    .config("spark.executor.memory", "4g") \
    .getOrCreate()

# Start timing and resource monitoring
start_time = time.time()
start_cpu = psutil.cpu_percent(interval=None)  # Initial CPU usage
start_mem = psutil.virtual_memory().percent  # Initial memory usage

# Load the data from HDFS
df = spark.read.json(args.data_path)
row_count = df.count()  # Get total rows for throughput

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
end_cpu = psutil.cpu_percent(interval=None)  # Final CPU usage
end_mem = psutil.virtual_memory().percent  # Final memory usage

# Average CPU/memory usage on driver
avg_cpu = (start_cpu + end_cpu) / 2
avg_mem = (start_mem + end_mem) / 2

# Log basic metrics
logging.info(f"Dataset: {args.data_path}, Workers: {args.num_workers}, "
             f"Time: {processing_time:.2f}s, Rows: {row_count}, Throughput: {throughput:.2f} rows/s, "
             f"Driver CPU: {avg_cpu:.1f}%, Driver Memory: {avg_mem:.1f}%")

# Attempt to log executor metrics (requires Spark REST API or manual log parsing)
try:
    from pyspark import SparkContext
    sc = SparkContext.getOrCreate()
    status = sc.statusTracker().getJobInfo(sc.getJobIdsForGroup()[0])  # Get latest job info
    # This is approximate; Spark doesn't expose executor CPU/memory directly in Python API
    logging.info(f"Executor metrics not fully available via Python API; check Spark UI or logs")
except Exception as e:
    logging.warning(f"Failed to fetch executor metrics: {str(e)}")

# Stop Spark session
spark.stop()