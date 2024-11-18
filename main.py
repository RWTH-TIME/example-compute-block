from scystream.sdk.core import entrypoint
from scystream.sdk.config import SDKConfig
from scystream.sdk.database_handling.postgres_manager import PostgresConfig
from scystream.sdk.scheduler import Scheduler
from scystream.sdk.spark_manager import SparkManager

global_config = SDKConfig(
    app_name="test_app",
    cb_spark_master="spark://localhost:7077"
)


@entrypoint()
def test_entrypoint():
    spark = SparkManager()

    # I want to use a postgres db
    pg_conf = PostgresConfig(
        connection_name="first_pg_conn",
        pg_user="postgres",
        pg_pass="postgres",
        pg_host="localhost",
        pg_port=5432
    )
    db_conn = spark.setup_pg(pg_conf)

    # Sample DataFrame
    data = [("John", 30), ("Jane", 25), ("Jake", 35)]
    columns = ["name", "age"]

    df = spark.session.createDataFrame(data, columns)

    # Write the DataFrame to create a new table in PostgreSQL
    db_conn.write(df, table="person_table", mode="overwrite")

    print(db_conn)
    print("hello")


if __name__ == "__main__":
    Scheduler.execute_function("test_entrypoint")
