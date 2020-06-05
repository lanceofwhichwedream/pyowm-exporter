FROM python:3.8-buster

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY pyowm-exporter.py .

CMD ['python', "./pyowm-exporter.py"]