from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Tạo Spark Session
appName = "Credit_card_batch"
master = "spark://thanh-asus-tuf:7077"
spark = SparkSession.builder \
    .master(master) \
    .appName(appName) \
    .enableHiveSupport() \
    .getOrCreate()

# Đọc dữ liệu từ tệp Parquet trên HDFS
hdfs_path = "hdfs://127.0.0.1:9000/user/thanh/credit_card"



# Thiết lập kết nối JDBC cho PostgreSQL
jdbc_url = "jdbc:postgresql://localhost:5432/CreditCard"
properties = {
    "user": "postgres",
    "password": "1111",
    "driver": "org.postgresql.Driver"
}

# Ghi dữ liệu vào bảng PostgreSQL
table_name = "report"

def load_to_database(hdfs_path,properties, table_name, jdbc_url,year = None, month = None):
    condition = (col("year") == year) if year is not None else (col("year") != "-1") 
    condition = condition & (col("month") == month) if month is not None else condition
    df = spark.read.parquet(hdfs_path).filter(condition)
    df.show()

    df.printSchema()
    # df.write \
    # .mode("append") \
    # .jdbc(url=jdbc_url, table=table_name, properties=properties)

load_to_database(hdfs_path,properties,table_name,jdbc_url)