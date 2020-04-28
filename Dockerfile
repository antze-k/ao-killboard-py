ARG PYTHON_VERSION=3.6
FROM python:${PYTHON_VERSION}-alpine
COPY requirements.txt /root/requirements.txt
COPY src /root/src
COPY docker-entrypoint.sh /do
RUN apk add --no-cache build-base
RUN python -mpip install pip setuptools wheel --upgrade
RUN pip install -r /root/requirements.txt
RUN apk del --no-cache build-base
ENTRYPOINT ["/do"]
CMD ["run"]
