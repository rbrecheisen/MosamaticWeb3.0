FROM tensorflow/tensorflow:2.15.0-gpu

COPY nvidia-public-key.txt /nvidia-public-key.txt

RUN apt-key add /nvidia-public-key.txt
RUN apt-get update -y && \
    apt-get install -y vim libpq-dev pkg-config cmake openssl wget git dos2unix && \
    apt-get install -y libgl1-mesa-glx libxrender1 && \
    apt-get install -y libffi-dev && \
    apt-get install -y pigz dcm2niix && \
    mkdir -p /data/static && \
    mkdir -p /data/datasets && \
    mkdir -p /data/uploads/{0..9} && chmod 777 -R /data/uploads

# Run these steps separately, otherwise the large RUN will execute always
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip setuptools wheel && pip install -r /requirements.txt --verbose

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN dos2unix /docker-entrypoint.sh

COPY src/mosamatic3 /src

WORKDIR /src

RUN apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD ["/docker-entrypoint.sh"]