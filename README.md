# DE_1TD169_project_2025
Data engineering I 1TD169 Project, 2025, Group 27

# Spark and Hadoop Scalability Experiments
This repository contains scripts and tools for conducting scalability experiments using Apache Spark on a standalone cluster. The project focuses on processing large datasets (e.g TLDR summaries) to benchmark Spark’s performance under varying worker counts, data sizes, and resource configurations. Experiments measure runtime, throughput, CPU/memory usage, and scalability, with results logged for analysis.

## Project Structure
```
.
├── configure_dataset/         # Scripts for dataset preparation
│   ├── create_subset.py      # Creates a single subset from a local file
│   └── create_subsets_on_hdfs.py  # Creates multiple subsets on HDFS
├── logs/                     # Log files from experiments
│   ├── experiment_submission_.log  # Submission logs
├── README.md                 # This file
├── scalability_experiments/  # Bash scripts for running experiments
│   ├── experiment_1.sh       # Exp 1: Varying workers with data size
│   ├── experiment_2_3.sh     # Exp 2 & 3: Fixed workers, varying data
│   ├── experiment_4.sh       # Exp 4: Custom configuration
│   └── experiment_5.sh       # Exp 5: Final experiment
├── scripts/                  # Core Python scripts and notebooks
│   ├── calculate_rouge.py    # ROUGE score calculation workload
│   ├── data_analysis.ipynb   # Jupyter notebook for data analysis
│   ├── format_outputs.py     # Formats experiment outputs
│   ├── workload.py           # workload script
│   └── workload_with_rest_api.py  # Workload with Spark REST API
└── setup/                    # Cluster setup scripts
├── configure_cluster.sh  # Configures Spark cluster
```

## Features
- **Scalability Testing**: Experiments vary dataset sizes (e.g., 10%, 20%, 50%, 100%) and worker counts (1-4) to assess Spark performance.
- **Workloads**: Includes ROUGE score calculation (for text summarization).
- **Resource Monitoring**: Tracks driver CPU/memory usage with `psutil` and attempts executor metrics via Spark REST API.
- **Automation**: Bash scripts automate experiment execution and log results in a structured format.


## Prerequisites
- **Software**:
  - Apache Spark (tested with 3.x)
  - Python 3.x
  - Hadoop
- **Python Packages**:
  ```bash
  pip install pyspark psutil rouge-score requests pandas

## Hardware
- Cluster with 1 master (e.g., 80 GB storage) and 4 workers (e.g., 20 GB each)
- Ubuntu OS


## Setup
1. **Clone the Repository**:
   ```bash
   git clone git@github.com:SouravSharan/DE_1TD169_project_2025.git
   cd DE_1TD169_project_2025.
   ```

2. **Configure Cluster**:
   - Run setup scripts on each node:
     ```bash
     ./setup/setup_vm.sh  # On master and workers
     ```
   - Update cluster config:
     ```bash
     ./setup/configure_cluster.sh
     ./setup/update_hosts.sh
     ```

3. **Start Spark Cluster**:
   ```bash
   $SPARK_HOME/sbin/start-master.sh  # On master
   $SPARK_HOME/sbin/start-worker.sh spark://master-ip:7077  # On each worker
   ```
4. Upload data on HDFS
## Usage
1. **Prepare Dataset**:
   - Use `data_analysis.ipynb` for data analysis.
   - For HDFS:
     ```bash
     python configure_dataset/create_subsets_on_hdfs.py
     ```
     
3. **Run Experiments**:
   - Example: Experiment 1 (varying workers):
     ```bash
     ./scalability_experiments/experiment_5.sh
     ```
   - Check logs in `logs/` for results.

4. **Analyze Results**:
   - View logs (e.g., `logs/rouge_experiments.log`):
     ```
     Data: corpus-webis-tldr-17_10pct, Workers: 4, Cores: 2, Time: 25.30s, Rows: 16845943, Throughput: 665846.76 rows/s, Driver CPU: 35.2%, Driver Memory: 40.1%
     ```

### Results

| Timestamp            | Data                               | Data Size | Workers | Cores | Time (s) | Rows    | Throughput (rows/s) | Driver CPU (%) | Driver Memory (%) |
|----------------------|----------------------------------|-----------|---------|-------|---------|---------|----------------------|---------------|------------------|
| 2025-03-21 03:56:41 | corpus-webis-tldr-17_10pct_5pct  | 5%        | 1       | 2     | 39.77   | 19242   | 483.83               | 1.8           | 27.9             |
| 2025-03-21 04:19:33 | corpus-webis-tldr-17_10pct_5pct  | 5%        | 2       | 2     | 41.25   | 19242   | 466.48               | 1.9           | 28               |
| 2025-03-21 03:33:53 | corpus-webis-tldr-17_10pct_5pct  | 5%        | 4       | 1     | 50.1    | 19242   | 384.08               | 0.5           | 27.4             |
| 2025-03-21 01:50:40 | corpus-webis-tldr-17_10pct_5pct  | 5%        | 1       | 1     | 50.42   | 19242   | 381.6                | 3.1           | 27.9             |
| 2025-03-21 02:25:04 | corpus-webis-tldr-17_10pct_5pct  | 5%        | 2       | 1     | 50.99   | 19242   | 377.38               | 2.4           | 27.8             |
| 2025-03-21 02:59:35 | corpus-webis-tldr-17_10pct_5pct  | 5%        | 3       | 1     | 54.67   | 19242   | 351.95               | 2.8           | 27.6             |
| 2025-03-21 03:55:30 | corpus-webis-tldr-17_10pct_20pct | 20%       | 1       | 2     | 114     | 76952   | 675.01               | 1.6           | 27.6             |
| 2025-03-21 04:18:21 | corpus-webis-tldr-17_10pct_20pct | 20%       | 2       | 2     | 122.53  | 76952   | 628                  | 1.1           | 27.8             |
| 2025-03-22 00:49:30 | corpus-webis-tldr-17_10pct_60pct | 60%       | 4       | 4     | 150.74  | 231388  | 1535                 | 0.006         | 0.285            |
| 2025-03-22 00:46:41 | corpus-webis-tldr-17_10pct_60pct | 60%       | 3       | 4     | 150.99  | 231388  | 1532.48              | 0.014         | 0.283            |
| 2025-03-22 00:43:53 | corpus-webis-tldr-17_10pct_60pct | 60%       | 2       | 4     | 151.62  | 231388  | 1526.1               | 0.004         | 0.282            |
| 2025-03-22 00:41:03 | corpus-webis-tldr-17_10pct_60pct | 60%       | 1       | 4     | 152.86  | 231388  | 1513.75              | 0.009         | 0.286            |
| 2025-03-22 00:29:25 | corpus-webis-tldr-17_10pct_60pct | 60%       | 1       | 3     | 154.98  | 231388  | 1493.02              | 0.004         | 0.283            |
| 2025-03-22 00:38:12 | corpus-webis-tldr-17_10pct_60pct | 60%       | 4       | 3     | 155.94  | 231388  | 1483.79              | 0.007         | 0.281            |
| 2025-03-22 00:32:22 | corpus-webis-tldr-17_10pct_60pct | 60%       | 2       | 3     | 158.56  | 231388  | 1459.29              | 0.059         | 0.287            |
| 2025-03-22 00:35:18 | corpus-webis-tldr-17_10pct_60pct | 60%       | 3       | 3     | 158.83  | 231388  | 1456.81              | 0.006         | 0.282            |

*Table truncated for brevity.*


