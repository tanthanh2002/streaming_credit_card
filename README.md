# Streaming Creadit Card Processing
## Introduction
This project aims to simulate a data pipeline for processing streaming data using Apache Kafka, Apache Spark, Hadoop, and Apache Airflow. The pipeline reads data from a CSV file, sends it through Kafka for streaming, processes it with Spark, and stores it into Hadoop as a data lake partitioned by year and month. Additionally, at the end of each month, the pipeline extracts data from the data lake and loads it into PostgreSQL as a data warehouse using Apache Airflow.

## Technicals in use
- Apache Spark
- Apache Kafka
- Hadoop
- Apache Airflow
- PostgreSQL
## Architecture
<image src="./diagram.png"></image>
## Setup (in Ubuntu)
### Apache Kafka
--- 
- version: 3.6.0
- OS: Ubuntu 22.04

#### Các bước
- Bước 1: Tải [kafka_2.13-3.6.0.tgz](https://kafka.apache.org/downloads)

```bash
$ wget https://downloads.apache.org/kafka/3.6.0/kafka_2.13-3.6.0.tgz
```

- Bước 2: Giải nén

```bash
$ tar -xzf path/to/kafka_2.13-3.6.0.tgz
```

- Bước 3: Move vào nơi lưu trữ mong muốn

```bash
# lưu ở user thanh
$ sudo mv path/to/kafka_2.13-3.6.0 /home/thanh/kafka 
```

- Bước 4: config kafka

```bash
$ nano ~/kafka/config/server.properties
```

```bash
# thay đổi log dir từ mặc định là log.dirs=/tmp/kafka-logs sang như sau để thông tin dữ liệu không bị mất vì lưu ở tmp
log.dirs=/home/thanh/kafka/logs
```

- Bước 5: set up biến môi trường

```bash
$ nano ~/.bashrc
export PATH=$PATH:/opt/kafka/bin
```

```bash
$ source ~/.bashrc
```

- Bước 6: tạo systemd file để start zookeeper và kafka 
<p align="center">/etc/systemd/system/zookeeper.service</p>

```
[Unit]
Description=Zookeeper Service
After=network.target

[Service]
ExecStart=/home/thanh/kafka/bin/zookeeper-server-start.sh /home/thanh/kafka/con>
ExecStop=/home/thanh/kafka/bin/zookeeper-server-stop.sh
User=thanh
Restart=always

[Install]
WantedBy=multi-user.target

```

```bash
$ sudo systemctl enable zookeeper
$ sudo systemctl start zookeeper
```
<p align="center">/etc/systemd/system/kafka.service</p>

```
[Unit]
Description=Kafka Service
After=zookeeper.service

[Service]
ExecStart=/home/thanh/kafka/bin/kafka-server-start.sh /home/thanh/kafka/config/>
ExecStop=/home/thanh/kafka/bin/kafka-server-stop.sh
User=thanh
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
$ sudo systemctl enable kafka
$ sudo systemctl start kafka
```


### Apache Spark
---
- version: 3.5.0
- os: Ubuntu 22.04

#### Các bước

- Bước 1: tải spark

```bash
$ wget https://www.apache.org/dyn/closer.lua/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz
```

- Bước 2: giải nén và di chuyển vào nơi lưu trữ

```bash
$ tar -xzf spark-3.5.0-bin-hadoop3.tgz
$ mv spark-3.5.0-bin-hadoop3 spark
```

- Bước 3: set up biến môi trường
```bash
$ nano ~/.bashrc
# Add below lines at the end of the .bashrc file.
export SPARK_HOME=/home/thanh/spark
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
export PYSPARK_PYTHON=/usr/bin/python3
```

```bash
$ source ~/.bashrc
```

- Bước 4: Kiểm tra

```bash
# dùng lệnh sau để dùng spark shell với scala
$ spark-shell
```

```bash
# kết quả
Spark context Web UI available at http://192.168.191.73:4041
Spark context available as 'sc' (master = local[*], app id = local-1706279744256).
Spark session available as 'spark'.
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /___/ .__/\_,_/_/ /_/\_\   version 3.5.0
      /_/
         
Using Scala version 2.12.18 (OpenJDK 64-Bit Server VM, Java 21.0.1)
Type in expressions to have them evaluated.
Type :help for more information.

scala> 
```

- Bước 5: viết file spark-start.sh và spark-stop.sh 
<p align="center">spark-start.sh</p>

```bash
start-master.sh
sleep 3
start-worker.sh spark://thanh-asus-tuf:7077 --port 8001
sleep 3
start-worker.sh spark://thanh-asus-tuf:7077 --port 8002
```
<p align="center">spark-stop.sh</p>

```bash
stop-worker.sh
sleep 3
stop-master.sh
```

```bash
#start and stop
$ ~/spark-start.sh
$ ~/spark-stop.sh
```

Truy cập [http://localhost:8080](http://localhost:8080)
### Apache Hadoop
---
- Version: 3.3.6
- OS: Ubuntu 22.04

#### Các bước

- Bước 1: Tải hadoop

```bash
$ wget https://dlcdn.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz
```

- Bước 2: Giải nén và di chuyển vào nơi lưu trữ

```bash
$ tar xzf hadoop-3.3.6.tar.gz
$ mv hadoop-3.3.6 /home/thanh/hadoop
```

- Bước 3: set up biến môi trường

```bash
$ nano ~/.bashr

#thêm các dòng sau
export HADOOP_HOME=/home/thanh/hadoop
export HADOOP_INSTALL=$HADOOP_HOME
export HADOOP_MAPRED_HOME=$HADOOP_HOME
export HADOOP_COMMON_HOME=$HADOOP_HOME
export HADOOP_HDFS_HOME=$HADOOP_HOME
export YARN_HOME=$HADOOP_HOME
export HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
export PATH=$PATH:$HADOOP_HOME/sbin:$HADOOP_HOME/bin
export HADOOP_OPTS="-Djava.library.path=$HADOOP_HOME/lib/native"
```

- Bước 4: edit hadoop-env.sh File

```bash
$ sudo nano $HADOOP_HOME/etc/hadoop/hadoop-env.sh
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
```

- Bước 5:  Edit core-site.xml File

```bash
$ sudo nano $HADOOP_HOME/etc/hadoop/core-site.xml

# nội dung
<configuration>
<property>
  <name>hadoop.tmp.dir</name>
  <value>/home/thanh/tmpdata</value>
</property>
<property>
  <name>fs.default.name</name>
  <value>hdfs://127.0.0.1:9000</value>
</property>
</configuration>
```

- Bước 6: Edit hdfs-site.xml File

```bash
$ sudo nano $HADOOP_HOME/etc/hadoop/hdfs-site.xml

# nội dung
<configuration>
<property>
  <name>dfs.data.dir</name>
  <value>/home/thanh/dfsdata/namenode</value>
</property>
<property>
  <name>dfs.data.dir</name>
  <value>/home/thanh/dfsdata/datanode</value>
</property>
<property>
  <name>dfs.replication</name>
  <value>1</value>
</property>
</configuration>
```

- Bước 7: Edit mapred-site.xml File

```bash
$ sudo nano $HADOOP_HOME/etc/hadoop/mapred-site.xml

# nội dung
<configuration> 
<property> 
  <name>mapreduce.framework.name</name> 
  <value>yarn</value> 
</property> 
</configuration>
```

- Bước 8: Edit yarn-site.xml File

```bash
$ sudo nano $HADOOP_HOME/etc/hadoop/yarn-site.xml

# nội dung

<configuration>
<property>
  <name>yarn.nodemanager.aux-services</name>
  <value>mapreduce_shuffle</value>
</property>
<property>
  <name>yarn.nodemanager.aux-services.mapreduce.shuffle.class</name>
  <value>org.apache.hadoop.mapred.ShuffleHandler</value>
</property>
<property>
  <name>yarn.resourcemanager.hostname</name>
  <value>127.0.0.1</value>
</property>
<property>
  <name>yarn.acl.enable</name>
  <value>0</value>
</property>
<property>
  <name>yarn.nodemanager.env-whitelist</name>   
  <value>JAVA_HOME,HADOOP_COMMON_HOME,HADOOP_HDFS_HOME,HADOOP_CONF_DIR,CLASSPATH_PERPEND_DISTCACHE,HADOOP_YARN_HOME,HADOOP_MAPRED_HOME</value>
</property>
</configuration>
```

- Bước 9: fomat namenode

```bash
$ hdfs namenode -format
```

- Bước 10: viết file hadoop-start.sh và hadoop-stop.sh

```bash
# hadoop-start.sh
start-dfs.sh
sleep 5
start-yarn.sh
sleep 5
```

```bash
# hadoop-stop.sh
stop-yarn.sh
sleep 5
stop-dfs.sh
```

- Bước 10: start và truy cập

```bash
$ ~/hadoop-start.sh
```

Truy cập [http://localhost:9870](http://localhost:9870)

### Apache Superset

- Step 1: Install below list of packages

```bash
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev python3-pip libsasl2-dev libldap2-dev default-libmysqlclient-dev

sudo apt-get install python3-setuptools

pip3 install --upgrade pip

# Make sure we have the latest version of pip and setuptools:

pip install --upgrade setuptools pip
```


- Step 2: Create Python Virtual Environment to install Apache Superset on this
```bash
python -m venv supersetvenv

Activate Python Virtual Environment "supersetvenv"

source supersetvenv/bin/activate

pip install Pillow
```


- Step 3: Installing and Initializing Superset

Command to install apache-superset:
```bash
pip install apache-superset

export FLASK_APP=superset
```

Generate secret key for superset
```bash
openssl rand -base64 42
export SUPERSET_SECRET_KEY=SP8lhgc2rAYjDnCWVirc0jwHDQc0d0rP97X9qArNgMG4zAq/pQ8UlCS0
```

Command to initialize the database:
```bash
superset db upgrade
```

Step 4: Run the below commands to complete the installation

Create an admin user in your metadata database (use `admin` as username to be able to load the examples)
```bash
superset fab create-admin
```

 Load some data to play with
 ```bash
 superset load_examples
```

Create default roles and permissions
```bash
superset init
```


To start a development web server on port 8099, use -p to bind to another port

```bash
superset run -p 8099 --with-threads --reload --debugger
```

- Step 5: Open below url in the browser

http://localhost:8099

### Airflow

```bash
airflow webserver --port 8083

airflow scheduler
```
