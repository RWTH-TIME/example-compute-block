from typing import List
import requests
from bs4 import BeautifulSoup

from scystream.sdk.env.settings import EnvSettings, OutputSettings, \
    FileSettings
from scystream.sdk.file_handling.s3_manager import S3Operations


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


def crawling(urls: str):
    texts = []
    try:
        for url in urls:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text(separator=" ")

            texts.append(text.strip())
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

    return ' '.join(texts)


def save_and_upload(text_str: str, s3_settings: FileSettings):
    output = "output.txt"
    with open(output, "w", encoding="utf-8") as file:
        file.write(text_str)

    s3_conn = S3Operations(s3_settings)
    s3_conn.upload_file(
        path_to_file=output,
        bucket_name=s3_settings.BUCKET_NAME,
        target_name=f"{s3_settings.FILE_PATH}/{s3_settings.FILE_NAME}.txt"
    )


if __name__ == "__main__":
    test = CrawlerEntrySettings(
        txt_file_out=TextFileOutput(
            S3_HOST="http://localhost",
            S3_PORT="9000",
            S3_ACCESS_KEY="minioadmin",
            S3_SECRET_KEY="minioadmin",
            BUCKET_NAME="jibbia",
            FILE_PATH="outputOfFile",
            FILE_NAME="fileoutput.txt"
        )
    )

    text = crawling(test.URLS)
    save_and_upload(text, s3_settings=test.txt_file_out)
