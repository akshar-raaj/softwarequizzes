FROM python:3.10

WORKDIR /srv

ADD ./requirements.txt /srv/requirements.txt

RUN pip install -r requirements.txt

ADD . /srv

#CMD ["gunicorn", "main:app", "--config", "./gunicorn.conf.py"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
