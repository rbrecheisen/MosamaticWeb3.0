FROM tensorflow/tensorflow:2.3.0-gpu

COPY src/mosamatic3 /src
COPY requirements.txt /requirements.txt
COPY docker-entrypoint.sh /docker-entrypoint.sh
COPY nvidia-public-key.txt /nvidia-public-key.txt

RUN apt-key add /nvidia-public-key.txt &&
    apt-get update -y &&
    apt-get install -y vim libpq-dev pkg-config cmake openssl wget git vim &&
    apt-get install -y libgl1-mesa-glx libxrender1 &&
    apt-get install -y libffi-dev &&
    apt-get install -y pigz dcm2niix &&
    pip install --upgrade pip setuptools wheel &&
    pip install -r /requirements.txt --verbose &&
    pip install uwsgi gunicorn &&
    mkdir -p /data/static &&
    mkdir -p /data/datasets &&
    mkdir -p /data/uploads/{0..9} && chmod 777 -R /data/uploads

WORKDIR /src

EXPOSE 8001

RUN apt-get autoremove -y &&
    apt-get clean &&
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD ["/docker-entrypoint.sh"]
