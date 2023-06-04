# Use the official Python 3.10.11-bullseye base image
FROM python:3.10.11-slim-bullseye

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt ./

RUN apt install build-dep python3-lxml

RUN pip install --no-cache-dir --upgrade pip \
    && pip --no-cache-dir install -r requirements.txt

COPY . .

CMD ["python", "src/main.py"]