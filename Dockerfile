FROM python:3.7

COPY ./* /tmp/app
WORKDIR /tmp/app
RUN pip install -r requirements.txt

RUN ["python3", "main.py"]
