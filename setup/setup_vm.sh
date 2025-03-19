#!/bin/bash

# Usage: ./setup_vm.sh <role> <master_ip> <worker_ips>
# Example: ./setup_vm.sh master 192.168.1.101 "192.168.1.102 192.168.1.103"
# Example: ./setup_vm.sh worker 192.168.1.101

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
wget -q https://downloads.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz
tar -xzf hadoop-3.3.6.tar.gz
sudo mv hadoop-3.3.6 /usr/local/hadoop
echo "export HADOOP_HOME=/usr/local/hadoop" >> ~/.bashrc
echo "export PATH=\$PATH:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin" >> ~/.bashrc

echo "Installing Spark..."
wget -q https://downloads.apache.org/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz
tar -xzf spark-3.5.0-bin-hadoop3.tgz
sudo mv spark-3.5.0-bin-hadoop3 /usr/local/spark
echo "export SPARK_HOME=/usr/local/spark" >> ~/.bashrc
echo "export PATH=\$PATH:\$SPARK_HOME/bin" >> ~/.bashrc
source ~/.bashrc

if [ "$ROLE" == "master" ]; then
    # Master-specific setup
    echo "Setting up master node..."

    # SSH setup
    ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
    for worker_ip in $WORKER_IPS; do
        ssh-copy-id -i ~/.ssh/id_rsa.pub ubuntu@$worker_ip
    done

    # Hadoop config
    echo "<configuration><property><name>fs.defaultFS</name><value>hdfs://$MASTER_IP:9000</value></property></configuration>" > /usr/local/hadoop/etc/hadoop/core-site.xml
    echo "<configuration><property><name>dfs.replication</name><value>3</value></property><property><name>dfs.namenode.name.dir</name><value>/hadoop_data/namenode</value></property><property><name>dfs.datanode.data.dir</name><value>/hadoop_data/datanode</value></property></configuration>" > /usr/local/hadoop/etc/hadoop/hdfs-site.xml
    sudo mkdir -p /hadoop_data/namenode /hadoop_data/datanode
    sudo chown -R ubuntu:ubuntu /hadoop_data
    echo "$WORKER_IPS" | tr " " "\n" > /usr/local/hadoop/etc/hadoop/workers

    # Spark config
    echo "export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64" > /usr/local/spark/conf/spark-env.sh
    echo "export HADOOP_CONF_DIR=/usr/local/hadoop/etc/hadoop" >> /usr/local/spark/conf/spark-env.sh
    echo "$WORKER_IPS" | tr " " "\n" > /usr/local/spark/conf/workers
    echo "spark.master spark://$MASTER_IP:7077" > /usr/local/spark/conf/spark-defaults.conf

    # Format HDFS (run once)
    hdfs namenode -format
elif [ "$ROLE" == "worker" ]; then
    # Worker-specific setup
    echo "Setting up worker node..."

    # Hadoop config
    scp ubuntu@$MASTER_IP:/usr/local/hadoop/etc/hadoop/core-site.xml /usr/local/hadoop/etc/hadoop/
    scp ubuntu@$MASTER_IP:/usr/local/hadoop/etc/hadoop/hdfs-site.xml /usr/local/hadoop/etc/hadoop/
    sudo mkdir -p /hadoop_data/datanode
    sudo chown -R ubuntu:ubuntu /hadoop_data

    # Spark config
    scp ubuntu@$MASTER_IP:/usr/local/spark/conf/spark-env.sh /usr/local/spark/conf/
fi

echo "Setup complete for $ROLE node!"
