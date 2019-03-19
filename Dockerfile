FROM python:3.6-alpine as base

FROM base as builder

RUN mkdir /install
WORKDIR /install

COPY requirements.txt /requirements.txt

RUN apk add --no-cache --virtual .build-deps gcc musl-dev
RUN pip install --install-option="--prefix=/install" -r /requirements.txt
RUN apk del .build-deps gcc musl-dev

FROM base

COPY --from=builder /install /usr/local
COPY . /src

WORKDIR /src

CMD ["python", "run.py"]