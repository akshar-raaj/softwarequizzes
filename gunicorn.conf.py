accesslog = "/tmp/softwarequizzes-access.txt"
errorlog = "/tmp/softwarequizzes-error.txt"
capture_output = True
daemon = True
pidfile = "/tmp/softwarequizzes.pid"
bind = "127.0.0.1:8002"
worker_class = "uvicorn.workers.UvicornWorker"
