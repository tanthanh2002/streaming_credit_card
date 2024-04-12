#read data from kafka topic credit_card

from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType, BooleanType
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, concat_ws, lit, expr
from datetime import datetime

appName = "Credit_card_streaming"
master = "spark://thanh-asus-tuf:7077"

spark = SparkSession.builder \
    .master(master) \
    .appName(appName) \
    .enableHiveSupport() \
    .getOrCreate()

# Define schema
schema = StructType([
    StructField("User", StringType(), True),
    StructField("Card", StringType(), True),
    StructField("Year", StringType(), True),
    StructField("Month", StringType(), True),
    StructField("Day", StringType(), True),
    StructField("Time", StringType(), True),
    StructField("Amount", StringType(), True),
    StructField("Use_Chip", StringType(), True),
    StructField("Merchant_Name", StringType(), True),
    StructField("Merchant_City", StringType(), True),
    StructField("Merchant_State", StringType(), True),
    StructField("Zip", StringType(), True),
    StructField("MCC", StringType(), True),
    StructField("Errors", StringType(), True),
    StructField("Is_Fraud", StringType(), True),
])

# Read data from Kafka topic with defined schema
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "127.0.0.1:9092") \
    .option("subscribe", "credit_card") \
    .option("startingOffsets", "earliest") \
    .load() \
    .select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

#transform data
df_transformed = df.withColumn("Transaction_Date", concat_ws("/", col("Day"), col("Month"), col("Year")))

df_transformed = df_transformed.withColumn("Time", concat_ws(":", col("Time"), lit("00")))

df_transformed = df_transformed.withColumn("Amount", expr("substring(Amount, 2)").cast("double")*24000)

df_transformed = df_transformed.filter(col("Is_Fraud") == "No")

# Display streaming data
query = df_transformed.writeStream \
    .outputMode("append") \
    .format("parquet") \
    .partitionBy("year","month") \
    .option("path", "hdfs://127.0.0.1:9000/user/thanh/credit_card")\
    .option("checkpointLocation", "hdfs://127.0.0.1:9000/user/thanh/checkpoints") \
    .start()

# Wait for the real-time processing to finish
query.awaitTermination()



#spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 read_data_from_kafka_topic.py
