# Use the official Python 3.10.11-bullseye base image
FROM python:3.9-slim-bullseye

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt ./

RUN  pip --no-cache-dir install -r requirements.txt --extra-index-url https://www.piwheels.org/simple

COPY . .

CMD ["python", "src/main.py"]