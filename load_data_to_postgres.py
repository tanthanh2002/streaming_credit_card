from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import findspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import to_csv
from sqlalchemy import create_engine


findspark.init()
db_user = 'postgres'
db_password = '1111'
db_host = 'localhost'
db_port = '5432'
db_name = 'postgres'
table_name = 'credit_card_transactions'
mode = "overwrite"
url = f"jdbc:postgresql://{db_host}:{db_port}/{db_name}"
properties = {"user": db_user,"password": db_password,"driver": "org.postgresql.Driver"}


def load_data_to_db(**kwargs):
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    year = 2002
    month = 10
    if month is None and year is None:
        hdfs_path = "hdfs://127.0.0.1:9000/user/thanh/credit_card"
    else:
        hdfs_path = "hdfs://127.0.0.1:9000/user/thanh/credit_card/Year={}/Month={}/*".format(year, month)
    # Tạo một SparkSession
    spark = SparkSession.builder \
        .master("local") \
        .appName("Read and Convert Parquet to To PostgreSQL") \
        .getOrCreate()

    # Kết nối với cluster Hadoop
    spark.conf.set("fs.defaultFS", hdfs_path)

    # Đọc dữ liệu từ các file parquet
    df = spark.read.parquet(hdfs_path)

    df.write.jdbc(url=url, table=table_name, mode=mode, properties=properties)
    
  
    
load_data_to_db(year=None, month=None)

# Define the DAG
dag = DAG(
    'Load_data_to_postgres',
    description='Example DAG',
    schedule_interval='0 0 L * *', 
    start_date=datetime(2024, 1, 1),
    catchup=False
)

# Define the task
task = PythonOperator(
    task_id='load_data',
    python_callable=load_data_to_db,
    dag=dag
)

