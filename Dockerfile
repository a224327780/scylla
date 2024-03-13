FROM ghcr.io/a224327780/python

WORKDIR /data/python/scylla

COPY . .

RUN pip install --no-cache-dir -r requirements.txt && python --version

CMD ["python", "main.py"]