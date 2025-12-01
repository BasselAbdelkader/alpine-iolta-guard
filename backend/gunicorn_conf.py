# Gunicorn configuration file
bind = "0.0.0.0:8002"
workers = 4
timeout = 120
accesslog = "/app/logs/gunicorn-access.log"
errorlog = "/app/logs/gunicorn-error.log"
loglevel = "info"
