# DE_1TD169_project_2025
Data engineering I 1TD169 Project, 2025, Group 27







The Hadoop/Spark cluster is now setup. To get access, follow the guide below.

### 1. Setup local machine
Save the key posted in the WhatsApp group to a `.pem` file.
Create or modify the file ~/.ssh/config on your local (laptop) computer by adding a section like the one shown below:
Replace `/path/to/keyfile.pem` with your actual path.
```
Host 130.238.27.215
KexAlgorithms +diffie-hellman-group1-sha1
        User ubuntu
        # modify this to match the name of your key
        IdentityFile /path/to/keyfile.pem
        # Spark master web GUI
        LocalForward 8080 192.168.2.204:8080
        # HDFS namenode web gui
        LocalForward 9870 192.168.2.204:9870
        # Python notebook
        LocalForward 8888 localhost:8888
        # Spark applications
        LocalForward 4040 localhost:4040
        LocalForward 4041 localhost:4041
        LocalForward 4042 localhost:4042
        LocalForward 4043 localhost:4043
        LocalForward 4044 localhost:4044
        LocalForward 4045 localhost:4045
        LocalForward 4046 localhost:4046
        LocalForward 4047 localhost:4047
        LocalForward 4048 localhost:4048
        LocalForward 4049 localhost:4049
        LocalForward 4050 localhost:4050
        LocalForward 4051 localhost:4051
        LocalForward 4052 localhost:4052
        LocalForward 4053 localhost:4053
        LocalForward 4054 localhost:4054
        LocalForward 4055 localhost:4055
        LocalForward 4056 localhost:4056
        LocalForward 4057 localhost:4057
        LocalForward 4058 localhost:4058
        LocalForward 4059 localhost:4059
        LocalForward 4060 localhost:4060
```

Now you can ssh into our VM using
```
ssh 130.238.27.215
```
### 2. Hadoop
The NameNode is `192.168.2.204`. We currently have one DataNode. You should now be able to browse our HDFS on the Hadoop Web GUI at

[http://localhost:9870/explorer.html#/user/ubuntu/](http://localhost:9870/explorer.html#/user/ubuntu/)

In the folder `small_data` there are two subsets of the Reddit dataset, one containing 10 records and one with 10 000 records. These are ment for starting to experiment with before we scale up our solution.

### 3. Spark
The master node is `192.168.2.204`. We currently have one worker. You can reach the Spark Web UI at

[http://localhost:8080/](http://localhost:8080/)

When a Spark session is running on the cluster you can reach the application UI at

[http://localhost:4040/](http://localhost:4040/)


### 4. Jupyter Notebook
Start the jupyter server by running
```
jupyter server --port=8888 --no-browser --ip=0.0.0.0 --certfile ssl_cert/mycert.pem --keyfile=ssl_cert/mykey.key
```
You can reach the jupyter notebook from 

[https://localhost:8888/lab/tree/DE_1TD169_project_2025/data_analysis.ipynb](https://localhost:8888/lab/tree/DE_1TD169_project_2025/data_analysis.ipynb)

The password is  `group27password`.

The notebook loads one of the subsets from our HDFS and is ment as a starting point for further analysis.


