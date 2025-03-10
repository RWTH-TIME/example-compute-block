from scystream.sdk.core import entrypoint
from typing import List

from crawling import crawling, save_and_upload
from analysis import word_frequency, generate_pdf
from scystream.sdk.env.settings import EnvSettings, OutputSettings, \
    FileSettings, InputSettings
from scystream.sdk.file_handling.s3_manager import S3Operations
from scystream.sdk.config import get_compute_block
from scystream.sdk.config.config_loader import generate_config_from_compute_block
from scystream.sdk.scheduler import Scheduler
from pathlib import Path
import os


class TextFileOutput(FileSettings, OutputSettings):
    __identifier__ = "test_file_containting_crawled_words"
    pass


class CrawlerEntrySettings(EnvSettings):
    URLS: List[str] = [
        "https://www.gutenberg.org/cache/epub/3300/pg3300.txt",
        "https://www.gutenberg.org/cache/epub/6435/pg6435.txt",
        "https://www.gutenberg.org/cache/epub/26163/pg26163.txt",
        "https://www.gutenberg.org/cache/epub/833/pg833.txt"
    ]

    txt_file_out: TextFileOutput


@entrypoint(CrawlerEntrySettings)
def crawl_urls(settings):
    text = crawling(settings.URLS)
    save_and_upload(text, s3_settings=settings.txt_file_out)


class TextFileInput(FileSettings, InputSettings):
    __identifier__ = "txt_input"
    pass


class MostCommonPDFOutput(FileSettings, OutputSettings):
    __identifier__ = "most_common"


class LeastCommonPDFOutput(FileSettings, OutputSettings):
    __identifier__ = "least_common"


class WordFrequencySettings(EnvSettings):
    USE_STOPWORDS: bool = True
    txt_file_input: TextFileInput

    pdf_most_common: MostCommonPDFOutput
    pdf_least_common: LeastCommonPDFOutput


def read_txt_to_variable(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


@entrypoint(WordFrequencySettings)
def gen_stats(settings):
    # Download File from input
    download_fn = "download.txt"

    s3_conn = S3Operations(settings.txt_file_input)
    s3_conn.download_file(
        bucket_name=settings.txt_file_input.BUCKET_NAME,
        s3_object_name=f"{
            settings.txt_file_input.FILE_PATH}/{settings.txt_file_input.FILE_NAME}.txt",
        local_file_path=download_fn
    )

    # Read File
    text = read_txt_to_variable(download_fn)

    # Make analysis
    stats = word_frequency(text, settings.USE_STOPWORDS)

    # Gen Files & Upload Output
    most_common_pdf_fn = settings.pdf_most_common.FILE_NAME
    least_common_pdf_fn = settings.pdf_least_common.FILE_NAME
    generate_pdf(stats[0], most_common_pdf_fn)
    generate_pdf(stats[1], least_common_pdf_fn, False)

    s3_conn.upload_file(
        path_to_file=most_common_pdf_fn,
        bucket_name=settings.pdf_most_common.BUCKET_NAME,
        target_name=f"{
            settings.pdf_most_common.FILE_PATH}/{settings.pdf_most_common.FILE_NAME}.pdf"
    )
    s3_conn.upload_file(
        path_to_file=least_common_pdf_fn,
        bucket_name=settings.pdf_least_common.BUCKET_NAME,
        target_name=f"{
            settings.pdf_least_common.FILE_PATH}/{settings.pdf_least_common.FILE_NAME}.pdf"
    )


"""
if __name__ == "__main__":
    compute_block = get_compute_block()
    generate_config_from_compute_block(compute_block, Path("gockel.yaml"))

    os.environ["test_file_containting_crawled_words_BUCKET_NAME"] = "run"
    os.environ["test_file_containting_crawled_words_FILE_NAME"] = "output"
    os.environ["test_file_containting_crawled_words_FILE_PATH"] = "/"
    os.environ["test_file_containting_crawled_words_S3_ACCESS_KEY"] = "minioadmin"
    os.environ["test_file_containting_crawled_words_S3_SECRET_KEY"] = "minioadmin"
    os.environ["test_file_containting_crawled_words_S3_HOST"] = "http://localhost"
    os.environ["test_file_containting_crawled_words_S3_PORT"] = "9000"

    os.environ["txt_input_BUCKET_NAME"] = "run"
    os.environ["txt_input_FILE_NAME"] = "output"
    os.environ["txt_input_FILE_PATH"] = "/"
    os.environ["txt_input_S3_ACCESS_KEY"] = "minioadmin"
    os.environ["txt_input_S3_SECRET_KEY"] = "minioadmin"
    os.environ["txt_input_S3_HOST"] = "http://localhost"
    os.environ["txt_input_S3_PORT"] = "9000"

    os.environ["least_common_BUCKET_NAME"] = "run"
    os.environ["least_common_FILE_NAME"] = "least_common"
    os.environ["least_common_FILE_PATH"] = "/"
    os.environ["least_common_S3_ACCESS_KEY"] = "minioadmin"
    os.environ["least_common_S3_SECRET_KEY"] = "minioadmin"
    os.environ["least_common_S3_HOST"] = "http://localhost"
    os.environ["least_common_S3_PORT"] = "9000"

    os.environ["most_common_BUCKET_NAME"] = "run"
    os.environ["most_common_FILE_NAME"] = "most_common"
    os.environ["most_common_FILE_PATH"] = "/"
    os.environ["most_common_S3_ACCESS_KEY"] = "minioadmin"
    os.environ["most_common_S3_SECRET_KEY"] = "minioadmin"
    os.environ["most_common_S3_HOST"] = "http://localhost"
    os.environ["most_common_S3_PORT"] = "9000"

    Scheduler.execute_function("crawl_urls")
    Scheduler.execute_function("gen_stats")
"""
