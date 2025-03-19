#!/bin/bash

# Define new IPs and names
MASTER_INTERNAL_IP="192.168.2.252"
MASTER_NAME="group27-v3-master"
MASTER_FLOATING_IP="130.238.27.127"
WORKER_INTERNAL_IPS="192.168.2.241 192.168.2.88 192.168.2.74 192.168.2.167"
WORKER_NAMES="group27-v3-worker-1 group27-v3-worker-2 group27-v3-worker-3 group27-v3-worker-4"
WORKER_FLOATING_IPS="130.238.27.107 130.238.27.161 130.238.27.56 130.238.27.193"

# Update Hadoop on Master
echo "<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://${MASTER_INTERNAL_IP}:9000</value>
    </property>
</configuration>" > /usr/local/hadoop/etc/hadoop/core-site.xml
echo "$WORKER_INTERNAL_IPS" | tr " " "\n" > /usr/local/hadoop/etc/hadoop/workers

# Update Spark on Master
echo "spark.master spark://${MASTER_INTERNAL_IP}:7077" > /usr/local/spark/conf/spark-defaults.conf
echo "$WORKER_INTERNAL_IPS" | tr " " "\n" > /usr/local/spark/conf/workers

# Update /etc/hosts on Master
sudo sed -i "/group27_v/d" /etc/hosts  # Remove old entries
echo "$MASTER_INTERNAL_IP $MASTER_NAME" | sudo tee -a /etc/hosts
i=1
for ip in $WORKER_INTERNAL_IPS; do
    worker_name=$(echo $WORKER_NAMES | cut -d' ' -f$i)
    echo "$ip $worker_name" | sudo tee -a /etc/hosts
    ((i++))
done

# Propagate to Workers
i=1
for ext_ip in $WORKER_FLOATING_IPS; do
    worker_name=$(echo $WORKER_NAMES | cut -d' ' -f$i)
    echo "Updating $worker_name ($ext_ip)..."
    scp /usr/local/hadoop/etc/hadoop/core-site.xml ubuntu@$ext_ip:/usr/local/hadoop/etc/hadoop/
    scp /usr/local/hadoop/etc/hadoop/hdfs-site.xml ubuntu@$ext_ip:/usr/local/hadoop/etc/hadoop/
    scp /usr/local/spark/conf/spark-env.sh ubuntu@$ext_ip:/usr/local/spark/conf/
    ssh ubuntu@$ext_ip "sudo sed -i '/group27_v/d' /etc/hosts"  # Remove old entries
    ssh ubuntu@$ext_ip "echo '$MASTER_INTERNAL_IP $MASTER_NAME' | sudo tee -a /etc/hosts"
    j=1
    for w_ip in $WORKER_INTERNAL_IPS; do
        w_name=$(echo $WORKER_NAMES | cut -d' ' -f$j)
        ssh ubuntu@$ext_ip "echo '$w_ip $w_name' | sudo tee -a /etc/hosts"
        ((j++))
    done
    ((i++))
done

# Restart services
echo "Restarting HDFS and Spark..."
/usr/local/hadoop/sbin/stop-dfs.sh
/usr/local/spark/sbin/stop-all.sh
/usr/local/hadoop/sbin/start-dfs.sh
/usr/local/spark/sbin/start-all.sh

echo "Cluster updated. Verify with:"
echo "  /usr/local/hadoop/bin/hdfs dfs -ls /"
echo "  Check Spark UI: http://${MASTER_INTERNAL_IP}:8080"
