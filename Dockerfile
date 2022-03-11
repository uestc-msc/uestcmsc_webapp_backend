FROM python:3.8
WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip config set global.index-url http://pypi.doubanio.com/simple && \
    pip config set global.trusted-host pypi.doubanio.com && \
    pip install -r requirements.txt
COPY . .
RUN python3 manage.py makemigrations accounts activities activities_files activities_photos activities_link activities_comments cloud users --noinput && \
    python3 manage.py migrate --noinput && \
    python3 manage.py collectstatic --noinput --clear && \
    python manage.py createcachetable
EXPOSE 8000
CMD ["gunicorn", "-b", "127.0.0.1:8000", "--access-logfile", "-", "uestcmsc_webapp_backend.wsgi"]