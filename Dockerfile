FROM python:3.11


COPY requirements.txt app/requirements.txt



WORKDIR /app
RUN pip install -r requirements.txt
COPY . /app

ENV PYTHONPATH /app

CMD ["python", "./src/main.py"]