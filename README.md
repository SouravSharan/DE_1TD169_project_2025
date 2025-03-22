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

## Hardware:
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
