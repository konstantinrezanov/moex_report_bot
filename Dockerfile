# Use the official Python 3.10.11-bullseye base image
FROM python:3.9.16-slim-bullseye

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt ./

RUN apt-get update && apt-get install -y libatlas-base-dev

RUN  python -m pip --no-cache-dir install -r requirements.txt --extra-index-url https://www.piwheels.org/simple

COPY . .

CMD ["python", "src/main.py"]