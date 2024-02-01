"""
Tracks the config i.e the things that vary between deploys.

See https://12factor.net/config
This drives strict separation of config from code.

In a parallel universe, this module could have been named 'config' instead of 'constants'.

Conventions:
1. Keep the environment variables separated from hard-coded constants.
2. Keep the config names in alphabetical order for easy scanning by engineers.
"""
import os
from dotenv import load_dotenv


load_dotenv()


# Read from environment
DATABASE_CONNECTION_STRING = os.environ['DATABASE_CONNECTION_STRING']
DATABASE_REPLICA_CONNECTION_STRING = os.environ['DATABASE_REPLICA_CONNECTION_STRING']
ES_ENDPOINT = os.environ.get('ES_ENDPOINT')
ES_AUTH_TOKEN = os.environ.get('ES_AUTH_TOKEN')
REDIS_HOST = os.environ['REDIS_HOST']
REDIS_PORT = os.environ['REDIS_PORT']
SECRET_KEY = os.environ["SECRET_KEY"]

# Hard-coded constants
ALGORITHM = "HS256"
ADMIN_EMAIL = "raaj.akshar@gmail.com"
DEFAULT_SUBDOMAINS = ['python', 'javascript', 'sql']
PLACEHOLDER_USER_EMAIL = "placeholder@softwarequizzes.com"
