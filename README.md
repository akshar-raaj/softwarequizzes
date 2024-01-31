## About

This repository powers backend of softwarequizes.com.

The APIs are hosted at http://api.softwarequizzes.com/docs.

## Features

The application allows the following operations:
- Create question
- Create question choices
- List questions
- List question choices
- User registration
- User login
- Answer a question
- Track user's progress
- Generate report

## Tech Stack

Programming Language: Python
API Framework: FastAPI
Transactional Database: MySQL
Cache and session storage: Redis
Search Engine: Elasticsearch
SQL Toolkit: SQLAlchemy


### Python

Allows rapid application development because of it's dynamically typed nature.

### FastAPI

A modern and high performance web framework geared towards building APIs.

It uses Python's async/await feature i.e cooperative multitasking and event loop making its speed at par with Node and Go.

And it exploits Python's type hints and stands on shoulders of giants like Pydantic. This gives several features out of the box, making it a modern framework.

### MySQL

A relational database providing strong ACID guarantees.

## Deployment Stack
Web Server: Gunicorn
Reverse Proxy and Load Balancer: Nginx

## Setup

Install the requirements

    pip install -r requirements.txt

Copy the contents of `.env.example` to `.env`.

Ensure you provide appropriate values for the following in `.env`
- DATABASE_CONNECTION_STRING
- SECRET_KEY
- REDIS_HOST
- REDIS_PORT

## Server

The server can be started using the following command:

    uvicorn main:app --reload --port 8000

This would start the server. Server would accept connections on port 8000.

You should be able to get response using following command:

    curl -X GET http://localhost:8000/

## API Documentation

API Documentation can be accessed at:

    http://localhost:8000/docs

## Production deployment

Invoke the following command

    /home/ubuntu/.pyenv/versions/softwarequizzes/bin/gunicorn main:app --config ./gunicorn.conf.py

This assumes that Gunicorn executable is at `/home/ubuntu/.pyenv/versions/softwarequizzes/bin/gunicorn`.

See gunicorn.conf.py to see the process id file path and access log file path.

This will start a Gunicorn server at port 8002.

It's highly likely that the server is serving multiple domains and hence Nginx is being used as a reverse proxy.

Nginx configuration file would look like:

    server {
            listen 80;
            listen [::]:80;

            server_name api.softwarequizzes.com;

            location / {
                proxy_pass http://127.0.0.1:8001;
            }
    }

## Production documentation

This application is deployed at api.softwarequizzes.com.

## Architecture

![softwarequizzes](https://github.com/akshar-raaj/softwarequizzes/assets/889120/d08399b8-8c3f-4cff-9c8c-cae80d06b75d)


## Database Replication

Our transactional database is MySQL.

We have configured replication for reliability and high availability.

The following link mentions the steps needed to configure replication.

https://dev.mysql.com/doc/refman/8.0/en/replication-configuration.html

### Source database server

We created a snapshot on the source database. The relevant dump file is dbdump.db

### Replica database server

Install MySQL server

https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-20-04

Change data directory of MySQL to point to EBS

https://www.digitalocean.com/community/tutorials/how-to-move-a-mysql-data-directory-to-a-new-location-on-ubuntu-20-04

Steps:

    sudo rm -rf /data/mysql/
    sudo rsync -av /var/lib/mysql /data/
    sudo systemctl start mysql.service
    sudo mysql < dbdump.db

Issue the following commands:

    mysql> set global server_id = 2;
    mysql> change replication source to
    -> source_host = '<ip>',
    -> source_user = 'repl',
    -> source_password = '<pass>',
    -> source_log_file = 'binlog.000038',
    -> source_log_pos = 893,
    -> GET_MASTER_PUBLIC_KEY=1;

Issue start replica command

    mysql> start replica;

The replica should catch-up with the master soon.