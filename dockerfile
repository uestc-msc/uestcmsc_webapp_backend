FROM python:3.8
WORKDIR /code
RUN apt-get update \
    && apt-get install -y python3-dev default-libmysqlclient-dev build-essential
RUN pip3 config set global.index-url http://pypi.doubanio.com/simple \
    && pip3 config set global.trusted-host pypi.doubanio.com \
    && pip3 install pipenv
COPY Pipfile Pipfile.lock .
RUN set -ex && pipenv install --system --deploy
COPY . .
RUN python3 manage.py collectstatic --noinput --clear --no-post-process
EXPOSE 8000
CMD ["gunicorn","-c", "uestcmsc_webapp_backend/gunicorn.conf.py","uestcmsc_webapp_backend.wsgi"]
