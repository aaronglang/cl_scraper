FROM python:3.7

COPY . /tmp/scraper/
WORKDIR /tmp/scraper
RUN pip install -r requirements.txt

CMD ["python3", "main.py"]