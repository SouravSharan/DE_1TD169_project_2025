#!/bin/bash

# Usage: ./setup_vm.sh <role> <master_ip> <worker_ips>
# Example: ./setup_vm.sh master 130.238.27.127 "130.238.27.86 130.238.27.161"
# Example: ./setup_vm.sh worker 130.238.27.127

ROLE=$1
MASTER_IP=$2
WORKER_IPS=$3

# Common Setup
echo "Updating system and installing prerequisites..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y openjdk-11-jdk python3 python3-pip openssh-server
sudo systemctl enable ssh && sudo systemctl start ssh
echo "export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64" >> ~/.bashrc

echo "Installing Hadoop..."
wget -q https://downloads.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz || { echo "Hadoop download failed"; exit 1; }
tar -xzf hadoop-3.3.6.tar.gz
sudo rm -rf /usr/local/hadoop  # Clean up old install
sudo mv hadoop-3.3.6 /usr/local/hadoop
echo "export HADOOP_HOME=/usr/local/hadoop" >> ~/.bashrc
echo "export PATH=\$PATH:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin" >> ~/.bashrc

echo "Installing Spark..."
wget -q https://downloads.apache.org/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz || { echo "Spark download failed"; exit 1; }
tar -xzf spark-3.5.0-bin-hadoop3.tgz
sudo rm -rf /usr/local/spark  # Clean up old install
sudo mv spark-3.5.0-bin-hadoop3 /usr/local/spark
echo "export SPARK_HOME=/usr/local/spark" >> ~/.bashrc
echo "export PATH=\$PATH:\$SPARK_HOME/bin" >> ~/.bashrc

# Source environment variables
source ~/.bashrc

if [ "$ROLE" == "master" ]; then
    #echo "Setting up master node..."
    #ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa -q
    #echo "Please manually copy ~/.ssh/id_rsa.pub to workers' ~/.ssh/authorized_keys"

    # Hadoop config
    echo "<configuration><property><name>fs.defaultFS</name><value>hdfs://$MASTER_IP:9000</value></property></configuration>" > /usr/local/hadoop/etc/hadoop/core-site.xml
    echo "<configuration><property><name>dfs.replication</name><value>3</value></property><property><name>dfs.namenode.name.dir</name><value>/hadoop_data/namenode</value></property><property><name>dfs.datanode.data.dir</name><value>/hadoop_data/datanode</value></property></configuration>" > /usr/local/hadoop/etc/hadoop/hdfs-site.xml
    sudo mkdir -p /hadoop_data/namenode /hadoop_data/datanode
    sudo chown -R ubuntu:ubuntu /hadoop_data
    echo "$WORKER_IPS" | tr " " "\n" > /usr/local/hadoop/etc/hadoop/workers

    # Spark config
    mkdir -p /usr/local/spark/conf
    cp /usr/local/spark/conf/spark-env.sh.template /usr/local/spark/conf/spark-env.sh || touch /usr/local/spark/conf/spark-env.sh
    touch /usr/local/spark/conf/workers
    touch /usr/local/spark/conf/spark-defaults.conf
    echo "export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64" >> /usr/local/spark/conf/spark-env.sh
    echo "export HADOOP_CONF_DIR=/usr/local/hadoop/etc/hadoop" >> /usr/local/spark/conf/spark-env.sh
    echo "$WORKER_IPS" | tr " " "\n" > /usr/local/spark/conf/workers
    echo "spark.master spark://$MASTER_IP:7077" > /usr/local/spark/conf/spark-defaults.conf

    # Format HDFS
    /usr/local/hadoop/bin/hdfs namenode -format
elif [ "$ROLE" == "worker" ]; then
    echo "Setting up worker node..."
    scp ubuntu@$MASTER_IP:/usr/local/hadoop/etc/hadoop/core-site.xml /usr/local/hadoop/etc/hadoop/
    scp ubuntu@$MASTER_IP:/usr/local/hadoop/etc/hadoop/hdfs-site.xml /usr/local/hadoop/etc/hadoop/
    sudo mkdir -p /hadoop_data/datanode
    sudo chown -R ubuntu:ubuntu /hadoop_data
    scp ubuntu@$MASTER_IP:/usr/local/spark/conf/spark-env.sh /usr/local/spark/conf/
fi

echo "Setup complete for $ROLE node!"
