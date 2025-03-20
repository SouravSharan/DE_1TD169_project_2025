from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from rouge_score import rouge_scorer

# Initialize Spark session
spark = SparkSession.builder \
    .appName("ROUGE Score Calculation") \
    .getOrCreate()

# Load the data from HDFS
df = spark.read.json("hdfs://group27-v5-cluster-master:9000/small_data/mini_data_10.json")

# Check the schema to verify the columns
df.printSchema()

# Show some example data
df.show(5)

# Initialize the ROUGE scorer
scorer = rouge_scorer.RougeScorer(
    ['rouge1', 'rouge2', 'rougeL'],  # List of metrics as first argument
    use_stemmer=True  # Optional: enables stemming for better scoring
)

# Define a function to calculate ROUGE score for each row
def calculate_rouge(summary, content):
    if not summary or not content:
        return 0.0, 0.0, 0.0  # Handle null/empty inputs
    scores = scorer.score(content, summary)
    return scores['rouge1'].fmeasure, scores['rouge2'].fmeasure, scores['rougeL'].fmeasure

# Register the UDF for PySpark
from pyspark.sql.functions import udf
from pyspark.sql.types import StructType, StructField, FloatType

# Define schema for ROUGE scores (rouge1, rouge2, rougeL)
rouge_schema = StructType([
    StructField('rouge1', FloatType(), True),
    StructField('rouge2', FloatType(), True),
    StructField('rougeL', FloatType(), True)
])

# Register the UDF
rouge_udf = udf(lambda summary, content: calculate_rouge(summary, content), rouge_schema)

# Apply the UDF to calculate ROUGE scores
df_with_rouge = df.withColumn("rouge_scores", rouge_udf(col('summary'), col('content')))

# Extract individual ROUGE scores
df_with_rouge = df_with_rouge.select(
    'author',
    'subreddit',
    'summary',
    'content',
    'rouge_scores.rouge1',
    'rouge_scores.rouge2',
    'rouge_scores.rougeL'
)

# Show results
df_with_rouge.show(10)

# Save the results to HDFS in the /outputs directory
df_with_rouge.write.mode("overwrite").json("hdfs://group27-v5-cluster-master:9000/outputs/rouge_results.json")

# Stop Spark session
spark.stop()