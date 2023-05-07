FROM python:3.8-bullseye

WORKDIR /data/python

COPY . .

RUN pip install --no-cache-dir -r requirements.txt && python --version

CMD ["python", "main.py"]