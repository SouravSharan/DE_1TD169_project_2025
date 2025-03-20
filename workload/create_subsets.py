from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder.appName("Create Dataset Subsets") \
    .master("spark://192.168.2.23:7077") \
    .config("spark.executor.instances", 4) \
    .config("spark.executor.memory", "4g") \
    .getOrCreate()

# Full dataset path in HDFS
full_data_path = "hdfs://192.168.2.23:9000/data/corpus-webis-tldr-17_10pct.json"

# Read the full dataset
df = spark.read.json(full_data_path)

# Verify row count (optional)
total_rows = df.count()
print(f"Total rows in dataset: {total_rows}")

# Define subset percentages
subsets = {
    "10pct": 0.1,
    "20pct": 0.2,
    "50pct": 0.5,
    "100pct": 1
}

# Create and save each subset
for name, fraction in subsets.items():
    # Sample the dataset
    subset_df = df.sample(fraction=fraction, seed=42)  # Seed for reproducibility
    # Define output path
    output_path = f"hdfs://group27-v5-cluster-master:9000/data/corpus-webis-tldr-17_10pct_{name}.json"
    # Write subset to HDFS
    subset_df.write.mode("overwrite").json(output_path)
    print(f"Saved {name} subset to {output_path}")

# Stop Spark session
spark.stop()