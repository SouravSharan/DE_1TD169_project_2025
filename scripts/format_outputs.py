from pyspark.sql import SparkSession
import subprocess

# Initialize Spark session
spark = SparkSession.builder \
    .appName("RemoveFieldsAndSaveToHDFSWithStructure") \
    .getOrCreate()

# Define base input and output paths
base_input_path = "hdfs://192.168.2.23:9000/outputs/"
base_output_path = "hdfs://192.168.2.23:9000/outputs_formatted/"

# Use HDFS command to list directories matching the pattern
hdfs_cmd = "hdfs dfs -ls hdfs://192.168.2.23:9000/outputs/ | grep rouge_results"
result = subprocess.check_output(hdfs_cmd, shell=True).decode("utf-8")

# Extract folder names from the HDFS listing
folders = [line.split()[-1].split('/')[-1] for line in result.strip().split('\n') if line]

# Process each folder
for folder in folders:
    # Define input and output paths for this specific folder
    input_path = f"{base_input_path}{folder}/*"
    output_path = f"{base_output_path}{folder}"

    # Read JSON Lines files from the current folder
    df = spark.read.json(input_path)

    # Drop 'summary' and 'content' fields
    filtered_df = df.drop("summary", "content")

    # Write the filtered DataFrame to the corresponding output folder
    filtered_df.write.mode("overwrite").json(output_path)

# Stop the Spark session
spark.stop()