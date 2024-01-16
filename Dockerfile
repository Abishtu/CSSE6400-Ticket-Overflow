FROM ubuntu:latest

RUN apt-get update -y && \
    apt-get install -y python3 gunicorn python3-pip libpq-dev libcurl4-openssl-dev libssl-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install pipenv

WORKDIR /app

COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

COPY . .

RUN chmod +x bin/docker-entrypoint && chmod +x bin/hamilton

EXPOSE 6400

ENTRYPOINT ["/app/bin/docker-entrypoint"]
CMD ["serve"]
