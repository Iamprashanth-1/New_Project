FROM python:3.7-slim

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY src/app.py ./

# Command can be overwritten by providing a different command in the template directly.
