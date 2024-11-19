from scystream.sdk.core import entrypoint
from scystream.sdk.config import SDKConfig
from scystream.sdk.database_handling.postgres_manager import PostgresConfig
from scystream.sdk.scheduler import Scheduler
from scystream.sdk.spark_manager import SparkManager
from pyspark.sql import Row

global_config = SDKConfig(
    app_name="test_app",
    # TODO: Only when run in docker container
    cb_spark_master="spark://spark-master:7077"
)


@entrypoint()
def test_entrypoint():
    manager = SparkManager()

    pg_conf = PostgresConfig(
        pg_user="postgres",
        pg_pass="postgres",
        pg_host="postgres",
        pg_port=5432
    )
    db_conn = manager.setup_pg(pg_conf)

    table_name = "your_table_name"
    studentDF = manager.session.createDataFrame({
        Row(id=1, name="test", marks=75),
        Row(id=2, name="test", marks=88),
    })

    db_conn.write(database_name="postgres", dataframe=studentDF,
                  table=table_name, mode="overwrite")

    df = db_conn.read(database_name="postgres", table=table_name)
    print(df.show())

    df_two = db_conn.read(
        database_name="postgres",
        query=f"SELECT id FROM {table_name} WHERE id > 1"
    )

    print(df_two.show())


if __name__ == "__main__":
    Scheduler.execute_function("test_entrypoint")
