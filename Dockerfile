FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV DEBUG False
ENV ALLOWED_HOSTS "*"

RUN mkdir /usr/src/app
WORKDIR /usr/src/app/

RUN pip install --upgrade pip

COPY requirements.txt /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app/

RUN sed -i "s/DEBUG = .*/DEBUG = $DEBUG/" /usr/src/app/core/settings.py && \
    sed -i "s/ALLOWED_HOSTS = \[\]/ALLOWED_HOSTS = \['$ALLOWED_HOSTS'\]/g" /usr/src/app/core/settings.py

RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

EXPOSE 8000
