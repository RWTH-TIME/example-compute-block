FROM python:3.12

ENV PYTHONUNBUFFERED=1

# Install Java for Spark 
RUN apt-get update && \
    apt-get install -y default-jdk && \
    apt-get clean

WORKDIR /app

COPY requirements.txt /app

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app


# CMD sh -c "python -c 'import main; from scystream.sdk.scheduler import Scheduler; Scheduler.execute_function(\"test_file\")'"

# Cmd that will be overwritten by Airflow
CMD ["sh", "-c","echo Container is ready for the Scheduler.exectue_function call."]
