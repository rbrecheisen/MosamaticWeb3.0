FROM python:3.9

RUN pip install --upgrade pip setuptools wheel && \
    pip install pynetdicom pydicom

COPY main.py /src/main.py

WORKDIR /src

CMD ["python", "main.py"]