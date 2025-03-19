age: ./configure_cluster.sh <role> <master_ip> <worker_ips>
# Example: ./configure_cluster.sh master 130.238.27.127 "130.238.27.86 130.238.27.161 130.238.27.56 130.238.27.193"
# Example: ./configure_cluster.sh worker 130.238.27.127

ROLE=$1
MASTER_IP=$2
WORKER_IPS=$3

# Source environment variables
source ~/.bashrc

# Ensure directories exist
sudo mkdir -p /usr/local/hadoop/etc/hadoop
sudo mkdir -p /usr/local/spark/conf
sudo chown -R ubuntu:ubuntu /usr/local/hadoop /usr/local/spark

if [ "$ROLE" == "master" ]; then
    echo "Configuring master node..."

    # Hadoop Configuration
    echo "<configuration>
        <property>
            <name>fs.defaultFS</name>
            <value>hdfs://$MASTER_IP:9000</value>
        </property>
    </configuration>" > /usr/local/hadoop/etc/hadoop/core-site.xml

    echo "<configuration>
        <property>
            <name>dfs.replication</name>
            <value>3</value>
        </property>
        <property>
            <name>dfs.namenode.name.dir</name>
            <value>/hadoop_data/namenode</value>
        </property>
        <property>
            <name>dfs.datanode.data.dir</name>
            <value>/hadoop_data/datanode</value>
        </property>
    </configuration>" > /usr/local/hadoop/etc/hadoop/hdfs-site.xml

    sudo mkdir -p /hadoop_data/namenode /hadoop_data/datanode
    sudo chown -R ubuntu:ubuntu /hadoop_data
    echo "$WORKER_IPS" | tr " " "\n" > /usr/local/hadoop/etc/hadoop/workers

    # Spark Configuration
    cp /usr/local/spark/conf/spark-env.sh.template /usr/local/spark/conf/spark-env.sh 2>/dev/null || touch /usr/local/spark/conf/spark-env.sh
    touch /usr/local/spark/conf/workers
    touch /usr/local/spark/conf/spark-defaults.conf
    echo "export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64" >> /usr/local/spark/conf/spark-env.sh
    echo "export HADOOP_CONF_DIR=/usr/local/hadoop/etc/hadoop" >> /usr/local/spark/conf/spark-env.sh
    echo "$WORKER_IPS" | tr " " "\n" > /usr/local/spark/conf/workers
    echo "spark.master spark://$MASTER_IP:7077" > /usr/local/spark/conf/spark-defaults.conf

    # Format HDFS (run once)
    /usr/local/hadoop/bin/hdfs namenode -format

    echo "Master configuration complete. Start services with:"
    echo "  /usr/local/hadoop/sbin/start-dfs.sh"
    echo "  /usr/local/spark/sbin/start-all.sh"

elif [ "$ROLE" == "worker" ]; then
    echo "Configuring worker node..."

    # Hadoop Configuration
    scp ubuntu@$MASTER_IP:/usr/local/hadoop/etc/hadoop/core-site.xml /usr/local/hadoop/etc/hadoop/
    scp ubuntu@$MASTER_IP:/usr/local/hadoop/etc/hadoop/hdfs-site.xml /usr/local/hadoop/etc/hadoop/
    sudo mkdir -p /hadoop_data/datanode
    sudo chown -R ubuntu:ubuntu /hadoop_data

    # Spark Configuration
    scp ubuntu@$MASTER_IP:/usr/local/spark/conf/spark-env.sh /usr/local/spark/conf/

    echo "Worker configuration complete."
else
    echo "Invalid role. Use 'master' or 'worker'."
    exit 1
fi
