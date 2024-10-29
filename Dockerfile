FROM python:3.11
ENV PYTHONUNBUFFERED=1
WORKDIR /chessmatch

COPY ./requirements.txt /chessmatch/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /chessmatch/requirements.txt