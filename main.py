from scystream.sdk.core import entrypoint
from scystream.sdk.config import SDKConfig
from scystream.sdk.database_handling.postgres_manager import PostgresConfig
from scystream.sdk.file_handling.s3_manager import S3Config, S3Operations
from scystream.sdk.scheduler import Scheduler
from scystream.sdk.spark_manager import SparkManager
from scystream.sdk.env.settings import EnvSettings, \
    OutputSettings
from pyspark.sql import Row


class GlobalENVs(EnvSettings):
    """
    Global ENVs, shall not be set by scheduler.
    """
    DEVELOPMENT: bool = True


GLOBAL_ENVS = GlobalENVs.get_settings()

print(GLOBAL_ENVS.DEVELOPMENT)

global_config = SDKConfig(
    app_name="test_app",
    cb_spark_master=(
        "local[*]" if GLOBAL_ENVS.DEVELOPMENT else "spark://spark-master:7077"
    )
)


class TestEntrypointDBOutput(OutputSettings):
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "postgres"
    PG_PORT: int = 5432
    TABLE_NAME: str = "your_table_name"
    DB_NAME: str = "postgres"


class TestEntrypointSettings(EnvSettings):
    db_output: TestEntrypointDBOutput


@entrypoint(TestEntrypointSettings)
def test_entrypoint(settings):
    manager = SparkManager()

    pg_conf = PostgresConfig(
        pg_user=settings.db_output.POSTGRES_USER,
        pg_pass=settings.db_output.POSTGRES_PASSWORD,
        pg_host=(
            "localhost"
            if GLOBAL_ENVS.DEVELOPMENT else settings.db_output.POSTGRES_HOST
        ),
        pg_port=settings.db_output.PG_PORT
    )
    print(pg_conf.pg_user)

    db_conn = manager.setup_pg(pg_conf)

    table_name = settings.db_output.TABLE_NAME
    studentDF = manager.session.createDataFrame({
        Row(id=1, name="test", marks=75),
        Row(id=2, name="test", marks=88),
    })

    db_conn.write(database_name=settings.db_output.DB_NAME,
                  dataframe=studentDF,
                  table=table_name, mode="overwrite")

    # Read from just created db #
    df = db_conn.read(database_name=settings.db_output.DB_NAME,
                      table=table_name)
    print(df.show())

    df_two = db_conn.read(
        database_name=settings.db_output.DB_NAME,
        query=f"SELECT id FROM {table_name} WHERE id > 1"
    )

    print(df_two.show())


class TestFileEntrypointOutput(OutputSettings):
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_HOST: str = "http://minio"
    S3_PORT: int = 9000
    TARGET_FILE_NAME: str = "target.txt"


class TestFileEntrypoint(EnvSettings):
    minio_output: TestFileEntrypointOutput


@entrypoint(TestFileEntrypoint)
def test_file(settings):
    s3_conf = S3Config(
        access_key=settings.minio_output.S3_ACCESS_KEY,
        secret_key=settings.minio_output.S3_SECRET_KEY,
        endpoint=(
            "http://localhost"
            if GLOBAL_ENVS.DEVELOPMENT else settings.minio_output.S3_HOST
        ),
        port=settings.minio_output.S3_PORT
    )

    file_handling = S3Operations(s3_conf)
    file_handling.upload_file(
        path_to_file="test.txt",
        bucket_name="gockel",
        target_name=settings.minio_output.TARGET_FILE_NAME)

    # Download the just uploaded file again #
    print("DOWNLOADING")
    file_handling.download_file(
        bucket_name="gockel",
        s3_object_name="target.txt",
        local_file_path="download.txt"
    )


# if __name__ == "__main__":
#    Scheduler.execute_function("test_entrypoint")
#    Scheduler.execute_function("test_file")
