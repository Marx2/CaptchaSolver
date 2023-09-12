FROM python:3.10.13-slim-bullseye
WORKDIR /app
RUN apt update && apt install -y python3-opencv \
  && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*
COPY ./requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETVARIANT
RUN printf "I'm building for TARGETPLATFORM=${TARGETPLATFORM}" \
    && printf ", TARGETARCH=${TARGETARCH}" \
    && printf ", TARGETVARIANT=${TARGETVARIANT} \n" \
    && printf "With uname -s : " && uname -s \
    && printf "and  uname -m : " && uname -m
RUN if [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
      pip install --no-cache-dir tensorflow; \
    else \
      pip install --no-cache-dir --ignore-installed --upgrade https://tf.novaal.de/core2/tensorflow-2.8.0-cp310-cp310-linux_x86_64.whl; \
    fi
COPY app.py .
COPY background2.jpg .
COPY helpers.py .
COPY self_captcha_model2.hdf5 .
COPY self_model_labels2.dat .
EXPOSE 8000
ENV FLASK_APP=app.py
ENV FLASK_ENV="docker"
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
CMD ["gunicorn",  "--bind", "0.0.0.0:8000", "app:app"]