from cassandra.cluster import Cluster
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, expr, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, FloatType
import logging
# import uuid

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_sparkconnection():
    spark = None
    spark = SparkSession.builder.appName("spark_datasteam")\
                                .config('spark.jars',".venv/lib/python3.11/site-packages/pyspark/jars/spark-cassandra-connector-assembly_2.12-3.5.1.jar,"
                                        ".venv/lib/python3.11/site-packages/pyspark/jars/spark-sql-kafka-0-10_2.12-3.5.3.jar,"
                                        ".venv/lib/python3.11/site-packages/pyspark/jars/kafka-clients-3.5.1.jar,"
                                        ".venv/lib/python3.11/site-packages/pyspark/jars/commons-pool2-2.12.0.jar,"
                                        ".venv/lib/python3.11/site-packages/pyspark/jars/spark-token-provider-kafka-0-10_2.12-3.5.3.jar") \
                                .config('spark.cassandra.connection.host', "localhost") \
                                .getOrCreate()
        
    spark.sparkContext.setLogLevel("Error")
    logging.info("Spark connection created successfully")

    return spark


def cassandra_connection():
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()

    print("Cassandra session created")
    return session


def create_keyspace(session):
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS spark_datastream
        With replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}
    """)

    print("Keyspace created")

def create_table(session):
    session.execute("""
        CREATE TABLE IF NOT EXISTS spark_datastream.weather (
            id UUID PRIMARY KEY,
            timestamp TIMESTAMP,
            country TEXT,
            coordinates_lat FLOAT,
            coordinates_lon FLOAT,
            weather_main TEXT,
            weather_type TEXT,
            temperature_main FLOAT,
            temperature_range_min FLOAT,
            temperature_range_max FLOAT,
            humidity FLOAT,
            pressure FLOAT,
            visibility FLOAT,
            wind_speed FLOAT,
            wind_deg FLOAT
            )
    """)
    print("Table created")




def kafka_connection(spark_connection):
    spark_df = None
    
    print("running kafka")
    spark_df = spark_connection.readStream \
                .format('kafka') \
                .option("failOnDataLoss","false") \
                .option('kafka.bootstrap.servers','127.0.0.1:9092') \
                .option('subscribe','weather_now') \
                .option('startingOffsets','earliest') \
                .load()

    query = spark_df \
                .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
                .writeStream \
                .outputMode("append") \
                .format("console") \
                .option("truncate", "false") \
                .start()
    

    print(spark_df)

    return spark_df

def create_selection_df(spark_df):
    schema = StructType([
        StructField("country", StringType(), False),
        StructField("coordinates_lon", FloatType(), False),
        StructField("coordinates_lat", FloatType(), False),
        StructField("weather_main", StringType(), False),
        StructField("weather_type", StringType(), False),
        StructField("temperature_main", FloatType(), False),
        StructField("temperature_range_min", FloatType(), False),
        StructField("temperature_range_max", FloatType(), False),
        StructField("humidity", FloatType(), False),
        StructField("pressure", FloatType(), False),
        StructField("visibility", FloatType(), False),
        StructField("wind_speed", FloatType(), False),
        StructField("wind_deg", FloatType(), False)
    ])

    sel = spark_df.selectExpr("CAST(value AS STRING)").select(from_json(col('value'), schema).alias('data')).select("data.*").withColumn("id", expr("uuid()")).withColumn("timestamp",current_timestamp())
    print(sel)

    return sel



if __name__ == "__main__":
    sparkconnection = create_sparkconnection()
    sparkconnection


    if sparkconnection is not None:
        df = kafka_connection(sparkconnection)
        selection_df = create_selection_df(df)
        cassandra_session = cassandra_connection()

        if cassandra_session is not None:
            create_keyspace(cassandra_session)
            create_table(cassandra_session)

            streaming = selection_df.writeStream.format("org.apache.spark.sql.cassandra") \
                        .option('checkpointLocation', '/tmp/checkpoint') \
                        .option('keyspace', 'spark_datastream') \
                        .option('table', 'weather')\
                        .start()
            
            streaming.awaitTermination()