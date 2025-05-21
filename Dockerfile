FROM python:3.13-slim-bullseye AS dev
COPY . /workspaces/gufo_thor
WORKDIR /workspaces/gufo_thor
RUN \
    set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends git\
    && pip install --upgrade pip\
    && pip install --upgrade build\
    && pip install -e .[deps,test,lint,docs,ipython]