# https://docs.gunicorn.org/en/stable/settings.html#settings
bind = "127.0.0.1:8000"
workers = 2
threads = 3
accesslog = "-"
access_log_format = r'%({X-Real-IP}i)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
