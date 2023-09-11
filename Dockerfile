FROM python:3.10.13-slim-bullseye
WORKDIR /app
RUN apt update && apt install -y python3-opencv \
  && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*
COPY ./requirements.txt /app
RUN pip install -r requirements.txt
COPY app.py .
COPY background2.jpg .
COPY helpers.py .
COPY self_captcha_model2.hdf5 .
COPY self_model_labels2.dat .
EXPOSE 8000
ENV FLASK_APP=app.py
ENV FLASK_ENV="docker"
CMD ["gunicorn",  "--bind", "0.0.0.0:8000", "app:app"]