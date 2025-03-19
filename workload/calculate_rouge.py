from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StructType, StructField, StringType, FloatType
from rouge import Rouge
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Reddit ROUGE Score Calculation") \
    .master("spark://192.168.2.252:7077") \
    .config("spark.executor.memory", "2g") \
    .config("spark.executor.cores", "1") \
    .getOrCreate()

# Define ROUGE calculation function
def calculate_rouge(reference, hypothesis):
    try:
        if not reference or not hypothesis:
            logger.warning("Empty reference or hypothesis")
            return {"rouge-1": 0.0, "rouge-2": 0.0, "rouge-l": 0.0}
        rouge = Rouge()
        scores = rouge.get_scores(hypothesis, reference)[0]
        return {
            "rouge-1": scores["rouge-1"]["f"],
            "rouge-2": scores["rouge-2"]["f"],
            "rouge-l": scores["rouge-l"]["f"]
        }
    except Exception as e:
        logger.error(f"ROUGE calculation failed: {str(e)}")
        return {"rouge-1": 0.0, "rouge-2": 0.0, "rouge-l": 0.0}

# Register UDF
rouge_udf = udf(calculate_rouge, 
                StructType([
                    StructField("rouge-1", FloatType(), False),
                    StructField("rouge-2", FloatType(), False),
                    StructField("rouge-l", FloatType(), False)
                ]))

# Read JSONL file as text and parse
data_path = "hdfs://192.168.2.252:9000/reddit_data/mini_data_10.json"
try:
    # Read as text lines
    text_df = spark.read.text(data_path)
    # Parse each line as JSON
    parsed_df = text_df.rdd.map(lambda row: json.loads(row.value)).toDF()
    parsed_df.printSchema()  # Debug: Show schema
    parsed_df.show(5, truncate=False)  # Debug: Show sample data
except Exception as e:
    logger.error(f"Failed to read JSONL: {str(e)}")
    spark.stop()
    exit(1)

# Select body and summary, drop nulls
df_with_summary = parsed_df.select(
    "body",
    "summary"
).na.drop()

# Calculate ROUGE scores
rouge_df = df_with_summary.withColumn("rouge_scores", rouge_udf("body", "summary"))
result_df = rouge_df.select(
    "body",
    "summary",
    rouge_df.rouge_scores["rouge-1"].alias("rouge_1_f"),
    rouge_df.rouge_scores["rouge-2"].alias("rouge_2_f"),
    rouge_df.rouge_scores["rouge-l"].alias("rouge_l_f")
)

# Show results
result_df.show(truncate=False)

# Compute average scores
avg_scores = result_df.agg({
    "rouge_1_f": "avg",
    "rouge_2_f": "avg",
    "rouge_l_f": "avg"
}).collect()[0]

print(f"Average ROUGE-1 F-Score: {avg_scores['avg(rouge_1_f)']:.4f}")
print(f"Average ROUGE-2 F-Score: {avg_scores['avg(rouge_2_f)']:.4f}")
print(f"Average ROUGE-L F-Score: {avg_scores['avg(rouge_l_f)']:.4f}")

# Save results to HDFS
result_df.write.mode("overwrite").parquet("hdfs://192.168.2.252:9000/reddit_data/rouge_results")

# Stop Spark session
spark.stop()